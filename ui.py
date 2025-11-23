import streamlit as st
import requests
import base64
import pandas as pd
import json

# Page Config for Professional Look
st.set_page_config(
    page_title="Querify 2.0",
    page_icon="🧠",
    layout="wide" # Wide layout for better "Notebook" feel
)

# Custom CSS for Minimalist Design
st.markdown("""
<style>
    /* Chat Message Bubble Styling */
    .stChatMessage {
        background-color: transparent;
    }
    /* Code Block Styling */
    .stCodeBlock {
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    /* DataFrame Container */
    .dataframe-container {
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("Querify 2.0 Agentic BI")
st.markdown("---")

# Session State for History
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- FUNCTION TO RENDER A MESSAGE ---
def render_message(role, content, is_new=False):
    with st.chat_message(role):
        # 1. If it's a simple text message
        if isinstance(content, str):
            st.markdown(content)
        
        # 2. If it's a Complex Agent Response (Dictionary)
        elif isinstance(content, dict):
            payload = content
            
            # A. The "Gemini" Thinking Dropdown
            if payload.get("steps"):
                # "complete" state makes it greyed out and collapsed by default
                status_label = "Thinking Process (Click to Expand)"
                state = "complete"
                
                # If this is the *new* message being generated, we might want it expanded initially?
                # But you requested hidden unless user wants to see.
                with st.status(status_label, expanded=False, state=state):
                    for step in payload["steps"]:
                        st.markdown(f"**Attempt {step['attempt']}**")
                        st.info(f"🧠 *{step['thought']}*")
                        with st.expander("View Code"):
                            st.code(step['code'], language="python")
                        if step['error']:
                            st.error(f"Error: {step['error']}")
                        if step['output']:
                            st.caption("Execution Output:")
                            st.text(step['output'])
                        st.divider()

            # B. The Main Natural Language Answer
            st.markdown(payload["answer"])

            # C. The "Notebook" Data Table
            if payload.get("dataframe"):
                try:
                    # Convert JSON string back to DataFrame
                    df = pd.read_json(payload["dataframe"], orient='records')
                    st.caption("📊 Data Preview:")
                    st.dataframe(df, use_container_width=True, hide_index=True)
                except Exception as e:
                    st.error(f"Could not render table: {e}")

            # D. The Embedded Plot
            if payload.get("image"):
                try:
                    image_bytes = base64.b64decode(payload["image"])
                    st.image(image_bytes, caption="Generated Visualization", use_column_width=False, width=600)
                except:
                    st.error("Error rendering plot image.")

# --- DISPLAY HISTORY ---
for msg in st.session_state.messages:
    render_message(msg["role"], msg["content"])

# --- INPUT HANDLING ---
if prompt := st.chat_input("Ask a question about your data..."):
    # 1. Append User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generate AI Response
    with st.chat_message("assistant"):
        # Create a placeholder container to stream updates if we wanted, 
        # but for now we just wait for the API
        with st.spinner("Analyzing Database..."):
            try:
                response = requests.post("http://localhost:8000/chat", json={"text": prompt})
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Hack: If it's SQL agent (type: sql), it returns simple dict. 
                    # If EDA, it returns complex dict. 
                    # We store the whole dict in history.
                    
                    st.session_state.messages.append({"role": "assistant", "content": data})
                    
                    # Force a rerun to render using the clean function defined above
                    st.rerun()
                else:
                    st.error(f"API Error: {response.status_code}")
            
            except Exception as e:
                st.error(f"Connection Failed: {e}")