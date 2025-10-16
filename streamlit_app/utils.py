import httpx, os
WATCHER = os.getenv("WATCHER_URL", "http://127.0.0.1:8000")
AGG = os.getenv("AGGREGATOR_URL", "http://127.0.0.1:8001")
REP = os.getenv("REPORTER_URL", "http://127.0.0.1:8002")

def get_risk(wallet):
    try:
        r = httpx.get(f"{AGG}/risk/{wallet}")
        return r.json()
    except:
        return []

def explain_tx(tx_hash):
    try:
        r = httpx.get(f"{REP}/explain/{tx_hash}")
        return r.json().get("reply")
    except:
        return "Error explaining tx"
