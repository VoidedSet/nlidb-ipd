import pandas as pd
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_experimental.utilities import PythonREPL
from llm_setup import get_llm
from db_connection import get_db

class EDAAgent:
    def __init__(self):
        self.db = get_db()
        # We use the "fast" model for loops, but you can switch to "smart" if complex
        self.llm = get_llm(model_type="fast") 
        self.repl = PythonREPL()

    def get_schema(self):
        return self.db.get_table_info()

    def generate_plan_and_code(self, question: str, retry_context: str = ""):
        """
        Generates the JSON plan + Python code.
        retry_context: If the previous run failed, this contains the error msg.
        """
        schema = self.get_schema()
        
        system_prompt = """
        You are a Senior Data Scientist. You have access to a MySQL database.
        Your goal is to answer the user's question by writing Python code.
        
        DATABASE SCHEMA:
        {schema}
        
        INSTRUCTIONS:
        1. Return a VALID JSON object (no markdown formatting outside the json).
        2. The 'code' field must contain complete, executable Python code.
        3. Inside the code:
           - Use `import pandas as pd`
           - Use `import matplotlib.pyplot as plt` if plotting.
           - Connect to the DB using: 
             `engine = create_engine('mysql+mysqlconnector://root:@localhost:3306/student_db')`
             (Update the connection string to match the local setup: user 'root', no password).
           - Load data into a DataFrame: `df = pd.read_sql("SELECT * FROM ...", engine)`
           - Perform the analysis.
           - **CRITICAL**: Assign the final result to a variable named `final_result`.
        
        REQUIRED JSON STRUCTURE:
        {{
            "thought_process": "Explain why you are choosing this approach.",
            "expected_output_type": "str" | "float" | "dataframe" | "plot",
            "code": "The python code string..."
        }}
        """
        
        if retry_context:
            system_prompt += f"\n\nPREVIOUS ATTEMPT FAILED. ERROR:\n{retry_context}\nFix the code."

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{question}")
        ])
        
        # Use simple Invoke. JSON Mode is better, but string parsing works for Llama 3 usually.
        chain = prompt | self.llm | StrOutputParser()
        response = chain.invoke({"schema": schema, "question": question})
        
        # Clean cleanup (sometimes Llama wraps JSON in ```json ... ```)
        cleaned = response.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)

    def run(self, question: str):
        print(f"   [EDA Agent] Received: {question}")
        
        attempts = 0
        max_retries = 3
        previous_error = ""
        
        while attempts < max_retries:
            attempts += 1
            print(f"   [EDA Agent] Thinking (Attempt {attempts})...")
            
            try:
                # 1. Generate Plan
                plan_data = self.generate_plan_and_code(question, previous_error)
                print(f"   [EDA Agent] Plan: {plan_data['thought_process']}")
                
                # 2. Prepare Code (Inject sqlalchemy import if missing)
                code = "from sqlalchemy import create_engine\n" + plan_data['code']
                expected_type = plan_data['expected_output_type']
                
                print("   [EDA Agent] Executing Python...")
                
                # 3. Execute in REPL
                # PythonREPL returns the stdout (print statements)
                # To get the variable `final_result`, we usually need to print it at the end of the generated code
                # But a better way for the agent is to inspect the local scope. 
                # For this prototype, we will instruct the LLM to `print(final_result)` in the prompt? 
                # No, let's capture local scope.
                
                # We run the code using `exec` manually to capture variables, 
                # as LangChain's REPL is strictly for string output.
                local_scope = {}
                exec(code, globals(), local_scope)
                
                # 4. Verification Loop
                if 'final_result' not in local_scope:
                    raise ValueError("Code ran, but `final_result` variable was not defined.")
                
                actual_result = local_scope['final_result']
                print(f"   [EDA Agent] Result Type: {type(actual_result)}")
                
                # Basic Type Checking (Extend this logic as needed)
                if expected_type == "float" and not isinstance(actual_result, (float, int)):
                    raise ValueError(f"Expected float, got {type(actual_result)}")
                if expected_type == "dataframe" and not isinstance(actual_result, pd.DataFrame):
                    raise ValueError(f"Expected DataFrame, got {type(actual_result)}")
                
                return f"Analysis Complete. Result: {actual_result}"

            except Exception as e:
                print(f"   [EDA Agent] Error: {e}")
                previous_error = str(e)
        
        return "Failed to generate valid analysis after 3 attempts."