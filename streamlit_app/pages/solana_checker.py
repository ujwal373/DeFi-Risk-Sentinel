# streamlit_app/pages/solana_checker.py

import streamlit as st
from utils.solana_utils import fetch_solana_transactions
from utils.risk_engine import compute_solana_risk

st.set_page_config(page_title="Solana Risk Scanner", page_icon="🔍")

st.title("🔍 Solana Wallet Risk Scanner")
st.markdown("Check any **Solana wallet** for suspicious activity, tx patterns, or potential risks.")

# --- Input ---
wallet_address = st.text_input("Enter Solana wallet address:", help="Paste any valid Solana public address")

if wallet_address:
    with st.spinner("Fetching transactions and assessing risk..."):
        tx_data = fetch_solana_transactions(wallet_address)
        risk_result = compute_solana_risk(tx_data)

    st.subheader("📊 Risk Score")
    st.progress(risk_result["risk_score"] / 100)
    st.markdown(f"**Score**: `{risk_result['risk_score']} / 100`")
    st.markdown(f"**Reason**: {risk_result['reason']}")

    if risk_result["flags"]:
        st.markdown("⚠️ **Risk Flags Triggered:**")
        st.code(", ".join(risk_result["flags"]))

    st.divider()
    st.subheader("🧾 Recent Transactions")

    if "error" in tx_data:
        st.error("Couldn't fetch transactions. Check the wallet address.")
    else:
        txs = tx_data.get("transactions", [])
        if not txs:
            st.warning("No transactions found for this address.")
        else:
            for tx in txs[:5]:
                st.json(tx)
