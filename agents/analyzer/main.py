from fastapi import FastAPI
from shared.schemas import OnChainEvent, RiskResult
from .rules import load_rules, evaluate

app = FastAPI(title="Analyzer")
RULESET = load_rules()

@app.post("/analyze", response_model=RiskResult)
def analyze(e: OnChainEvent):
    ev = e.model_dump()
    flags, why, score = evaluate(ev, RULESET)
    return RiskResult(wallet=e.wallet, score=score, flags=flags, rationale=why, tx_hash=e.tx_hash)

@app.get("/health")
def health():
    return {"ok": True, "rules": len(RULESET.get("rules", []))}
