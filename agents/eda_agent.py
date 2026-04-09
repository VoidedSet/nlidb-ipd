import os
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from sqlalchemy import create_engine, inspect, text
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm_setup import get_llm
from db_connection import get_db

class EDAAgent:
    def __init__(self):
        self.llm = get_llm(role="coder")

    def get_schema(self, db_url: str = None):
        return get_db(db_url).get_table_info()

    def extract_column_from_question(self, question: str, available_cols: list):
        """Use LLM to identify which columns user is asking about"""
        prompt = ChatPromptTemplate.from_messages([
            ("human", f"""Given the user question and available columns, extract which column(s) they're interested in.
            
User question: {question}
Available columns: {', '.join(available_cols[:20])}

Return ONLY the column name(s) separated by commas. If no specific column mentioned, return the first numeric column.
If you can't find a match, return 'auto' to pick the best numeric column.""")
        ])
        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({}).strip()
        
        # Try to find the column in available columns
        cols_lower = [c.lower() for c in available_cols]
        result_lower = result.lower()
        
        for col in available_cols:
            if col.lower() in result_lower or result_lower in col.lower():
                return col
        
        # If no match, return first numeric column
        for col in available_cols:
            if col not in [str(type(x).__name__) for x in [1, 1.0, pd.Timestamp.now()]]:
                return col
        return available_cols[0] if available_cols else None

    def find_entity_filter(self, question: str, df: pd.DataFrame):
        """Detect if user is asking about a specific product/entity and return filter"""
        # Check text columns for potential product names
        text_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        if not text_cols:
            return None, None
        
        # Simple keyword matching in text columns
        question_lower = question.lower()
        keywords = question_lower.split()
        
        for col in text_cols:
            col_values = df[col].astype(str).str.lower().unique()
            for val in col_values:
                # Check if any multi-word product names match
                for keyword in keywords:
                    if len(keyword) > 3 and keyword in val:  # Avoid matching tiny words
                        matching_rows = df[df[col].astype(str).str.lower().str.contains(keyword, na=False)]
                        if len(matching_rows) > 0:
                            return col, matching_rows
        
        return None, None

    def analyze_entity(self, entity_df: pd.DataFrame, entity_name: str):
        """Generate business-relevant analysis for a specific entity"""
        if entity_df.empty:
            return None
        
        # Find numeric columns for analysis
        numeric_cols = entity_df.select_dtypes(include=['number']).columns.tolist()
        
        metrics = {}
        if 'Sales' in numeric_cols:
            metrics['Total Sales'] = entity_df['Sales'].sum()
            metrics['Avg Sale'] = entity_df['Sales'].mean()
        
        if 'Profit' in numeric_cols:
            metrics['Total Profit'] = entity_df['Profit'].sum()
            metrics['Avg Profit'] = entity_df['Profit'].mean()
            metrics['Profit Margin'] = (metrics['Total Profit'] / metrics['Total Sales'] * 100) if metrics.get('Total Sales') else 0
        
        if 'Quantity' in numeric_cols:
            metrics['Units Sold'] = entity_df['Quantity'].sum()
        
        metrics['Transactions'] = len(entity_df)
        
        return metrics

    def run(self, question: str, db_url: str = None):
        steps = []
        try:
            # Get table info
            db = get_db(db_url)
            schema = db.get_table_info()
            
            step1 = {
                "attempt": 1,
                "thought": f"Processing question: {question}",
                "code": "Schema retrieval",
                "error": None,
                "output": "Ready"
            }
            steps.append(step1)

            # Simple data load - just get first table and basic stats
            db_uri = db_url or os.getenv("DATABASE_URL")
            if not db_uri:
                return {
                    "status": "failure",
                    "answer": "No database configured. Please enter database credentials.",
                    "steps": steps,
                    "image": None,
                    "dataframe": None
                }
            engine = create_engine(db_uri)
            
            # Get first table name
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            if not tables:
                return {
                    "status": "failure",
                    "answer": "No tables found in database",
                    "steps": steps,
                    "image": None,
                    "dataframe": None
                }
            
            # Load data from first table
            table_name = tables[0]
            query = f"SELECT * FROM {table_name} LIMIT 1000"
            df = pd.read_sql(query, engine)
            
            # Check if user is asking about a specific entity/product
            entity_col, entity_df = self.find_entity_filter(question, df)
            
            if entity_df is not None and len(entity_df) > 0:
                # Analyze specific product/entity
                entity_name = entity_df[entity_col].iloc[0] if entity_col else "Product"
                step1["thought"] = f"Found specific entity in '{entity_col}': {entity_name}"
                step1["code"] = f"df_filtered = df[df['{entity_col}'].str.contains('{entity_name[:25]}', na=False)]"
                step1["output"] = f"Filtered to {len(entity_df)} matching records"
                
                metrics = self.analyze_entity(entity_df, entity_name)
                
                # Create visualization for the entity
                plot_base64 = None
                try:
                    numeric_cols = entity_df.select_dtypes(include=['number']).columns.tolist()
                    if 'Profit' in numeric_cols:
                        fig, ax = plt.subplots(figsize=(10, 5))
                        entity_df['Profit'].hist(bins=20, ax=ax, edgecolor='black', color='steelblue')
                        ax.set_title(f"Profit Distribution: {entity_name[:40]}")
                        ax.set_xlabel("Profit per Transaction")
                        ax.set_ylabel("Frequency")
                        
                        buf = io.BytesIO()
                        fig.savefig(buf, format='png', bbox_inches='tight')
                        buf.seek(0)
                        plot_base64 = base64.b64encode(buf.read()).decode('utf-8')
                        plt.close(fig)
                except Exception as plot_err:
                    print(f"Plot error: {plot_err}")
                
                # Build business recommendation with detailed insights
                profit_margin = metrics.get('Profit Margin', 0)
                total_profit = metrics.get('Total Profit', 0)
                transactions = metrics.get('Transactions', 0)
                
                recommendation = "✓ Good opportunity" if profit_margin > 10 and total_profit > 0 else "⚠️ Caution advised" if profit_margin < 0 else "→ Monitor performance"
                
                # Generate detailed insights
                insights = []
                insights.append(f"${total_profit:.2f} profit" if total_profit >= 0 else f"${total_profit:.2f} loss")
                insights.append(f"{profit_margin:.1f}% margin")
                insights.append(f"{transactions} transactions")
                
                answer = f"{recommendation} for '{entity_name}': {' | '.join(insights)}"
                
                # Prepare dataframe JSON - show just this entity
                dataframe_json = entity_df.head(50).to_json(orient='records', date_format='iso')
                
                return {
                    "status": "success",
                    "answer": answer,
                    "steps": steps,
                    "image": plot_base64,
                    "dataframe": dataframe_json
                }
            
            # Extract which column to analyze based on question
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            
            if not numeric_cols:
                numeric_cols = df.columns.tolist()
            
            # Use LLM or simple matching to find relevant column
            target_col = self.extract_column_from_question(question, numeric_cols or df.columns.tolist())
            if not target_col:
                target_col = numeric_cols[0] if numeric_cols else df.columns[0]
            
            # Generate stats for the target column
            if pd.api.types.is_numeric_dtype(df[target_col]):
                col_stats = df[target_col].describe().to_dict()
                stats_text = f"Mean: {col_stats.get('mean', 'N/A'):.2f}, Median: {df[target_col].median():.2f}, Std: {col_stats.get('std', 'N/A'):.2f}"
            else:
                col_stats = df[target_col].value_counts().head(5).to_dict()
                stats_text = f"Top values: {', '.join([f'{k} ({v})' for k, v in list(col_stats.items())[:3]])}"
            
            # Create visualization for target column
            plot_base64 = None
            try:
                fig, ax = plt.subplots(figsize=(10, 5))
                
                if pd.api.types.is_numeric_dtype(df[target_col]):
                    ax.hist(df[target_col].dropna(), bins=30, edgecolor='black', color='steelblue')
                    ax.set_ylabel("Frequency")
                else:
                    top_vals = df[target_col].value_counts().head(10)
                    ax.bar(top_vals.index.astype(str), top_vals.values, color='steelblue', edgecolor='black')
                    ax.tick_params(axis='x', rotation=45)
                    ax.set_ylabel("Count")
                
                ax.set_title(f"Analysis of {target_col}")
                ax.set_xlabel(target_col)
                
                buf = io.BytesIO()
                fig.savefig(buf, format='png', bbox_inches='tight')
                buf.seek(0)
                plot_base64 = base64.b64encode(buf.read()).decode('utf-8')
                plt.close(fig)
            except Exception as plot_err:
                print(f"Plot error: {plot_err}")
            
            # Prepare dataframe JSON
            dataframe_json = df.head(50).to_json(orient='records', date_format='iso')
            
            # Generate answer specific to the question
            answer = f"Analyzed '{target_col}' in table '{table_name}' ({len(df)} rows). {stats_text}"
            
            return {
                "status": "success",
                "answer": answer,
                "steps": steps,
                "image": plot_base64,
                "dataframe": dataframe_json
            }
            
        except Exception as e:
            return {
                "status": "failure",
                "answer": f"Analysis failed: {str(e)}",
                "steps": steps,
                "image": None,
                "dataframe": None
            }

    def run_with_csv(self, question: str, df: pd.DataFrame):
        """Analyze CSV data"""
        steps = []
        try:
            step1 = {
                "attempt": 1,
                "thought": f"Processing: {question}",
                "code": "CSV loaded",
                "error": None,
                "output": "Ready"
            }
            steps.append(step1)
            
            # First, check if user is asking about a specific entity/product
            entity_col, entity_df = self.find_entity_filter(question, df)
            
            if entity_df is not None and len(entity_df) > 0:
                # Analyze specific product/entity
                entity_name = entity_df[entity_col].iloc[0] if entity_col else "Product"
                step1["thought"] = f"Found specific entity in '{entity_col}': {entity_name}"
                step1["code"] = f"df_filtered = df[df['{entity_col}'].str.contains('{entity_name[:25]}', na=False)]"
                step1["output"] = f"Filtered to {len(entity_df)} matching records"
                
                metrics = self.analyze_entity(entity_df, entity_name)
                
                # Create visualization for the entity
                plot_base64 = None
                try:
                    numeric_cols = entity_df.select_dtypes(include=['number']).columns.tolist()
                    if 'Profit' in numeric_cols:
                        fig, ax = plt.subplots(figsize=(10, 5))
                        entity_df['Profit'].hist(bins=20, ax=ax, edgecolor='black', color='steelblue')
                        ax.set_title(f"Profit Distribution: {entity_name[:40]}")
                        ax.set_xlabel("Profit per Transaction")
                        ax.set_ylabel("Frequency")
                        
                        buf = io.BytesIO()
                        fig.savefig(buf, format='png', bbox_inches='tight')
                        buf.seek(0)
                        plot_base64 = base64.b64encode(buf.read()).decode('utf-8')
                        plt.close(fig)
                except Exception as plot_err:
                    print(f"Plot error: {plot_err}")
                
                # Build business recommendation with detailed insights
                profit_margin = metrics.get('Profit Margin', 0)
                total_profit = metrics.get('Total Profit', 0)
                transactions = metrics.get('Transactions', 0)
                
                recommendation = "✓ Good opportunity" if profit_margin > 10 and total_profit > 0 else "⚠️ Caution advised" if profit_margin < 0 else "→ Monitor performance"
                
                # Generate detailed insights
                insights = []
                insights.append(f"${total_profit:.2f} profit" if total_profit >= 0 else f"${total_profit:.2f} loss")
                insights.append(f"{profit_margin:.1f}% margin")
                insights.append(f"{transactions} transactions")
                
                answer = f"{recommendation} for '{entity_name}': {' | '.join(insights)}"
                recommendation = "✓ Good opportunity" if profit_margin > 10 and total_profit > 0 else "⚠️ Caution advised" if profit_margin < 0 else "→ Monitor performance"
                
                answer = f"{recommendation} for '{entity_name}': {metrics['Transactions']} sales, ${total_profit:.2f} profit, {profit_margin:.1f}% margin"
                
                # Prepare dataframe JSON - show just this entity
                dataframe_json = entity_df.head(50).to_json(orient='records', date_format='iso')
                
                return {
                    "status": "success",
                    "answer": answer,
                    "steps": steps,
                    "image": plot_base64,
                    "dataframe": dataframe_json
                }
            
            # Otherwise, analyze by column
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            
            if not numeric_cols:
                numeric_cols = df.columns.tolist()
            
            # Use LLM to find relevant column
            target_col = self.extract_column_from_question(question, numeric_cols or df.columns.tolist())
            if not target_col:
                target_col = numeric_cols[0] if numeric_cols else df.columns[0]
            
            # Generate stats for the target column
            if pd.api.types.is_numeric_dtype(df[target_col]):
                col_stats = df[target_col].describe().to_dict()
                stats_text = f"Mean: {col_stats.get('mean', 'N/A'):.2f}, Median: {df[target_col].median():.2f}, Std: {col_stats.get('std', 'N/A'):.2f}"
            else:
                col_stats = df[target_col].value_counts().head(5).to_dict()
                stats_text = f"Top values: {', '.join([f'{k} ({v})' for k, v in list(col_stats.items())[:3]])}"
            
            # Create visualization for target column
            plot_base64 = None
            try:
                fig, ax = plt.subplots(figsize=(10, 5))
                
                if pd.api.types.is_numeric_dtype(df[target_col]):
                    ax.hist(df[target_col].dropna(), bins=30, edgecolor='black', color='steelblue')
                    ax.set_ylabel("Frequency")
                else:
                    top_vals = df[target_col].value_counts().head(10)
                    ax.bar(top_vals.index.astype(str), top_vals.values, color='steelblue', edgecolor='black')
                    ax.tick_params(axis='x', rotation=45)
                    ax.set_ylabel("Count")
                
                ax.set_title(f"Analysis of {target_col}")
                ax.set_xlabel(target_col)
                
                buf = io.BytesIO()
                fig.savefig(buf, format='png', bbox_inches='tight')
                buf.seek(0)
                plot_base64 = base64.b64encode(buf.read()).decode('utf-8')
                plt.close(fig)
            except Exception as plot_err:
                print(f"Plot error: {plot_err}")
            
            # Prepare dataframe JSON
            dataframe_json = df.head(50).to_json(orient='records', date_format='iso')
            
            # Generate answer specific to the question
            answer = f"Analyzed '{target_col}' in CSV ({len(df)} rows). {stats_text}"
            
            return {
                "status": "success",
                "answer": answer,
                "steps": steps,
                "image": plot_base64,
                "dataframe": dataframe_json
            }
            
        except Exception as e:
            return {
                "status": "failure",
                "answer": f"CSV analysis failed: {str(e)}",
                "steps": steps,
                "image": None,
                "dataframe": None
            }
