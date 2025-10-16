import streamlit as st
import uuid
import random
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import get_risk

WATCHER = os.getenv("WATCHER_URL", "http://127.0.0.1:8000")  # new!

st.title("Wallet Risk Checker (Live)")

wallet = st.text_input("Enter Wallet Address", value="0xABCDEF1234")

if st.button("Run Risk Analysis"):
    tx_hash = "0x" + uuid.uuid4().hex[:16]
    payload = {
        "wallet": wallet,
        "protocol": random.choice(["Uniswap", "Aave", "Custom", "Unknown"]),
        "apr": random.uniform(10, 250),
        "contract_age_days": random.choice([1, 3, 5, 12, 45]),
        "tx_hash": tx_hash
    }

    try:
        import httpx
        r = httpx.post(f"{WATCHER}/analyze_wallet", json=payload, timeout=10)
        if r.status_code == 200:
            st.success(f"Risk processed for wallet: {wallet}")
    except Exception as e:
        st.error(f"Error analyzing: {e}")

risks = get_risk(wallet)
if risks:
    latest = risks[-1]
    st.metric("Risk Score", latest["score"])
    st.write("Flags:", ", ".join(latest["flags"]))
    st.write("Why:", ", ".join(latest["rationale"]))
    st.write("Tx Hash:", latest["tx_hash"])
    st.line_chart([r["score"] for r in risks])
