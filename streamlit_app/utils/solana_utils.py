import os, httpx
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("HELIUS_API_KEY")
BASE_URL = "https://api.helius.xyz/v0"

async def fetch_solana_transactions(wallet_address):
    url = f"{BASE_URL}/addresses/{wallet_address}/transactions?api-key={API_KEY}&limit=5"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        if r.status_code == 200:
            return r.json()
        else:
            return {"error": f"Failed to fetch transactions: {r.status_code}"}
