from fastapi import FastAPI
from pydantic import BaseModel
from agents.router import route_query
from agents.sql_agent import SQLAgent
from agents.eda_agent import EDAAgent

app = FastAPI(title="Querify 2.0 API")

sql_agent = SQLAgent()
eda_agent = EDAAgent()

class QueryRequest(BaseModel):
    text: str

@app.post("/chat")
def chat_endpoint(request: QueryRequest):
    user_input = request.text
    
    try:
        route = route_query(user_input)
    except:
        route = "EDA_TASK"

    if route == "SQL_QUERY":
        response = sql_agent.run(user_input)
        return {"type": "sql", "answer": response}

    elif route == "EDA_TASK":
        result = eda_agent.run(user_input)
        return {
            "type": "eda",
            "answer": result["answer"],
            "steps": result["steps"],
            "image": result["image"],
            "dataframe": result["dataframe"]
        }

    return {"type": "error", "answer": "Unknown route"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)