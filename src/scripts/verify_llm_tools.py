import asyncio
import httpx
import json
import sys

async def verify_tool_call():
    url = "http://127.0.0.1:8000/v1/chat/completions"
    
    # We use core-api-min (Gemini) by default as it has reliable tool calling capabilities
    model = "core-api-min" if len(sys.argv) < 2 else sys.argv[1]

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "Schalte das Licht im Büro ein (Domain: light, Service: turn_on, Entity: light.schreibtisch). Mache danach die Systemlautstärke auf 50%."
            }
        ]
    }

    print(f"Sende Request an {url} mit Modell {model}...")
    
    # Needs a long timeout for local LLMs
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            
            print("\n--- RESPONSE ---")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("----------------")
            
            if "choices" in data and len(data["choices"]) > 0:
                print("\nAssistant Reply:")
                print(data["choices"][0]["message"]["content"])
                
                print("\n[SUCCESS] Request erfolgreich ausgeführt. Tool Calling sollte im Server-Log sichtbar sein.")
            else:
                print("\n[FAIL] Ungültiges Response-Format.")
                
    except Exception as e:
        print(f"\n[FAIL] Fehler beim HTTP Request: {e}")
        try:
            print(f"Response war: {resp.text}")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(verify_tool_call())

