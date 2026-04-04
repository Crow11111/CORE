import { GoogleGenAI } from "@google/genai";
import dotenv from "dotenv";
dotenv.config();

const ai = new GoogleGenAI({});
async function test() {
  const session = await ai.live.connect({
    model: "gemini-3.1-flash-live-preview",
    config: {},
    callbacks: {
      onmessage: (msg) => {
        console.log("Model response:", JSON.stringify(msg, null, 2));
      }
    }
  });
  console.log("Connected");
  session.send({ clientContent: { turns: [{ role: "user", parts: [{ text: "Hallo Live API!" }] }], turnComplete: true } });
  await new Promise(r => setTimeout(r, 6000));
  session.close();
}
test();
