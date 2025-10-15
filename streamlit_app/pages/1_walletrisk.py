import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import get_risk

st.title("Wallet Risk Score")
wallet = st.text_input("Enter wallet address", value="0xABCDEF1234")

if st.button("Get Risk"):
    risks = get_risk(wallet)
    if not risks:
        st.warning("No data for this wallet.")
    else:
        latest = risks[-1]
        st.metric("Risk Score", latest["score"])
        st.write("Flags:", ", ".join(latest["flags"]))
        st.write("Why:", ", ".join(latest["rationale"]))
        st.write("Tx Hash:", latest["tx_hash"])
        st.line_chart([r["score"] for r in risks])
