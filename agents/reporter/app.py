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
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{AGG}/tx/{tx_hash}")
    if r.status_code != 200 or r.json() is None:
        return {"reply": f"Tx {tx_hash} not found."}
    risk = r.json()
    base = f"Tx {tx_hash}: Risk {risk['score']}/100. Flags: {', '.join(risk['flags'])}. Because: {', '.join(risk['rationale'])}."
    if not OPENAI_API_KEY:
        return {"reply": base + " (LLM disabled)"}
    # Optional LLM rationale
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        prompt = (
          "Explain the following DeFi risk assessment for a non-expert.\n"
          f"Wallet: {risk['wallet']}\n"
          f"Score: {risk['score']}\n"
          f"Flags: {risk['flags']}\n"
          f"Rationale: {risk['rationale']}\n"
          "Advise simple next steps (read-only, no financial advice)."
        )
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role":"user","content": prompt}],
            temperature=0.2,
        )
        return {"reply": resp.choices[0].message.content.strip()}
    except Exception as e:
        return {"reply": base + f" (LLM error: {e})"}
