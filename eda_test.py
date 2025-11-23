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






