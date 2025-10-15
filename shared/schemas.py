from pydantic import BaseModel

class OnChainEvent(BaseModel):
    wallet: str
    protocol: str
    apr: float
    contract_age_days: int
    tx_hash: str

class RiskResult(BaseModel):
    wallet: str
    score: int
    flags: list[str]
    rationale: list[str]
    tx_hash: str
