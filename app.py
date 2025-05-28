import streamlit as st
from forecast_utils import extract_numeric_metrics, forecast_pu_consumption

st.title("📊 Forecast Anything: Market Metric Forecaster")

uploaded_file = st.file_uploader("Upload Spreadsheet", type=["xlsx"])
if uploaded_file:
    st.info("📂 Extracting metrics...")
    metrics_df = extract_numeric_metrics(uploaded_file)

    if metrics_df.empty:
        st.error("❌ No numeric metrics found.")
    else:
        selected_row = st.selectbox(
            "Select the metric to forecast:",
            metrics_df.apply(lambda row: f"{row['Label']} ({row['Value']} {row['Unit']}) — {row['Sheet']}", axis=1)
        )

        if selected_row:
            st.session_state["selected_metric"] = selected_row

        metric = metrics_df[metrics_df.apply(lambda row: f"{row['Label']} ({row['Value']} {row['Unit']}) — {row['Sheet']}" == selected_row, axis=1)].iloc[0]
        base_value = metric["Value"]
        base_year = st.number_input("Base Year (e.g., 2022)", value=2022)

        cagr_input = st.number_input("Enter CAGR (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.1)

        forecast_years = st.slider("Forecast Period (Years)", 1, 15, 5)

        df_forecast = forecast_pu_consumption(base_value, base_year, cagr_input / 100, forecast_years)

        st.write(f"### 📈 Forecast for: `{metric['Label']}`")
        st.dataframe(df_forecast)