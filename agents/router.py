from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm_setup import get_llm

def route_query(question: str):
    llm = get_llm(model_type="fast")
    
    system_prompt = """
    You are an expert Data Router. You have access to a SQL Database.
    
    Your goal is to decide if the user's question requires:
    1. SQL_QUERY: A direct database retrieval (e.g., "How many users are there?", "Show me the top 5 sales").
    2. EDA_TASK: Complex analysis, visualization, plotting, or statistical reasoning requiring Python (e.g., "Plot the trend," "Calculate correlation," "Forecast next month").
    
    Output ONLY one word: 'SQL_QUERY' or 'EDA_TASK'.
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{question}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    decision = chain.invoke({"question": question})
    return decision.strip()