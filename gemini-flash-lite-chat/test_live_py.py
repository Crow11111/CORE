import os
import asyncio
from google import genai

async def main():
    client = genai.Client()
    async with client.aio.live.connect(model='gemini-3.1-flash-live-preview', config={"response_modalities": ["TEXT"]}) as session:
        print("connected")
        await session.send_realtime_input(text="Hallo, antworten Sie auf diesen Text mit OK.")
        async for message in session.receive():
            if message.server_content is not None:
                print(message.server_content.model_turn.parts[0].text)
            else:
                print(message)

if __name__ == "__main__":
    asyncio.run(main())
