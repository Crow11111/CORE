import { GoogleGenAI } from '@google/genai';
import dotenv from 'dotenv';
dotenv.config();
const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
async function run() {
  let sessionObj;
  try {
    const session = await ai.live.connect({
      model: "gemini-3.1-flash-live-preview",
      config: {
        responseModalities: ["AUDIO"]
      },
      callbacks: {
        onopen: () => {
            console.log("Opened");
            // we will send after resolving
        },
        onmessage: (msg) => console.log("Message received."),
        onerror: (e) => console.error("WS Error:", e),
        onclose: () => { console.log("Closed"); process.exit(0); }
      }
    });
    console.log("Session connected. Sending...");
    session.sendClientContent({ turns: [{ role: "user", parts: [{ text: "Hello, what is 1+1?" }] }] });
  } catch (e) {
    console.error("Error:", e);
  }
}
run();
