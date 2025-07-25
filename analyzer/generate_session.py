import asyncio
from pyrogram import Client
import os
from dotenv import load_dotenv

load_dotenv()

async def generate_session():
    api_id = int(os.getenv('API_ID'))
    api_hash = os.getenv('API_HASH')
    
    async with Client("temp_session", api_id=api_id, api_hash=api_hash) as app:
        print("Session string:")
        print(await app.export_session_string())

if __name__ == "__main__":
    asyncio.run(generate_session())
