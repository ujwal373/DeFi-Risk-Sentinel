import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import explain_tx

st.title("Transaction Explainer")
tx = st.text_input("Enter transaction hash")

if st.button("Explain"):
    if tx:
        with st.spinner("Thinking..."):
            msg = explain_tx(tx)
        st.success(msg)
    else:
        st.warning("Enter a transaction hash.")
