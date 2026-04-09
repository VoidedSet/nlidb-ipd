from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import io
from agents.router import route_query
from agents.sql_agent import SQLAgent
from agents.eda_agent import EDAAgent

app = FastAPI(title="Querify 2.0 API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sql_agent = SQLAgent()
eda_agent = EDAAgent()

# Store CSV data in memory (for simple demo)
csv_storage = {}

class QueryRequest(BaseModel):
    text: str
    db_url: str | None = None
    csv_source: str | None = None  # name of CSV in storage

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        # Store in memory with filename as key
        csv_storage[file.filename] = df
        
        return {
            "status": "success",
            "filename": file.filename,
            "rows": len(df),
            "columns": len(df.columns),
            "message": f"Uploaded {file.filename} with {len(df)} rows"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/chat")
def chat_endpoint(request: QueryRequest):
    user_input = request.text
    
    print(f"[API] Request received: {user_input}")
    print(f"[API] DB URL from request: {request.db_url}")
    print(f"[API] CSV source from request: {request.csv_source}")
    
    try:
        route = route_query(user_input)
    except:
        route = "EDA_TASK"

    if route == "SQL_QUERY":
        if request.csv_source:
            return {"type": "error", "answer": "SQL queries not supported for CSV data. Use EDA analysis instead."}
        print(f"[API] Routing to SQL Agent with db_url: {request.db_url}")
        response = sql_agent.run(user_input, request.db_url)
        return {"type": "sql", "answer": response}

    elif route == "EDA_TASK":
        if request.csv_source and request.csv_source in csv_storage:
            # Use CSV data
            print(f"[API] Using CSV: {request.csv_source}")
            result = eda_agent.run_with_csv(user_input, csv_storage[request.csv_source])
        else:
            # Use database
            print(f"[API] Routing to EDA Agent with db_url: {request.db_url}")
            result = eda_agent.run(user_input, request.db_url)
        
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