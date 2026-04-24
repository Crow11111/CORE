import os
import httpx
import asyncio
import json
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

async def test_gemini_call():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY missing")
        return

    model = "gemini-3.1-pro-preview"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    # Szenario 1: Minimaler Call (wie im Coupler aktuell)
    payload_minimal = {
        "contents": [{"role": "user", "parts": [{"text": "Explain the OMEGA CORE in one sentence."}]}],
        "generationConfig": {
            "temperature": 0.7
        }
    }

    # Szenario 2: Call mit expliziter (korrekter) Thinking Config
    payload_fixed = {
        "contents": [{"role": "user", "parts": [{"text": "Explain the OMEGA CORE in one sentence."}]}],
        "generationConfig": {
            "temperature": 0.7,
            "thinkingConfig": {
                "includeThoughts": True,
                "thinkingLevel": "high"
            }
        }
    }

    async with httpx.AsyncClient() as client:
        print(f"\n--- Testing Scenario 1 (Minimal) ---")
        try:
            resp = await client.post(url, json=payload_minimal, timeout=30.0)
            print(f"Status: {resp.status_code}")
            if resp.status_code != 200:
                print(f"Error Body: {resp.text}")
            else:
                print("Success!")
        except Exception as e:
            print(f"Exception: {e}")

        print(f"\n--- Testing Scenario 2 (Fixed Thinking Config) ---")
        try:
            resp = await client.post(url, json=payload_fixed, timeout=30.0)
            print(f"Status: {resp.status_code}")
            if resp.status_code != 200:
                print(f"Error Body: {resp.text}")
            else:
                print("Success!")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_gemini_call())
