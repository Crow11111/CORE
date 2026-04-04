import { GoogleGenAI } from '@google/genai';
import dotenv from 'dotenv';
dotenv.config();
const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
async function run() {
  try {
    const session = await ai.live.connect({
      model: "gemini-3.1-flash-live-preview",
      config: {
        responseModalities: ["AUDIO"]
      },
      callbacks: {
        onopen: () => {
            console.log("Opened");
            session.sendClientContent({ turns: [{ role: "user", parts: [{ text: "Hello, what is 1+1?" }] }] });
        },
        onmessage: (msg) => console.log("Message:", JSON.stringify(msg).slice(0, 100)),
        onerror: (e) => console.error("WS Error:", e),
        onclose: () => console.log("Closed")
      }
    });
  } catch (e) {
    console.error("Error:", e);
  }
}
run();
