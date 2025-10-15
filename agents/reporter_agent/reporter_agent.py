from uagents import Agent, Context, Protocol
import httpx

AGG = "http://127.0.0.1:8001"
REP = "http://127.0.0.1:8002"

agent = Agent(name="reporter_agent")

protocol = Protocol(name="chat-protocol")

from pydantic import BaseModel

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

    else:
        await ctx.send(ctx.sender, "Unknown command. Use /risk or /explain")


agent.include(protocol)

if __name__ == "__main__":
    agent.run()
