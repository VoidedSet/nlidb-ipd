from agents.sql_agent import SQLAgent

agent = SQLAgent()
response = agent.run('''Delete Courses table from the database and 
                     create a new table named Enrollments with columns StudentID, CourseID, EnrollmentDate. 
                     Then create a course table with course name and course id and 
                     add Computer Networks, Algortithms, Data Structures as entries.
                     Now enroll the existing students Jake in Computer Networks and Data Structures, Jhon in Algorithms and Data Structures
                     Jane in all three courses, Mary in Computer Networks only, Peter in Algorithms and Data Structures and
                     David in Data Structures only.''') 

# response = agent.run('''I first want you to give the count of entries in this table and then randomly populate a the studentsperformance table with 10 unclean half null entries. at the end i want you to give the count of entries again to make sure 10 new entries have been added.''')

print("\nFINAL ANSWER:", response)