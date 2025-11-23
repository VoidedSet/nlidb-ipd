from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm_setup import get_llm
from db_connection import get_db

class SQLAgent:
    def __init__(self):
        self.db = get_db()
        # Use the "fast" model (Groq/Llama3) for writing SQL
        self.llm = get_llm(model_type="fast")

    def get_schema(self):
        return self.db.get_table_info()

    def generate_sql(self, question: str):
        """
        Step 1: Convert Natural Language to SQL
        """
        schema = self.get_schema()
        
        template = """
        You are a MySQL expert. Given the database schema below, write a SQL query to answer the user's question.
        
        SCHEMA:
        {schema}
        
        QUESTION: {question}
        
        GUIDELINES:
        1. Return ONLY the SQL query. No markdown, no explanation.
        2. Use standard MySQL syntax.
        3. If the question is ambiguous, pick the most logical interpretation.
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", template),
            ("human", "{question}")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        raw_query = chain.invoke({"schema": schema, "question": question})
        
        # Cleaning the output (Llama 3 sometimes adds markdown)
        cleaned_query = raw_query.replace("```sql", "").replace("```", "").strip()
        return cleaned_query

    # ... imports remain the same

    def run(self, question: str):
        # 1. Generate SQL
        print("   [SQL Agent] Generating SQL...")
        sql_query = self.generate_sql(question)
        print(f"   [SQL Agent] Query: {sql_query}")
        
        # 2. Execute SQL (modified to handle multiple statements)
        try:
            # Split by semicolon to handle scripts (Drop; Create; Insert)
            # Note: This is a simple split. In prod, use a parser to avoid splitting text inside quotes.
            statements = [s.strip() for s in sql_query.split(';') if s.strip()]
            
            results = []
            for stmt in statements:
                print(f"      -> Executing: {stmt[:50]}...") # Print first 50 chars
                res = self.db.run(stmt)
                results.append(res)
            
            # We use the last result for the synthesis (usually the SELECT output)
            final_db_result = results[-1] if results else "Success"

        except Exception as e:
            return f"Error executing SQL: {e}"

        # 3. Synthesize Answer
        print("   [SQL Agent] Synthesizing answer...")
        
        synthesis_template = """
        You are a Data Analyst. 
        User Question: {question}
        SQL Query Used: {query}
        Database Result: {result}
        
        Please provide a concise, natural language answer based on the result.
        If the result is empty or "None", assume the action (like Insert/Delete) was successful and inform the user.
        """
        
        synth_prompt = ChatPromptTemplate.from_messages([("human", synthesis_template)])
        synth_chain = synth_prompt | self.llm | StrOutputParser()
        
        final_answer = synth_chain.invoke({
            "question": question,
            "query": sql_query,
            "result": final_db_result
        })
        
        return final_answer