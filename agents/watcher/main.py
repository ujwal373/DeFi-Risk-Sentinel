import asyncio, httpx, os, uuid, random
from shared.schemas import OnChainEvent
from pydantic import BaseModel
from fastapi import FastAPI


ANALYZER = os.getenv("ANALYZER_URL","http://127.0.0.1:8003")
AGG = os.getenv("AGGREGATOR_URL","http://127.0.0.1:8001")

async def loop_events():
    async with httpx.AsyncClient() as c:
        while True:
            e = OnChainEvent(
                wallet="0xABCDEF1234",
                protocol=random.choice(["Uniswap","Unknown","Custom"]),
                apr=random.choice([12,45,120,300]),
                contract_age_days=random.choice([2,5,10,30]),
                tx_hash="0x"+uuid.uuid4().hex[:16]
            )
            a = await c.post(f"{ANALYZER}/analyze", json=e.model_dump())
            risk = a.json()
            await c.post(f"{AGG}/risk", json=risk)
            print("Event processed:", risk)
            await asyncio.sleep(5)

asyncio.run(loop_events())

app = FastAPI(title="Watcher")

@app.post("/analyze_wallet")
async def analyze_wallet_input(event: OnChainEvent):
    async with httpx.AsyncClient() as client:
        # Send to analyzer
        r = await client.post(f"{ANALYZER}/analyze", json=event.model_dump())
        risk = r.json()
        # Store to aggregator
        await client.post(f"{AGG}/risk", json=risk)
        return {"status": "processed", "risk": risk}
