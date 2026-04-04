import { GoogleGenAI } from '@google/genai';
const ai = new GoogleGenAI({ apiKey: "test" });
try {
  let session = new ai.live.Session({ send: msg => console.log(msg) }, ai.apiClient);
  session.sendClientContent({ turns: [{ role: "user", parts: [{ text: "hi" }] }] });
} catch (e) {
  console.log("Error:", e);
}
