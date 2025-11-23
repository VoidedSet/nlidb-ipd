import os
from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv

load_dotenv()

def get_db():
    """
    Establishes a connection to the MySQL database using SQLAlchemy
    and returns a LangChain SQLDatabase wrapper.
    """
    db_uri = os.getenv("DATABASE_URL")
    if not db_uri:
        raise ValueError("DATABASE_URL not found in .env")
        
    # sample_rows_in_table_info=0 prevents it from scanning data (faster)
    return SQLDatabase.from_uri(db_uri, sample_rows_in_table_info=0)

if __name__ == "__main__":
    # Quick test
    try:
        db = get_db()
        print(f"Connected! Tables found: {db.get_usable_table_names()}")
    except Exception as e:
        print(f"Connection failed: {e}")