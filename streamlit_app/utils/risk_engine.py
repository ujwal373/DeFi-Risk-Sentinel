# streamlit_app/utils/risk_engine.py

def compute_solana_risk(tx_data: dict) -> dict:
    if "error" in tx_data:
        return {
            "risk_score": 90,
            "flags": ["invalid_address"],
            "reason": "Address invalid or no transactions found."
        }

    txs = tx_data.get("transactions", [])
    flags = []
    score = 30  # start with a base of 30/100

    if len(txs) == 0:
        score = 95
        flags.append("empty_history")
        reason = "No transaction history found."
    else:
        if len(txs) < 3:
            score += 20
            flags.append("low_activity")

        for tx in txs:
            if tx.get("err") is not None:
                score += 20
                flags.append("tx_error")

            if tx.get("instructions", 0) > 10:
                score += 10
                flags.append("high_instruction_tx")

            # Optional: Check suspiciously large balance change
            post_bal = tx.get("post_balances", [])
            if post_bal and len(post_bal) >= 2:
                delta = abs(post_bal[0] - post_bal[1])
                if delta > 1_000_000_000:  # > 1 SOL
                    score += 15
                    flags.append("large_balance_change")

        # Normalize score
        score = min(score, 100)
        reason = "Flags triggered: " + ", ".join(flags) if flags else "No major risk indicators."

    return {
        "risk_score": score,
        "flags": flags,
        "reason": reason
    }
