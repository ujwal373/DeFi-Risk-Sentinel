from fastapi import FastAPI
from pydantic import BaseModel
import httpx, os

AGG = os.getenv("AGGREGATOR_URL","http://127.0.0.1:8001")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL","gpt-4o-mini")

app = FastAPI(title="Reporter")

class ChatQuery(BaseModel):
    cmd: str
    arg: str|None=None

async def get_risk_from_tx(tx_hash: str):
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{AGG}/tx/{tx_hash}")
        if r.status_code == 200:
            return r.json()
    return None

@app.post("/chat")
async def chat(q: ChatQuery):
    if q.cmd == "/risk" and q.arg:
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{AGG}/risk/{q.arg}")
        data = r.json()
        if not data: return {"reply": f"No records for {q.arg} yet."}
        last = data[-1]
        return {"reply": f"Risk {last['score']}/100 | flags: {', '.join(last['flags'])} | tx: {last['tx_hash']}"}
    if q.cmd == "/explain" and q.arg:
        return await explain_tx(q.arg)
    return {"reply": "Commands: /risk <wallet>, /explain <tx_hash>"}

@app.get("/explain/{tx_hash}")
async def explain_tx(tx_hash: str):
    risk = await get_risk_from_tx(tx_hash)
    if not risk:
        return {"reply": f"Tx {tx_hash} not found."}
    
    base = f"Tx {tx_hash}: Risk {risk['score']}/100. Flags: {', '.join(risk['flags'])}. Because: {', '.join(risk['rationale'])}."
    
    if not OPENAI_API_KEY:
        return {"reply": base + " (LLM disabled)"}

    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        prompt = (
            f"This transaction has a risk score of {risk['score']}/100.\n"
            f"Flags: {', '.join(risk['flags'])}\n"
            f"Rationale: {', '.join(risk['rationale'])}\n"
            "Explain the risk in simple terms and recommend what a DeFi user should do (no financial advice)."
        )
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return {"reply": response.choices[0].message.content.strip()}
    except Exception as e:
        return {"reply": base + f" (LLM error: {e})"}

