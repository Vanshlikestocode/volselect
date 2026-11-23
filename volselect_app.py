"""VolSelect site: NIFTY volatility and risk monitor. An overview, the live market (forward paper-trading
record, target portfolio for the next rebalance, delayed quotes) and the walk-forward research behind it.

    streamlit run volselect_app.py
"""
import streamlit as st

pages = [st.Page("views/overview.py", title="Overview", icon=":material/home:", default=True),
         st.Page("views/live_market.py", title="Live market", icon=":material/monitoring:"),
         st.Page("views/research.py", title="Research", icon=":material/insights:")]
nav = st.navigation(pages)
with st.sidebar:
    st.markdown("**VolSelect**  \nNIFTY volatility and risk monitor")
    st.caption("By Vansh Dave and Karthik Agarwal. Updated every trading day at 18:00 IST. Paper trading only; not investment advice.")
nav.run()
