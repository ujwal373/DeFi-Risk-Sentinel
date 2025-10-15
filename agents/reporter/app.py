from fastapi import FastAPI
from pydantic import BaseModel
import httpx, os

AGG = os.getenv("AGGREGATOR_URL","http://127.0.0.1:8001")
app = FastAPI(title="Reporter")

class ChatQuery(BaseModel):
    cmd: str
    arg: str|None=None

@app.post("/chat")
async def chat(q: ChatQuery):
    if q.cmd == "/risk" and q.arg:
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{AGG}/risk/{q.arg}")
        data = r.json()
        if not data: return {"reply": f"No records for {q.arg} yet."}
        last = data[-1]
        return {"reply": f"Risk {last['score']}/100 | flags: {', '.join(last['flags'])} | tx: {last['tx_hash']}"}
    return {"reply": "Commands: /risk <wallet>"}
