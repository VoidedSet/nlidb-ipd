from agents.eda_agent import EDAAgent

agent = EDAAgent()

# print(agent.run("I want you to first find out all entries having null values in the studentsperformance table. " \
# "Then, fill those null values with random values appropriate to the column data type." \
# "If an entry has multiple null values delete that entry." \
# "Keep on doing this until there are no null values left in the table. " \
# "At the end give me entries that got updated with new random value." \
# "Finally, give me a summary statistics of the cleaned table."))

# print(agent.run("I want you to first find out all entries having null or NaN (for numerical columns) "
# "or having NULL as a string (for categorical columns) in the studentsperformance table. "
# "and then i will want you to drop those entries. " \
# "at the end give me the count of entries that were dropped and the summary statistics of the cleaned table."))

# print(agent.run("I want you to clean the data and perform eda on the studentsperformance table." \
#                 "Then i want you to find trends and patterns in the data and give me insights about the data." \
#                 "Finally, give me visualizations to support your insights."))

print(agent.run('''I want to build a high-accuracy predictive model. 

1. Create a new column 'Target_Score' which is the average of math, reading, and writing scores.
2. The goal is to predict 'Target_Score' using 'parental level of education' and 'test preparation course' as features.
3. PROBLEM: These are text columns. You must Convert/Encode them into numbers (Ordinal Encoding) so the model works.
4. Train a Linear Regression model. 
5. IF the R-squared score is below 0.95 (which it likely will be), I want you to iteratively CREATE NEW FEATURES (e.g., interaction terms like 'math * reading' or polynomial features) and retrain. 
6. Keep adding features until R-squared > 0.95 or you have tried 3 iterations.
7. Finally, overwrite the database table with the new 'Target_Score' column and print the final R-squared and the list of features used.'''))
