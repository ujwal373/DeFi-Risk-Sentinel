from fastapi import FastAPI
from shared.schemas import RiskResult

store: dict[str, list[RiskResult]] = {}
tx_index: dict[str, RiskResult] = {}

app = FastAPI(title="Aggregator")

@app.get("/risk/{wallet}")
def get_risk(wallet: str):
    return store.get(wallet.lower(), [])

@app.get("/tx/{tx_hash}")
def get_tx(tx_hash: str):
    return tx_index.get(tx_hash, None)

@app.post("/risk")
def add_risk(r: RiskResult):
    wl = r.wallet.lower()
    store.setdefault(wl, []).append(r)
    tx_index[r.tx_hash] = r
    return {"ok": True, "count": len(store[wl])}
