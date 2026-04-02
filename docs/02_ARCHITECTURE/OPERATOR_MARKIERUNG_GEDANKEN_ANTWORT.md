# Gedanken vs. Antwort: Zwei getrennte Ebenen

## 1. Google Gemini API (strukturell — das ist der „echte“ Anker)

Cursor, AI Studio oder jedes eigene Tool können **nicht** unsere `<<<GEDANKEN>>>`-Tags parsen, wenn die Antwort **von der Gemini REST API** kommt. Dort liefern **Thinking-Modelle** die Trennung **im JSON**, nicht als Freitext-Markup.

**Offizielle Mechanik (Gemini API „Thinking“):**

- Request: je nach Modell z. B. **`thinkingConfig`** mit **`includeThoughts: true`** (und ggf. **`thinkingBudget`** für 2.5 Pro/Flash).
- Response: **`candidates[0].content.parts`** — jedes Part hat u. a. ein Feld **`thought`** (boolean):
  - **`thought: true`** → interne Gedanken/Zwischenschritte (Kurzfassungen)
  - **`thought: false`** → eigentliche Antwort für den Nutzer

**Parsing (logisch):** über alle `parts` iterieren; wenn `part.thought`, in UI-Bereich „Thoughts“; sonst in „Antwort“.

**Doku:** [Gemini API – Thinking](https://ai.google.dev/gemini-api/docs/thinking) (Google AI for Developers).

**Hinweis:** Was **Cursor** in der IDE als „Thought for 2s“ zeigt, ist **Cursor-eigen** (lokale Kette); das ist **nicht** automatisch dasselbe Feld wie `includeThoughts` in der **Google**-Antwort. Wer Google-Thoughts separat will, muss die **API-Antwort** so auswerten wie oben.

---

## 2. CORE-Operator-Tags (`<<<GEDANKEN>>>` / `<<<ANTWORT>>>`) — manuell, für dich und das Board

Das ist **unser** Konventionssystem für **deine** Eingaben und Transkripte (Health Board, Chats mit Operator-Kontext). **Kein** Google-Standard. **Kein** Ersatz für `includeThoughts` in der Gemini-API.

| Block | Öffnen | Schließen | Bedeutung |
|-------|--------|-----------|-----------|
| Operator-Gedanken | `<<<GEDANKEN>>>` | `<<</GEDANKEN>>>` | Deine Überlegung — keine ausführbare Direktive für die KI. |
| Direktive / Antwort | `<<<ANTWORT>>>` | `<<</ANTWORT>>>` | So wird es gemacht — messbar, ausführbar. |
| Kurz | `[G]` | `[A]` | Ein Satz Gedanke vs. eine Satz Direktive. |

---

## 3. Wo die Modelle pro Dienst eingetragen sind (faktisch)

| Dienst | Quelle im Repo |
|--------|----------------|
| Zentrale IDs + Rollen | `src/ai/model_registry.py` (liest `.env`) |
| Tabelle + Erklärung | `docs/02_ARCHITECTURE/AI_MODEL_CAPABILITIES.md` |
| Diktat STT (Pro vs. Live-Flash) | `GEMINI_DICTATE_STT_MODEL`, `GEMINI_DICTATE_STT_LIVE_MODEL`; Route `/api/dictate?mode=live` |
| Embeddings / RAG | `GEMINI_EMBED_MODEL`, Rolle `embedding` |
| TTS | `GEMINI_TTS_MODEL` |

---

**Kurz:** Für **Google-getrennte Thoughts** → API **`includeThoughts` + `parts[].thought`**. Für **deine Texte im Board** → **`<<<GEDANKEN>>>` / `<<<ANTWORT>>>`**. Beides parallel erlaubt, aber nicht verwechseln.


[LEGACY_UNAUDITED]
