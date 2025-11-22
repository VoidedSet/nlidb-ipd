from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from .models import DatabaseConnection
import urllib.parse
from sqlalchemy import inspect, text 

def build_connection_url(connection_instance: DatabaseConnection) -> str:
    """Constructs the SQLAlchemy connection URL, handling password decryption and encoding."""
    
    password_decrypted = connection_instance.password 
    password_safe = urllib.parse.quote_plus(password_decrypted)
    
    db_type = connection_instance.db_type.lower()
    
    if db_type == 'postgres':
        driver = 'postgresql'
        db_name = connection_instance.db_name 
    
    elif db_type == 'mysql':
        driver = 'mysql+pymysql'
        db_name = connection_instance.db_name
        
    else:
        raise ValueError(f"Unsupported database type: {connection_instance.db_type}")

    # Format: driver://user:pass@host:port/dbname
    return f"{driver}://{connection_instance.username}:{password_safe}@{connection_instance.host}:{connection_instance.port}/{db_name}"

def establish_connection(connection_instance: DatabaseConnection) -> Engine:
    """Establishes a temporary SQLAlchemy engine connection and tests it."""
    try:
        db_url = build_connection_url(connection_instance)
        engine = create_engine(db_url, pool_recycle=3600)
        
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            
        return engine
    
    except Exception as e:
        raise ConnectionError(f"Failed to connect to {connection_instance.name}: {str(e)}")


def introspect_schema(engine: Engine) -> dict:
    """Fetches table names and column metadata from the external database."""
    inspector = inspect(engine)
    metadata = {}
    table_names = inspector.get_table_names()
    
    for table_name in table_names:
        columns = inspector.get_columns(table_name)
        
        # Convert SQLAlchemy column objects to simple dicts
        metadata[table_name] = [
            {'name': c['name'], 'type': str(c['type'])}
            for c in columns
        ]
        
    return metadata