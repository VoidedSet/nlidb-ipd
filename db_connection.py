import os
from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv

load_dotenv()

def get_db(uri=None):
    db_uri = uri or os.getenv("DATABASE_URL")
    if not db_uri:
        raise ValueError("No database source provided.")
    return SQLDatabase.from_uri(db_uri)

if __name__ == "__main__":
    try:
        db = get_db()
        print(f"Connected! Tables found: {db.get_usable_table_names()}")
    except Exception as e:
        print(f"Connection failed: {e}")