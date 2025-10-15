from fastapi import FastAPI
from shared.schemas import RiskResult
store: dict[str, list[RiskResult]] = {}
app = FastAPI(title="Aggregator")

@app.get("/risk/{wallet}")
def get_risk(wallet: str):
    return store.get(wallet.lower(), [])

@app.post("/risk")
def add_risk(r: RiskResult):
    wl = r.wallet.lower()
    store.setdefault(wl, []).append(r)
    return {"ok": True, "count": len(store[wl])}
