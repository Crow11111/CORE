# Cursor / VS Code: Deutsche Oberfläche (Workspace)

**Zweck:** Einheitlich deutsche Menüs, Befehle und Standard-Dialoge in Cursor – inkl. Einbindung **über Extensions im Projekt**.

---

## 1. Extension (über „Extensions“ im Editor)

1. **Seitenleiste:** Symbol **Extensions** (oder `Ctrl+Shift+X`).
2. Suche: **German Language Pack for Visual Studio Code**.
3. Herausgeber: **Microsoft** · ID: `MS-CEINTL.vscode-language-pack-de`.
4. **Installieren**.

**Workspace-Hinweis:** Beim Öffnen von OMEGA_CORE fragt Cursor ggf., ob die **empfohlenen Extensions** installiert werden sollen – darin ist das Deutschpaket enthalten (siehe `.vscode/extensions.json`).

---

## 2. Anzeigesprache auf Deutsch stellen

1. `Ctrl+Shift+P` → **Configure Display Language** (oder **Sprache für die Anzeige konfigurieren**).
2. **Deutsch (de)** wählen.
3. Cursor **neu starten**, wenn dazu aufgefordert.

Falls **Deutsch** nicht in der Liste steht: zuerst Schritt 1 (Sprachpaket installieren), dann erneut öffnen.

---

## 3. Grenzen

- **KI-Chat / Composer:** Bleiben produktseitig oft Englisch; das betrifft nicht die IDE-Oberfläche.
- **Drittanbieter-Extensions:** Übersetzen nur, wenn sie Lokalisierung mitliefern.

---

## Verweise

| Artefakt | Pfad |
|----------|------|
| Extension-Empfehlung (Repo) | `.vscode/extensions.json` |
| Agenten-Einstieg | `AGENTS.md` |
