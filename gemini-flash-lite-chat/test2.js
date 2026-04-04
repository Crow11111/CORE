const { GoogleGenAI } = require('@google/genai');
const ai = new GoogleGenAI({ apiKey: "test" });
try {
  const session = ai.live.createSession ? ai.live.createSession() : new (ai.live.Session || require('@google/genai').Session)({ send: msg => console.log(msg) }, ai.apiClient);
  session.sendClientContent({ turns: [{ role: "user", parts: [{ text: "hi" }] }] });
} catch (e) {
  console.log("Error:", e);
}
