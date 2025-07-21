import streamlit as st
from sp500_scanner import run_scan

st.set_page_config(page_title="📈 S&P 500 Scanner", layout="wide")

st.title("📈 S&P 500 Technical Scanner")
st.write("Filters stocks based on moving averages, recent highs, and momentum (AROC).")

limit = st.slider("Number of stocks to scan (use lower for faster results):", 10, 500, 50, step=10)

if st.button("Run Scan"):
    with st.spinner("Scanning S&P 500 tickers..."):
        df_results = run_scan(limit=limit)

    if not df_results.empty:
        st.success(f"Found {len(df_results)} matching stocks.")
        st.dataframe(df_results, use_container_width=True)
        st.download_button("Download CSV", df_results.to_csv(index=False), "scan_results.csv")
    else:
        st.warning("No stocks met the criteria.")
