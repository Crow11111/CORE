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
        if (msg.serverContent && msg.serverContent.modelTurn) {
          const parts = msg.serverContent.modelTurn.parts;
          console.log("Model response:", JSON.stringify(parts, null, 2));
        }
      },
      onerror: (err) => console.error("Error:", err),
    }
  });
  console.log("Connected");

  try {
    console.log("Sending sendClientContent...");
    session.sendClientContent({ turns: "Hallo, kannst du mich hören? Bitte antworte kurz auf Deutsch.", turnComplete: true });
  } catch(e) {
    console.error("send error:", e.message);
  }

  await new Promise(r => setTimeout(r, 6000));
  session.close();
}
test();