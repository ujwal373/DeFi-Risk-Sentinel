from uagents import Agent, Context, Protocol
import httpx, os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

AGG = os.getenv("AGGREGATOR_URL", "http://127.0.0.1:8001")
REP = os.getenv("REPORTER_URL", "http://127.0.0.1:8002")
LLM_API = os.getenv("LLM_API", "http://localhost:11434/api/generate")  # local model default

agent = Agent(name="reporter_agent")
protocol = Protocol(name="chat-protocol")

class ChatInput(BaseModel):
    message: str

@protocol.on_message(model=ChatInput)
async def handle_chat(ctx: Context, msg: ChatInput):
    text = msg.message.strip()

    if text.startswith("/risk"):
        parts = text.split()
        if len(parts) != 2:
            await ctx.send(ctx.sender, "Usage: /risk <wallet>")
            return
        wallet = parts[1]
        async with httpx.AsyncClient() as c:
            r = await c.post(f"{REP}/chat", json={"cmd":"/risk", "arg":wallet})
        await ctx.send(ctx.sender, r.json().get("reply", "Error"))

    elif text.startswith("/explain"):
        parts = text.split()
        if len(parts) != 2:
            await ctx.send(ctx.sender, "Usage: /explain <tx_hash>")
            return
        tx = parts[1]
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{REP}/explain/{tx}")
        await ctx.send(ctx.sender, r.json().get("reply", "Error"))

    elif text.startswith("/why"):
        parts = text.split()
        if len(parts) != 2:
            await ctx.send(ctx.sender, "Usage: /why <wallet>")
            return
        wallet = parts[1]

        # Step 1: Get raw risk data
        async with httpx.AsyncClient() as c:
            risk_resp = await c.get(f"{REP}/explain/{wallet}")
        result = risk_resp.json()
        reasoning_prompt = f"""
        A wallet risk analysis was conducted with the following flags and reasons:
        {result.get('reply', '')}
        
        Based on the above, explain in simple terms why this wallet might be risky.
        Suggest what actions the user could take.
        """

        # Step 2: Ask the LLM
        async with httpx.AsyncClient() as c:
            llm_resp = await c.post(LLM_API, json={"prompt": reasoning_prompt, "stream": False})
        output = llm_resp.json()
        reply = output.get("response") or output.get("text", "No explanation generated.")

        await ctx.send(ctx.sender, reply)

    else:
        await ctx.send(ctx.sender, "Unknown command. Use /risk, /explain or /why.")

agent.include(protocol)

if __name__ == "__main__":
    agent.run()
