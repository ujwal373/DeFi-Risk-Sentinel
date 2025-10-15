from fastapi import FastAPI
from shared.schemas import OnChainEvent, RiskResult

app = FastAPI(title="Analyzer")

@app.post("/analyze", response_model=RiskResult)
def analyze(e: OnChainEvent):
    flags, why, score = [], [], 0
    if e.apr > 100:
        flags.append("suspicious_yield"); why.append("APR>100")
        score += 40
    if e.contract_age_days < 7:
        flags.append("young_contract"); why.append("age<7d")
        score += 30
    if e.protocol.lower() in {"unknown","custom"}:
        flags.append("unverified_protocol"); why.append("no registry")
        score += 20
    score = min(100, max(0, score))
    return RiskResult(wallet=e.wallet, score=score, flags=flags, rationale=why, tx_hash=e.tx_hash)
