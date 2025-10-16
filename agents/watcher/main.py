import httpx, os
from shared.schemas import OnChainEvent
from fastapi import FastAPI

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
