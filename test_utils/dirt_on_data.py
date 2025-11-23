from sqlalchemy import create_engine, text
import random

db_name = "prototype_testing" 
connection_string = f"mysql+mysqlconnector://root:@localhost:3306/{db_name}"

engine = create_engine(connection_string)

print(f"Connecting to {db_name}...")

with engine.connect() as conn:
    conn.execute(text("UPDATE studentsperformance SET `math score` = NULL WHERE RAND() < 0.05"))
    
    conn.execute(text("UPDATE studentsperformance SET `reading score` = NULL WHERE RAND() < 0.05"))
    
    conn.execute(text("UPDATE studentsperformance SET `writing score` = NULL WHERE `math score` IS NULL AND RAND() < 0.5"))

    conn.commit()