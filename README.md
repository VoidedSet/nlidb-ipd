# Querify

An LLM-driven BI prototype that routes natural-language questions to either SQL or exploratory data analysis (EDA), then returns a concise narrative, tables, and charts.

## What It Does

- Natural language to SQL for direct database retrieval.
- EDA on database tables or uploaded CSVs with plots and summary stats.
- Automatic routing between SQL and EDA requests.
- Two UIs: Streamlit chat UI and a lightweight static web client.

## Architecture (Current)

```text
User
  -> Streamlit UI (ui.py) or Static Web UI (frontend/)
  -> FastAPI backend (api.py)
  -> Route agent (LLM)
      -> SQL agent (MySQL via SQLAlchemy)
      -> EDA agent (pandas + matplotlib)
  -> Response (answer + optional table + optional plot)
```

## Example Output

![Sales distribution example](output/sales_distribution.png)

## Repository Layout

- api.py: FastAPI backend and routing endpoint.
- ui.py: Streamlit chat UI.
- agents/: route, SQL, and EDA agents.
- frontend/: static UI (HTML/CSS/JS) and a small local server.
- test-data/: sample CSVs for quick testing.
- output/: example images and generated artifacts.

## Setup

### 1) Install dependencies

```bash
python -m venv .venv
```

Windows PowerShell:

```bash
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Configure environment

Create a .env file with the following as needed:

```text
DATABASE_URL=mysql+pymysql://user:password@host:3306/dbname
GROQ_API_KEY=your_groq_key
FEATHERLESS_API_KEY=your_featherless_key
```

Notes:

- DATABASE_URL is required for SQL queries and DB-backed EDA.
- CSV analysis can be done without a database connection.

### 3) Run the backend

```bash
python api.py
```

### 4) Run a UI

Streamlit UI:

```bash
streamlit run ui.py
```

Static web UI:

```bash
python frontend/server.py
```

## Example Queries

SQL:

```text
Show the top 5 products by revenue
```

EDA:

```text
Plot monthly sales trend
```

CSV EDA:

```text
Detect outliers in customer spending
```

## Notes

- The router decides between SQL and EDA based on the question.
- The EDA agent uses pandas and matplotlib to generate plots and summary stats.
- CSVs are stored in memory for the current server session.

## Contributors

- Kshayik Doshi
- Krish Shah
- Kartik Sunil
- Rishi Mehta

## License

This project is intended for academic and research purposes.
