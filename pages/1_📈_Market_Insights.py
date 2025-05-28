import streamlit as st
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from duckduckgo_search import DDGS
from sklearn.linear_model import LinearRegression
from io import BytesIO

st.set_page_config(page_title="Market Insights", layout="wide")

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
                time.sleep(delay * (2 ** attempt))  # exponential backoff
            else:
                st.error(f"❌ Failed: {term} — {e}")
                return []

def extract_insights(text):
    cagr_match = re.search(r'CAGR[^0-9]*([\d.]+)%', text, re.IGNORECASE)
    cagr = float(cagr_match.group(1)) if cagr_match else None

    history = re.findall(r'(INR|USD)[^\d]*(\d[\d,\.]*)[^0-9]*(\d{4})', text)
    trends = re.findall(r'\b(?:trend|growth|demand|urbanization|digital|consumer|technology)\w*\b', text, re.IGNORECASE)

    return cagr, history, trends

def perform_regression(history):
    if not history:
        return None, None, None

    years, values = [], []
    for h in history:
        try:
            year = int(h[2])
            value = float(h[1].replace(',', ''))
            years.append(year)
            values.append(value)
        except:
            continue

    if len(years) < 2:
        return None, None, None

    X = np.array(years).reshape(-1, 1)
    y = np.array(values)
    model = LinearRegression().fit(X, y)
    future_years = np.arange(max(years)+1, max(years)+6).reshape(-1, 1)
    predictions = model.predict(future_years)

    df = pd.DataFrame({
        "Year": list(years) + list(future_years.flatten()),
        "Value": list(values) + list(predictions.astype(int)),
        "Type": ["Historical"] * len(years) + ["Forecast"] * len(future_years)
    })

    cagr = ((values[-1] / values[0]) ** (1 / (years[-1] - years[0])) - 1) * 100
    return df, cagr, (years, values, future_years.flatten(), predictions)

def convert_to_excel(df, summary, plot_fig):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Market Data')
        summary.to_excel(writer, index=False, sheet_name='Summary')

        worksheet = writer.sheets['Market Data']
        img_data = BytesIO()
        plot_fig.savefig(img_data, format='png')
        img_data.seek(0)
        worksheet.insert_image('G2', 'forecast_chart.png', {'image_data': img_data})
    output.seek(0)
    return output

# Scrape and process
st.markdown("### 🔍 Web Insights")
all_history, found_cagr, all_trends = [], None, []

for i, term in enumerate(search_terms):
    st.markdown(f"#### 🔎 Search {i+1}: `{term}`")
    results = get_ddg_results(term)
    if not results:
        st.warning("No results found.")
        continue

    for res in results:
        title = res.get("title", "No title")
        snippet = res.get("body", "No snippet")
        link = res.get("href", "")

        cagr, history, trends = extract_insights(snippet)
        if cagr and not found_cagr:
            found_cagr = cagr
        all_history.extend(history)
        all_trends.extend(trends)

        st.markdown(f"**📌 {title}**")
        st.markdown(f"🔗 [Source]({link})")
        st.markdown(f"**Snippet:** {snippet}")
        if cagr:
            st.markdown(f"- **📈 CAGR**: `{cagr}%`")
        if history:
            st.markdown("- **📊 Historical Values:**")
            for h in history:
                st.markdown(f"   • {h[0]} {h[1]} in {h[2]}")
        if trends:
            st.markdown("- **🌟 Trends:** " + ", ".join(set(trends)).title())
        st.markdown("---")
