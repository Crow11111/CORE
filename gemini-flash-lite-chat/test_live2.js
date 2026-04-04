import { GoogleGenAI } from "@google/genai";
import dotenv from "dotenv";
dotenv.config();

const ai = new GoogleGenAI({});
async function test() {
  const session = await ai.live.connect({ model: "gemini-3.1-flash-live-preview", config: {} });
  console.log("Connected");
  try {
    session.sendRealtimeInput({ text: "Hello Live API!" });
    console.log("sendRealtimeInput({ text }) succeeded");
  } catch(e) {
    console.error("sendRealtimeInput({ text }) failed:", e.message);
  }
  
  try {
    session.sendRealtimeInput([{ text: "Hello Live API!" }]);
    console.log("sendRealtimeInput([{ text }]) succeeded");
  } catch(e) {
    console.error("sendRealtimeInput([{ text }]) failed:", e.message);
  }
  
  try {
    session.sendClientContent({ turns: "Hello Live API!" });
    console.log("sendClientContent({ turns }) succeeded");
  } catch(e) {
    console.error("sendClientContent({ turns }) failed:", e.message);
  }

  session.close();
}
test();
