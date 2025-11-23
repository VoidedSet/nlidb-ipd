from sqlalchemy import create_engine, text
import random

# UPDATE THIS TO YOUR DATABASE NAME
db_name = "prototype_testing" 
connection_string = f"mysql+mysqlconnector://root:@localhost:3306/{db_name}"

engine = create_engine(connection_string)

print(f"Connecting to {db_name}...")

with engine.connect() as conn:
    # 1. Randomly set 5% of math scores to NULL
    print("Injecting NULLs into math score...")
    conn.execute(text("UPDATE studentsperformance SET `math score` = NULL WHERE RAND() < 0.05"))
    
    # 2. Randomly set 5% of reading scores to NULL
    print("Injecting NULLs into reading score...")
    conn.execute(text("UPDATE studentsperformance SET `reading score` = NULL WHERE RAND() < 0.05"))
    
    # 3. Create some 'Double Null' rows (to test the delete logic)
    print("Creating rows with MULTIPLE NULLs...")
    conn.execute(text("UPDATE studentsperformance SET `writing score` = NULL WHERE `math score` IS NULL AND RAND() < 0.5"))

    conn.commit()
    print("Done! Data is now corrupted.")