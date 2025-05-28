import streamlit as st
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

st.set_page_config(page_title="Market Insights", layout="wide")

# Check if a metric was selected
if "selected_metric" not in st.session_state:
    st.warning("⚠️ Please select a metric first on the home page.")
    st.stop()

query = st.session_state["selected_metric"]
query_label = query.split(" (")[0].strip()

st.title(f"📡 Market Insights for: {query_label}")

# Compose search queries
search_terms = [
    f"{query_label} market CAGR India site:investindia.gov.in",
    f"{query_label} market size historical India",
    f"{query_label} market trends India",
]

def get_ddg_results(query, max_results=5):
    with DDGS() as ddgs:
        return list(ddgs.text(query, max_results=max_results))

# Get and display search results
st.markdown("### 🔍 Scraped Insights & Market Data")

for i, term in enumerate(search_terms):
    st.markdown(f"#### 🔎 Search {i+1}: `{term}`")

    results = get_ddg_results(term)
    if not results:
        st.warning("No results found.")
        continue

    for res in results:
        title = res.get("title", "No title")
        snippet = res.get("body", "No snippet available.")
        link = res.get("href", "")

        st.markdown(f"**{title}**")
        st.markdown(f"- {snippet}")
        st.markdown(f"[🔗 Source]({link})")
        st.markdown("---")
