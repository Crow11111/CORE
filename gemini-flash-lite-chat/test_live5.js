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
        } else {
            console.log("Other msg:", JSON.stringify(msg, null, 2));
        }
      },
      onerror: (err) => console.error("Error:", err),
    }
  });
  console.log("Connected");

  try {
    session.send({ clientContent: { turns: [{ role: "user", parts: [{ text: "Hallo Live API!" }] }], turnComplete: true } });
  } catch(e) {
      try {
        session.sendClientContent({ turns: [{ role: "user", parts: [{ text: "Hallo, dies ist ein Test mit role." }] }], turnComplete: true });
      } catch(e2) {}
  }

  await new Promise(r => setTimeout(r, 6000));
  session.close();
}
test();