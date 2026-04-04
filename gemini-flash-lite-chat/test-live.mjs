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
      }
    });
    console.log("Connected. Sending text...");
    session.sendClientContent({ turns: [{ role: "user", parts: [{ text: "Hello, what is 1+1?" }] }] });
    
    setTimeout(() => {
        console.log("Disconnecting.");
        session.close();
        process.exit(0);
    }, 5000);
  } catch (e) {
    console.error("Error:", e);
  }
}
run();
