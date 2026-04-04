import { GoogleGenAI } from "@google/genai";
const ai = new GoogleGenAI({});
const session = ai.live.connect({ model: "gemini-3.1-flash-live-preview" });
// Check types
const valid1: Parameters<typeof session.then extends (onfulfilled: (value: infer V) => any) => any ? (V extends { sendRealtimeInput: infer F } ? F : never) : never> = undefined as any;
