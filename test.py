from agents.sql_agent import SQLAgent

agent = SQLAgent()
# Replace with a question relevant to your XAMPP database data
# response = agent.run('''Delete Courses table from the database and 
#                      create a new table named Enrollments with columns StudentID, CourseID, EnrollmentDate. 
#                      Then create a course table with course name and course id and 
#                      add Computer Networks, Algortithms, Data Structures as entries.
#                      Now enroll the existing students Jake in Computer Networks and Data Structures, Jhon in Algorithms and Data Structures
#                      Jane in all three courses, Mary in Computer Networks only, Peter in Algorithms and Data Structures and
#                      David in Data Structures only.''') 

response = agent.run('''List the names of students with their courses.''')

print("\nFINAL ANSWER:", response)