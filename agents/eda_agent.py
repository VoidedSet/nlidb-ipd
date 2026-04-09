import re

import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from pydantic import BaseModel, Field
from llm_setup import get_llm
from db_connection import get_db


class EDAPlan(BaseModel):
    thought_process: str = Field(description="Reasoning about the data and approach")
    code: str = Field(description="The executable Python code.")

class EDAAgent:
    def __init__(self):
        self.db = get_db()
        self.planner = get_llm(role="planner") 
        self.coder = get_llm(role="coder")     

    def get_schema(self):
        return self.db.get_table_info()

    def generate_plan_and_code(self, question: str, retry_context: str = ""):
        schema = self.get_schema()
        
        # --- 1. THE PLANNER (DeepSeek) ---
        planner_system = """
        Technical lead directing data engineer.
        Given database schema, write CONCISE 3-4 step instruction set to answer user question.
        
        CRITICAL RULES:
        1. Answer ONLY exact user question. No generic profiling/broad EDA.
        2. If user asks "what is the data about" or "tell me about the data" - analyze key tables and relationships to explain business domain.
        3. List EXACT table names and column names to use (from schema provided).
        4. NEVER assume columns exist everywhere - use only columns actually in schema.
        5. Specify exact output: "dataframe with X columns" or "matplotlib bar chart" etc.

        Keep under 100 words. Don't write code. Be specific about table/column names.
        """
        
        planner_prompt = ChatPromptTemplate.from_messages([
            ("system", planner_system),
            ("human", "User Question: {question}")
        ])

        print("      [EDA] Generating Plan (DeepSeek)...")
        plan_chain = planner_prompt | self.planner | StrOutputParser()
        thought_process = plan_chain.invoke({"schema": schema, "question": question})

        # --- 2. THE CODER (Qwen/Llama) ---
        coder_system = """
        Expert Python developer. Write executable code for provided analysis plan.
        
        CRITICAL RULES:
        1. Database: `engine = create_engine('mysql+mysqlconnector://root:@localhost:3306/prototype_testing')`
        2. NEVER assume columns exist in all tables. Only use columns mentioned in schema.
        3. If unsure about column names, query information_schema or use DESCRIBE.
        4. Use try-except for all database queries - handle errors gracefully.
        5. For data loading: `df = pd.read_sql("SELECT ...", engine)`
        6. Create visualizations carefully - check data exists before plotting.
        
        REQUIRED IMPORTS (always include):
        import pandas as pd
        import matplotlib.pyplot as plt
        from sqlalchemy import create_engine

        OUTPUTS:
        - ALWAYS assign main result/dataframe to `final_result` (never None)
        - If plotting: create figure, assign to `final_plot = plt.gcf()` then `plt.close()`
        - If no plot needed, don't create final_plot variable
        
        RETURN: Only valid Python code wrapped in ```python ... ``` blocks.
        """
        
        if retry_context:
            coder_system += f"\n\nPREVIOUS ERROR (FIX THIS):\nError: {retry_context}\n\nCommon fixes:\n- Import create_engine from sqlalchemy\n- Always assign something to final_result (never None)\n- Don't set final_plot = None if no plot needed\n- Check column names exist before using them\n- Use try-except for all database queries"

        coder_prompt = ChatPromptTemplate.from_messages([
            ("system", coder_system),
            ("human", "PLAN:\n{plan}\n\nWrite the code.")
        ])
        raw_code = code_chain.invoke({"plan": thought_process})
        
        # --- SMARTER CODE EXTRACTION ---
        # 1. Remove <think> blocks completely
        clean_code = re.sub(r'<think>.*?</think>', '', raw_code, flags=re.DOTALL)
        
        # 2. Extract strictly from the python markdown block if it exists
        match = re.search(r'```python\n(.*?)\n```', clean_code, re.DOTALL)
        if match:
            clean_code = match.group(1).strip()
        else:
            # Fallback cleanup just in case it forgot the markdown formatting
            clean_code = clean_code.replace("```python", "").replace("```", "").strip()

        return {
            "thought_process": thought_process,
            "code": clean_code
        }

    def synthesize_answer(self, question, steps, final_result):
        """
        Consumes the logs and result to create the final text response.
        """
        result_summary = str(final_result)
        if isinstance(final_result, pd.DataFrame):
            result_summary = f"DataFrame with columns: {list(final_result.columns)}. Preview: {final_result.head().to_string()}"

        # 1. SYSTEM: Persona (Updated to remove Yes-Man behavior)
        system_prompt = """
        You are a Senior Data Analyst acting as the interface for a BI tool.
        Your task is to provide a clear, rigorous, natural language conclusion based on the provided technical logs and results.
        
        CRITICAL INSTRUCTIONS:
        - Be objective and analytically rigorous.
        - Do NOT act like a "yes man". If the data contradicts the user's assumptions or if their premise is statistically flawed, you MUST explicitly point it out.
        - Provide warnings if the data quality is poor, if the sample size is too small, or if the requested analysis might lead to misleading conclusions.
        - Base your answers purely on the data provided in the result.
        """
        
        # 2. HUMAN: The Data
        human_message = """
        USER QUESTION: {question}
        
        TECHNICAL EXECUTION LOGS:
        {logs}
        
        FINAL RESULT/DATA:
        {result}
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_message)
        ])
        
        chain = prompt | self.planner | StrOutputParser()
        return chain.invoke({"question": question, "logs": str(steps), "result": result_summary})

    def run(self, question: str):
        steps = [] 
        max_retries = 3
        
        for attempt in range(max_retries):
            step_record = {
                "attempt": attempt + 1,
                "thought": "Planning logic...",
                "code": "",
                "error": None,
                "output": None
            }
            
            try:
                # 1. Plan
                prev_err = steps[-1]['error'] if steps else ""
                plan_data = self.generate_plan_and_code(question, prev_err)
                
                step_record["thought"] = plan_data['thought_process']
                step_record["code"] = plan_data['code']
                
                # 2. Execute
                local_scope = {}
                import sys
                from io import StringIO
                old_stdout = sys.stdout
                redirected_output = sys.stdout = StringIO()
                
                try:
                    exec(plan_data['code'], globals(), local_scope)
                    sys.stdout = old_stdout 
                    step_record["output"] = redirected_output.getvalue()
                except Exception as exec_err:
                    sys.stdout = old_stdout
                    raise exec_err

                # 3. Handle Results
                if 'final_result' not in local_scope:
                    raise ValueError("`final_result` variable missing.")
                
                actual_result = local_scope['final_result']
                
                # DataFrame to JSON for UI
                dataframe_json = None
                if isinstance(actual_result, pd.DataFrame):
                    dataframe_json = actual_result.head(100).to_json(orient='records', date_format='iso')
                
                # 4. Handle Plots
                plot_base64 = None
                if 'final_plot' in local_scope:
                    fig = local_scope['final_plot']
                    buf = io.BytesIO()
                    fig.savefig(buf, format="png", bbox_inches='tight')
                    buf.seek(0)
                    plot_base64 = base64.b64encode(buf.read()).decode("utf-8")
                    plt.close(fig)

                steps.append(step_record)
                
                # 5. Final Synthesis
                natural_answer = self.synthesize_answer(question, steps, actual_result)
                
                return {
                    "status": "success",
                    "answer": natural_answer,
                    "steps": steps,
                    "image": plot_base64,
                    "dataframe": dataframe_json 
                }

            except Exception as e:
                step_record["error"] = str(e)
                steps.append(step_record)
        
        return {
            "status": "failure",
            "answer": "I failed to generate a valid analysis after multiple attempts.",
            "steps": steps,
            "image": None,
            "dataframe": None
        }