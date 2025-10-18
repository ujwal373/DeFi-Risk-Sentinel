import streamlit as st
import asyncio
from utils.solana_utils import fetch_solana_transactions
from utils.risk_engine import compute_solana_risk

st.set_page_config(page_title="Solana Risk Scanner", page_icon="🔍")

st.title("🔍 Solana Wallet Risk Scanner")
st.markdown("Check any **Solana wallet** for suspicious activity, tx patterns, or potential risks.")

wallet_address = st.text_input("Enter Solana wallet address:")

if wallet_address and st.button("Scan Now"):
    with st.spinner("Fetching transactions..."):
        tx_data = asyncio.run(fetch_solana_transactions(wallet_address))
        risk_result = compute_solana_risk(tx_data)

    st.subheader("📊 Risk Score")
    st.progress(risk_result["risk_score"] / 100)
    st.write("**Score:**", risk_result["risk_score"])
    st.write("**Reason:**", risk_result["reason"])

    if risk_result["flags"]:
        st.write("⚠️ Flags:", ", ".join(risk_result["flags"]))

    st.divider()
    st.subheader("🧾 Recent Transactions")
    st.json(tx_data)
