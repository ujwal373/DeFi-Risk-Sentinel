# streamlit_app/utils/risk_engine.py

def compute_solana_risk(tx_data):
    if isinstance(tx_data, dict) and "error" in tx_data:
        return {
            "risk_score": 90,
            "reason": "Address invalid or no transactions found.",
            "flags": ["invalid_address"]
        }

    txs = tx_data if isinstance(tx_data, list) else []

    flags = []
    risk_score = 0

    if len(txs) > 10:
        flags.append("high_activity")
        risk_score += 20

    for tx in txs:
        if tx.get("type") == "Unknown":
            flags.append("unknown_type")
            risk_score += 10

        if tx.get("tokenTransfers"):
            flags.append("token_transfer_detected")
            risk_score += 15

    risk_score = min(risk_score, 100)

    return {
        "risk_score": risk_score,
        "reason": "Heuristic-based Solana risk assessment",
        "flags": list(set(flags))
    }
