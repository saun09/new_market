import streamlit as st
import openai

st.set_page_config(page_title="Market Insights", layout="wide")

# Ensure OpenAI API key is set
openai.api_key = st.secrets.get("OPENAI_API_KEY")

# Retrieve selected metric from session state
if "selected_metric" not in st.session_state:
    st.warning("Please select a metric first on the home page.")
    st.stop()

query = st.session_state["selected_metric"]

st.title(f"📡 Market Insights for: {query}")

# Define the prompt for OpenAI
prompt = f"""
You are a market analyst. Provide the following information for the {query} market in India:
1. Current CAGR.
2. Historical market values for the past 5 years.
3. Key market trends.
4. Source links for the data provided.

Present the information in a structured format.
"""

# Call OpenAI API
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a market analyst."},
        {"role": "user", "content": prompt}
    ]
)

# Display the response
summary = response.choices[0].message["content"]
st.markdown("### 📈 Forecast Summary")
st.markdown(summary)
