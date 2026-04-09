# Querify

> An LLM-driven Business Intelligence engine with NL2SQL, iterative EDA, sandboxed Python execution, multilingual querying, and sentiment-aware decision support.

## Overview

Querify is an intelligent business intelligence platform that allows users to interact with structured and unstructured data using natural language.

Unlike traditional NL2SQL systems that only convert a query into SQL, Querify can:

* Translate natural language into SQL
* Perform full exploratory data analysis (EDA)
* Generate and execute Python code safely inside a sandbox
* Support both SQL and NoSQL data sources
* Work with multilingual queries
* Analyze customer sentiment from reviews and textual data
* Produce human-readable insights, charts, and summaries

The system is designed primarily for small and medium businesses that need powerful analytics without requiring technical knowledge of SQL, Python, or data science.

---

# Features

* Natural Language → SQL translation
* Automatic routing between SQL and EDA tasks
* Iterative multi-pass EDA using LLM feedback loops
* Secure sandboxed Python execution
* Support for MySQL and MongoDB
* Multilingual query support
* Sentiment analysis for customer reviews and feedback
* Human-readable explanation generation
* Graph and visualization generation
* Role-Based Access Control (RBAC) support

---

# Architecture

```text
User
  ↓
Streamlit Frontend (ui.py)
  ↓
FastAPI Backend (api.py)
  ↓
Route Agent (LLM)
  ↓
Decision Node
 ├── SQL Agent → SQL Database
 └── EDA Agent → Python Sandbox
  ↓
Synthesizer LLM
  ↓
User Response
```

## Components

### 1. Frontend

Built using Streamlit.

Responsibilities:

* Accept user query
* Display tables, charts, and explanations
* Send query to backend using HTTP POST

### 2. Backend

Built using FastAPI.

Responsibilities:

* Receive frontend request
* Call `route_query()`
* Forward task to the appropriate agent
* Return final response

### 3. Route Agent

The Route Agent is an LLM-based classifier that determines whether the query is:

* `SQL_QUERY`
* `EDA_TASK`

Example:

* "Show total sales for 2024" → SQL Query
* "Plot monthly sales trends" → EDA Task

### 4. SQL Agent

The SQL Agent converts natural language into SQL.

Example:

```sql
SELECT department, COUNT(*)
FROM employees
GROUP BY department;
```

### 5. EDA Agent

The EDA Agent generates Python code for:

* Statistical summaries
* Correlation analysis
* Missing value detection
* Outlier detection
* Graph generation

### 6. Python Sandbox

All generated code is executed inside a restricted sandbox to prevent:

* File system access
* Network access
* Dangerous imports
* Arbitrary shell execution

### 7. Synthesizer

The Synthesizer LLM converts raw outputs into a clean explanation for the user.

---

# Iterative EDA Workflow

Querify does not rely on a single-pass analysis.

Instead, it repeatedly improves its analysis using a feedback loop:

1. Generate an initial EDA plan and Python code
2. Execute the code in the sandbox
3. Capture results and errors
4. Feed results back into the LLM
5. Refine the analysis until convergence

```text
User Query
   ↓
LLM (Coder)
   ↓
Python Sandbox
   ↓
Success?
 ├── No → Error Logger → LLM Retry
 └── Yes → Result + Plot
   ↓
LLM Synthesizer
   ↓
Final Answer
```

This allows Querify to recover automatically from syntax errors, bad plots, or incomplete analyses.

---

# Tech Stack

| Layer               | Technology                             |
| ------------------- | -------------------------------------- |
| Frontend            | Streamlit                              |
| Backend             | FastAPI                                |
| LLM Integration     | OpenAI / Gemini / other compatible LLM |
| Database            | MySQL, MongoDB                         |
| Data Processing     | Pandas                                 |
| Visualization       | Matplotlib, Seaborn                    |
| Sentiment Analysis  | DistilBERT (SST-2)                     |
| Execution Isolation | Python Sandbox                         |

---

# Example Queries

### SQL Queries

```text
Show the top 5 products by revenue
```

```text
How many employees joined in 2024?
```

```text
List customers from Mumbai
```

### EDA Queries

```text
Plot monthly sales trend
```

```text
Find correlation between price and demand
```

```text
Detect outliers in customer spending
```

### Sentiment Queries

```text
Analyze customer review sentiment by month
```

```text
Compare product sales with review sentiment
```

---

# Sample Output

Querify can return:

* SQL result tables
* Charts and plots
* Natural language summaries
* Statistical insights
* Sentiment distributions

Example:

> Sales increased by 18% between March and June. Customer sentiment also improved during the same period, suggesting a positive relationship between satisfaction and revenue.

---

# Experimental Results

From initial testing:

* 84% SQL accuracy in zero-shot mode
* 94% SQL accuracy with schema-aware prompting
* Average EDA convergence in 3.2 iterations
* 90% successful sandbox code execution rate

---

# Future Work

* Real-time streaming analytics
* Retrieval-Augmented Generation (RAG)
* Interactive dashboards
* More advanced chart support
* Larger benchmark evaluation
* Enterprise deployment with advanced RBAC

---

# Contributors

* Kshayik Doshi
* Krish Shah
* Kartik Sunil
* Rishi Mehta

---

# License

This project is intended for academic and research purposes.

```text
Copyright © 2025
```
