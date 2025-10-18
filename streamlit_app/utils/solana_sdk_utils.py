# streamlit_app/utils/solana_utils.py

from solana.rpc.api import Client
from solana.publickey import PublicKey
from solana.rpc.types import TokenAccountOpts
import os

# Default RPC (you can override via environment variable)
SOLANA_RPC = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
client = Client(SOLANA_RPC)

def is_solana_address(address: str) -> bool:
    """Validate if the input is a Solana address (length 32-44 and base58)"""
    try:
        PublicKey(address)
        return True
    except Exception:
        return False

def fetch_recent_transactions(address: str, limit: int = 10):
    """Fetch recent transactions for a Solana wallet address"""
    try:
        pubkey = PublicKey(address)
        sigs_resp = client.get_signatures_for_address(pubkey, limit=limit)

        if not sigs_resp["result"]:
            return {"error": "No transactions found"}

        tx_summaries = []

        for sig in sigs_resp["result"]:
            tx_sig = sig["signature"]
            tx_detail = client.get_transaction(tx_sig)

            if tx_detail.get("result"):
                meta = tx_detail["result"]["meta"]
                tx_info = tx_detail["result"]["transaction"]["message"]

                summary = {
                    "signature": tx_sig,
                    "slot": sig.get("slot"),
                    "err": meta.get("err"),
                    "post_balances": meta.get("postBalances"),
                    "instructions": len(tx_info.get("instructions", []))
                }
                tx_summaries.append(summary)

        return {
            "address": address,
            "tx_count": len(tx_summaries),
            "transactions": tx_summaries
        }

    except Exception as e:
        return {"error": str(e)}
