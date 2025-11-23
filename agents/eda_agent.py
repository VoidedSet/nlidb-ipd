import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from langchain_experimental.utilities import PythonREPL
from llm_setup import get_llm
from db_connection import get_db

# 1. Define the Structure we want strictly
class EDAPlan(BaseModel):
    thought_process: str = Field(description="Reasoning about the data and approach")
    expected_output_type: str = Field(description="The Python type of the result: float, str, dataframe, plot, ndarray")
    code: str = Field(description="The executable Python code. Do not use markdown backticks inside this string.")

class EDAAgent:
    def __init__(self):
        self.db = get_db()
        self.llm = get_llm(model_type="fast") 
        self.repl = PythonREPL()
        self.parser = JsonOutputParser(pydantic_object=EDAPlan)

    def get_schema(self):
        return self.db.get_table_info()

    def generate_plan_and_code(self, question: str, retry_context: str = ""):
        schema = self.get_schema()
        format_instructions = self.parser.get_format_instructions()
        
        system_prompt = """
        You are a Senior Data Scientist. You have access to a MySQL database.
        
        DATABASE SCHEMA:
        {schema}
        
        GOAL:
        Write Python code to answer the user's question.
        
        INSTRUCTIONS:
        1. Look at the schema carefully. 
        2. Inside the 'code' field:
           - Use `import pandas as pd`
           - Use `import numpy as np`
           - Use `from sqlalchemy import create_engine`
           - Connect: `engine = create_engine('mysql+mysqlconnector://root:@localhost:3306/prototype_testing')`
           - Load data: `df = pd.read_sql("SELECT * FROM ...", engine)`
           - Perform the analysis.
           - Assign the final answer to variable `final_result`.
        
        DATA PERSISTENCE RULES (CRITICAL):
        - If the user asks to PERMANENTLY CHANGE, REMOVE, or CLEAN data (e.g., "drop rows", "fill nulls"):
          1. Perform the operation on the DataFrame (e.g., `df.dropna(inplace=True)`).
          2. WRITE BACK to the database using:
             `df.to_sql('table_name', engine, if_exists='replace', index=False)`
          3. IMPORTANT: Use `if_exists='replace'` to overwrite the old table with the clean data.
        
        PYTHON BEST PRACTICES:
        - Handling "NULL" strings vs NaN:
          `df.replace('NULL', np.nan, inplace=True)` before dropping or filling.
        
        {format_instructions}
        """
        
        if retry_context:
            system_prompt += f"\n\nPREVIOUS ATTEMPT FAILED. ERROR:\n{retry_context}\nReview the code and fix the syntax or logic."

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{question}")
        ])
        
        chain = prompt | self.llm | self.parser
        
        response = chain.invoke({
            "schema": schema, 
            "question": question,
            "format_instructions": format_instructions 
        })
        return response
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
                
                # 2. Extract Code
                code = plan_data['code']
                expected_type = plan_data['expected_output_type']
                
                print("   [EDA Agent] Executing Python...")
                
                # 3. Execute
                local_scope = {}
                exec(code, globals(), local_scope)
                
                # 4. Verification
                if 'final_result' not in local_scope:
                    raise ValueError("Code ran, but `final_result` variable was not defined.")
                
                actual_result = local_scope['final_result']
                print(f"   [EDA Agent] Result Type: {type(actual_result)}")
                
                # 5. Type Check & Auto-Correction
                if expected_type == "float" and isinstance(actual_result, pd.DataFrame):
                    if not actual_result.empty:
                        actual_result = actual_result.iloc[0,0]
                
                return f"Analysis Complete. Result: {actual_result}"

            except Exception as e:
                print(f"   [EDA Agent] Error: {e}")
                previous_error = str(e)
        
        return "Failed to generate valid analysis after 3 attempts."