import streamlit as st
import re
import pandas as pd
import time
from duckduckgo_search import DDGS

st.set_page_config(page_title="Market Insights", layout="wide")

# Check if a metric was selected
if "selected_metric" not in st.session_state:
    st.warning("⚠️ Please select a metric first on the home page.")
    st.stop()

query = st.session_state["selected_metric"]
query_label = query.split(" (")[0].strip()

st.title(f"📡 Market Insights for: {query_label}")

search_terms = [
    f"{query_label} market CAGR India",
    f"{query_label} market size historical India",
    f"{query_label} market trends India",
]

def get_ddg_results(term, max_results=5, retries=3, delay=5):
    for attempt in range(retries):
        try:
            with DDGS() as ddgs:
                return list(ddgs.text(term, max_results=max_results))
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay * (2 ** attempt))  # Exponential backoff
            else:
                st.error(f"Failed to retrieve results for '{term}': {e}")
                return []

def extract_insights(text):
    cagr_match = re.search(r'CAGR[^0-9]*([\d.]+)%', text, re.IGNORECASE)
    cagr = cagr_match.group(1) + "%" if cagr_match else "Not found"

    history = re.findall(r'(INR|USD)[^\d]*(\d[\d,\.]*)[^0-9]*(\d{4})', text)
    trends = re.findall(r'\b(?:trend|growth|demand|urbanization|digital|consumer|technology)\w*\b', text, re.IGNORECASE)

    highlights = re.findall(r'\b(?:INR|USD|\d{4}|CAGR|\d+%)\b', text)

    return cagr, history, trends, highlights

st.markdown("### 🔍 Scraped Insights & Market Data")

all_history = []

for i, term in enumerate(search_terms):
    st.markdown(f"#### 🔎 Search {i+1}: {term}")

    results = get_ddg_results(term)
    if not results:
        st.warning("No results found.")
        continue

    for res in results:
        title = res.get("title", "No title")
        snippet = res.get("body", "No snippet available.")
        link = res.get("href", "")

        cagr, history, trends, highlights = extract_insights(snippet)
        all_history.extend(history)

        st.markdown(f"**📌 {title}**")
        st.markdown(f"🔗 [Source]({link})")
        st.markdown("---")
        st.markdown(f"**Snippet:**")
        for h in set(highlights):
            snippet = re.sub(f"\\b({re.escape(h)})\\b", r"**\1**", snippet)
        st.markdown(snippet)

        st.markdown(f"- **📈 CAGR**: {cagr}")
        if history:
            st.markdown("- **📊 Historical Values:**")
            for h in history:
                st.markdown(f"   • {h[0]} {h[1]} in {h[2]}")
        if trends:
            st.markdown("- **🌟 Trends:**")
            st.markdown("   • " + ", ".join(set(trends)).title())
        st.markdown("------")

# 📊 Plot historical data if available
if all_history:
    cleaned_data = []
    for h in all_history:
        try:
            year = int(h[2])
            value = float(h[1].replace(",", ""))
            cleaned_data.append((year, value))
        except:
            continue

    if cleaned_data:
        df = pd.DataFrame(cleaned_data, columns=["Year", "Value"])
        df = df.groupby("Year").mean().reset_index()  # In case of duplicate years

        st.markdown("### 📉 Historical Market Value Chart")
        st.line_chart(df.set_index("Year"))
