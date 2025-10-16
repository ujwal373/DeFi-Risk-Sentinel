import httpx, os
from shared.schemas import OnChainEvent
from fastapi import FastAPI
from agents.watcher.utils_rpc import get_latest_tx, get_contract_age
from shared.schemas import OnChainEvent

ANALYZER = os.getenv("ANALYZER_URL", "http://127.0.0.1:8003")
AGG = os.getenv("AGGREGATOR_URL", "http://127.0.0.1:8001")

app = FastAPI(title="Watcher")

@app.post("/analyze_wallet")
async def analyze_wallet_input(event: OnChainEvent):
    async with httpx.AsyncClient() as client:
        # Analyze the event
        r = await client.post(f"{ANALYZER}/analyze", json=event.model_dump())
        risk = r.json()
        # Store result
        await client.post(f"{AGG}/risk", json=risk)
        return {"status": "processed", "risk": risk}

@app.get("/analyze_realtime/{wallet}")
async def analyze_realtime(wallet: str):
    tx = get_latest_tx(wallet)
    if not tx:
        return {"error": "No recent tx found for this wallet."}

    # Extract simulated fields from real tx (you'll improve this later)
    contract_age = get_contract_age(tx['to']) if tx['to'] else 0
    event = OnChainEvent(
        wallet=wallet,
        protocol="Unknown",  # parse from tx input later
        apr=125.0,  # simulated for now
        contract_age_days=contract_age,
        tx_hash=tx['hash'].hex()
    )

    async with httpx.AsyncClient() as client:
        r = await client.post(f"{ANALYZER}/analyze", json=event.model_dump())
        risk = r.json()
        await client.post(f"{AGG}/risk", json=risk)
        return {"status": "processed", "tx_hash": tx['hash'].hex(), "risk": risk}
