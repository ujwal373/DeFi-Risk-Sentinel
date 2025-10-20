from uagents import Agent, Context, Protocol
import httpx, os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

AGG = os.getenv("AGGREGATOR_URL", "http://127.0.0.1:8001")
REP = os.getenv("REPORTER_URL", "http://127.0.0.1:8002")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

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

        # Step 1: Fetch risk explanation from reporter
        async with httpx.AsyncClient() as c:
            resp = await c.get(f"{REP}/explain/{wallet}")
        base_reasoning = resp.json().get("reply", "No data")

        # Step 2: Compose prompt for OpenAI
        openai_payload = {
            "model": "gpt-3.5-turbo",  # or "gpt-4" if needed
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert DeFi risk analyst explaining risks to a beginner user in simple terms."
                },
                {
                    "role": "user",
                    "content": f"""Given this wallet risk report:\n{base_reasoning}\n\nExplain what makes this wallet risky. Use simple language, suggest actions if needed."""
                }
            ]
        }

        headers = {
            "Authorization": f"Bearer {OPENAI_KEY}",
            "Content-Type": "application/json"
        }

        # Step 3: Call OpenAI API
        async with httpx.AsyncClient() as client:
            response = await client.post("https://api.openai.com/v1/chat/completions", json=openai_payload, headers=headers)
        reply = response.json().get("choices", [{}])[0].get("message", {}).get("content", "Error processing response")

        await ctx.send(ctx.sender, reply)

    else:
        await ctx.send(ctx.sender, "Unknown command. Use /risk, /explain or /why.")

agent.include(protocol)

if __name__ == "__main__":
    agent.run()
