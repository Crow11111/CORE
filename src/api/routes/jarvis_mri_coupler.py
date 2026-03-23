import os
import time
import asyncio
from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from loguru import logger
import httpx

from src.db.multi_view_client import embed_local, ingest_document, search_multi_view, _run_pg_sql
from src.logic_core.crystal_grid_engine import CrystalGridEngine
from src.config.core_state import BARYONIC_DELTA

router = APIRouter()


async def _search_sql_infra(query: str) -> str:
    """Suche in der core_infrastructure Tabelle auf dem VPS (2D-Fakten)."""
    q_clean = query.replace("'", "''").strip()
    if not q_clean:
        return ""

    # Extrahiere Keywords (Worte > 3 Zeichen)
    words = [w for w in q_clean.split() if len(w) > 3]
    if not words:
        words = [q_clean]

    conditions = []
    for w in words:
        conditions.append(f"node_name ILIKE '%{w}%'")
        conditions.append(f"service_name ILIKE '%{w}%'")
        conditions.append(f"CAST(port AS TEXT) = '{w}'")

    where_clause = " OR ".join(conditions)

    sql = f"""
    SELECT node_name, service_name, port, status, purpose
    FROM core_infrastructure
    WHERE {where_clause}
    LIMIT 10;
    """
    logger.debug(f"[JARVIS-MRI] SQL Search: {sql}")
    ok, out = await _run_pg_sql(sql)
    if not ok or not out.strip():
        return ""

    lines = out.strip().split("\n")
    # psql -t -A gibt keine Header/Trenner aus, wenn direkt aufgerufen.
    # Aber _run_pg_sql nutzt psql ohne -t -A standardmäßig (siehe multi_view_client.py _multiview_ssh_config)
    # Halt: search_multi_view überschreibt das. Aber _run_pg_sql nutzt den Standard.

    res = "### CORE-Infrastruktur Fakten (SQL):\n"
    found = False
    for line in lines:
        if "|" in line and "node_name" not in line and "-----" not in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 5:
                node, service, port, status, purpose = parts[:5]
                res += f"- {service}@{node} (Port: {port or 'N/A'}, Status: {status}) - {purpose}\n"
                found = True

    return res if found else ""


def _strip_env(s: str) -> str:
    return (s or "").strip().strip('"').strip("'")


# Zuvor nur OLLAMA_LOCAL_HOST → auf Dreadnought zeigt das oft auf leeres/falsches Ollama,
# während CORE bereits OLLAMA_HOST (z. B. LAN-Pi mit llama3.2:1b) nutzt.
# Reihenfolge: JARVIS_OLLAMA_URL (explizit fürs Plasmoid), OLLAMA_HOST, OLLAMA_LOCAL_HOST.
OLLAMA_API_BASE = (
    _strip_env(os.getenv("JARVIS_OLLAMA_URL"))
    or _strip_env(os.getenv("OLLAMA_HOST"))
    or _strip_env(os.getenv("OLLAMA_LOCAL_HOST"))
    or "http://127.0.0.1:11434"
).rstrip("/")

# Die 4 Dimensionen der Drehscheibe (MRI Coupler Matrix)
MODELS = {
    "core-local-min": {"type": "ollama", "target": os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")},
    "core-local-max": {"type": "ollama", "target": os.getenv("OLLAMA_HEAVY_MODEL", "qwen2.5-coder:7b")},
    "core-api-min": {"type": "gemini", "target": os.getenv("GEMINI_API_MODEL_MIN", "gemini-1.5-flash")},
    "core-api-max": {"type": "gemini", "target": os.getenv("GEMINI_API_MODEL_MAX", "gemini-1.5-pro")},
}

async def _inject_mri_pressure(prompt: str, response_text: str, start_time: float, model_id: str):
    """
    Die Magnetrotationsinstabilität (MRI).
    Das ist NICHT nur Logging. Das ist der Druck-Generator.
    """
    try:
        import hashlib
        ts = time.time()
        latency = ts - start_time

        # 1. Schnelles lokales Embedding (768-dim) für den Druck
        vector = await embed_local(prompt)
        if not vector:
            logger.warning("[JARVIS-MRI] Konnte kein Embedding erzeugen. Druckaufbau bricht hier ab.")
            return

        # 2. Vektor in die lokale Membran rammen (pgvector session_logs)
        h = hashlib.md5(f"{ts}{prompt[:40]}".encode()).hexdigest()[:10]
        doc_id = f"jarvis_mri_{h}"
        document = f"[JARVIS-MRI-IN ({model_id})] {prompt}\n\n[JARVIS-MRI-OUT] {response_text}"

        pressure_factor = (1.0 - BARYONIC_DELTA) + (latency * BARYONIC_DELTA)
        snapped_pressure = CrystalGridEngine.apply_operator_query(pressure_factor)

        await ingest_document(
            document=document,
            doc_id=doc_id,
            source_collection="session_logs",
            metadata={
                "source": "jarvis_mri",
                "model": model_id,
                "latency": latency,
                "pressure": float(snapped_pressure)
            },
        )
        logger.info(f"[JARVIS-MRI] Druck erfolgreich in Membran injiziert. (Pressure: {snapped_pressure:.4f})")

        # 3. ZÜNDUNG DES EVENT-BUS
        try:
            with open("/tmp/mri_zündung.flag", "w") as f:
                f.write(f"{snapped_pressure}")

            from src.daemons.core_event_bus import event_bus_instance
            if event_bus_instance and getattr(event_bus_instance, "_running", False):
                fake_event = {
                    "event": {
                        "data": {
                            "entity_id": "mri.jarvis_zündung",
                            "new_state": {"state": "active", "latency": latency, "pressure": float(snapped_pressure)}
                        }
                    }
                }
                asyncio.create_task(event_bus_instance._handle_event(fake_event))
            else:
                logger.debug("[JARVIS-MRI] Event-Bus nicht aktiv, Zündung wird nur in Membran geschrieben.")
        except Exception as e:
            logger.warning(f"[JARVIS-MRI] Daemon-Trigger fehlgeschlagen: {e}")

    except Exception as e:
        logger.error(f"[JARVIS-MRI] Fehler bei der Druck-Injektion: {e}")


@router.get("/v1/models")
async def get_models():
    """Gibt die 4 Drehscheiben-Modi an Jarvis (KDE) aus."""
    data = []
    for m_id in MODELS.keys():
        data.append({"id": m_id, "object": "model", "owned_by": "omega-core"})
    return JSONResponse(content={"data": data})


@router.post("/v1/chat/completions")
async def jarvis_mri_endpoint(request: Request, background_tasks: BackgroundTasks):
    """Die Drehscheibe (Router) für das KDE Jarvis Plasmoid."""
    payload = await request.json()
    messages = payload.get("messages", [])
    if not messages:
        return JSONResponse({"error": "No messages"}, status_code=400)

    # Letzten User-Prompt extrahieren
    latest_prompt = messages[-1].get("content", "").lower()
    default_model = os.getenv("ATLAS_DEFAULT_MODEL", "core-api-min")
    req_model = payload.get("model", default_model)

    # DUAL-SEARCH (SQL-Fakten + Vektor-Funnel)
    rag_context = ""
    thought_log = ""

    # 1. SQL-Search (2D-Fakten)
    sql_facts = await _search_sql_infra(latest_prompt)
    if sql_facts:
        rag_context += f"\n{sql_facts}\n"
        thought_log += f"[MRI:SQL] Fakten zur Infrastruktur gefunden. "

    # 2. Vector-Search (5D-Vektoren) – Immer für Kontext, außer bei trivialen Prompts
    if len(latest_prompt.split()) > 1:
        try:
            # 768 (Fast) + 3072 (Deep) Funnel
            results = await search_multi_view(latest_prompt, limit=3, use_3072=True)
            if results:
                thought_log += f"[MRI:VECTOR] {len(results)} Dokumente im Funnel (3072 dim) gefunden."
                rag_context += "\n\n### Zusätzlicher CORE-Kontext (Multi-View Vector Funnel):\n"
                for r in results:
                    rag_context += f"- [{r['doc_id']}] {r['document'][:400]}...\n"
        except Exception as e:
            logger.warning(f"[JARVIS-MRI] Vektor-Suche fehlgeschlagen: {e}")

    # Kontext in die erste System-Message injizieren (falls vorhanden)
    system_framing = (
        "Du bist ATLAS, die kognitive Sprachschnittstelle von OMEGA CORE. Du hast Zugriff auf lokale System-Tools und Home Assistant. "
        "WICHTIG: Die Entity-ID für das Licht in der Küche ist 'light.led_kuche'. Rufe bei 'Küche' immer 'light.led_kuche' auf. "
        "Nutze die bereitgestellten Tools, um Aktionen direkt auszuführen, anstatt sie nur vorzuschlagen."
    )
    if rag_context:
        system_framing += "\n\n[HINWEIS: Nutze die folgenden Fakten für deine Antwort!]\n" + rag_context

    system_msg_found = False
    for msg in messages:
        if msg["role"] == "system":
            msg["content"] = system_framing + "\n\n" + msg.get("content", "")
            system_msg_found = True
            break
    if not system_msg_found:
        messages.insert(0, {"role": "system", "content": system_framing})

    # Fallback
    if req_model not in MODELS:
        req_model = "core-local-min"

    config = MODELS[req_model]
    start_time = time.time()

    assistant_reply = ""
    usage_data = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    from src.connectors.local_executor import registry
    schemas = registry.get_schemas()

    try:
        # --- OLLAMA / GEMINI CALLS ---
        if config["type"] == "ollama":
            ollama_tools = [{"type": "function", "function": schema} for schema in schemas]

            async def _call_ollama(msgs):
                ollama_payload = {
                    "model": config["target"],
                    "messages": msgs,
                    "stream": False,
                    "temperature": payload.get("temperature", 0.7),
                    "tools": ollama_tools
                }
                async with httpx.AsyncClient() as client:
                    resp = await client.post(f"{OLLAMA_API_BASE}/api/chat", json=ollama_payload, timeout=300.0)
                    resp.raise_for_status()
                    return resp.json()

            ollama_data = await _call_ollama(messages)
            msg_data = ollama_data.get("message", {})

            # Tool Call Loop
            while msg_data.get("tool_calls"):
                tool_calls = msg_data.get("tool_calls")
                # Assistant msg anfügen
                messages.append(msg_data)

                for tc in tool_calls:
                    func_name = tc["function"]["name"]
                    args = tc["function"].get("arguments", {})
                    logger.info(f"[JARVIS-MRI] Ollama Tool Call: {func_name}({args})")
                    try:
                        result = await registry.execute(func_name, **args)
                    except Exception as e:
                        result = f"Error: {e}"
                    logger.info(f"[JARVIS-MRI] Tool Result: {result}")
                    messages.append({
                        "role": "tool",
                        "content": str(result)
                    })

                # Erneuter Call nach Ausführung
                ollama_data = await _call_ollama(messages)
                msg_data = ollama_data.get("message", {})

            assistant_reply = msg_data.get("content", "")
            usage_data["prompt_tokens"] = ollama_data.get("prompt_eval_count", 0)
            usage_data["completion_tokens"] = ollama_data.get("eval_count", 0)
            usage_data["total_tokens"] = usage_data["prompt_tokens"] + usage_data["completion_tokens"]

        elif config["type"] == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                return JSONResponse({"error": "GEMINI_API_KEY is missing"}, status_code=500)

            gemini_tools = [{"functionDeclarations": schemas}]

            async def _call_gemini(msgs):
                contents = []
                sys_instruct = None

                for m in msgs:
                    role = m["role"]
                    if role == "system":
                        sys_instruct = {"parts": [{"text": m["content"]}]}
                        continue
                    if role == "tool":
                        contents.append({
                            "role": "function",
                            "parts": [{"functionResponse": {"name": m.get("name", "tool"), "response": {"result": m["content"]}}}]
                        })
                        continue

                    # Ollama assistant responses can have tool_calls, mapping to Gemini functionCall
                    if role == "assistant" and m.get("tool_calls"):
                        parts = []
                        if m.get("content"):
                            parts.append({"text": m["content"]})
                        for tc in m["tool_calls"]:
                            parts.append({
                                "functionCall": {
                                    "name": tc["function"]["name"],
                                    "args": tc["function"].get("arguments", {})
                                }
                            })
                        contents.append({"role": "model", "parts": parts})
                        continue

                    gemini_role = "user" if role == "user" else "model"
                    contents.append({
                        "role": gemini_role,
                        "parts": [{"text": m["content"]}]
                    })

                gemini_payload = {
                    "contents": contents,
                    "tools": gemini_tools,
                    "generationConfig": {
                        "temperature": payload.get("temperature", 0.7)
                    }
                }
                if sys_instruct:
                    gemini_payload["systemInstruction"] = sys_instruct

                async with httpx.AsyncClient() as client:
                    resp = await client.post(
                        f"https://generativelanguage.googleapis.com/v1beta/models/{config['target']}:generateContent?key={api_key}",
                        json=gemini_payload,
                        timeout=60.0
                    )
                    resp.raise_for_status()
                    return resp.json()

            gemini_data = await _call_gemini(messages)

            while gemini_data.get("candidates") and gemini_data["candidates"][0]["content"].get("parts", [{}])[0].get("functionCall"):
                parts = gemini_data["candidates"][0]["content"]["parts"]

                # Gemini returns function calls, we format it as an assistant message with tool_calls for our internal message list
                tool_calls_for_msg = []
                for p in parts:
                    if "functionCall" in p:
                        fc = p["functionCall"]
                        tool_calls_for_msg.append({
                            "function": {
                                "name": fc["name"],
                                "arguments": fc.get("args", {})
                            }
                        })

                messages.append({
                    "role": "assistant",
                    "content": parts[0].get("text", "") if "text" in parts[0] else "",
                    "tool_calls": tool_calls_for_msg
                })

                for p in parts:
                    if "functionCall" in p:
                        fc = p["functionCall"]
                        func_name = fc["name"]
                        args = fc.get("args", {})
                        logger.info(f"[JARVIS-MRI] Gemini Tool Call: {func_name}({args})")
                        try:
                            result = await registry.execute(func_name, **args)
                        except Exception as e:
                            result = f"Error: {e}"
                        logger.info(f"[JARVIS-MRI] Tool Result: {result}")
                        messages.append({
                            "role": "tool",
                            "name": func_name,
                            "content": str(result)
                        })

                gemini_data = await _call_gemini(messages)

            try:
                assistant_reply = gemini_data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                assistant_reply = ""
                logger.error(f"[JARVIS-MRI] Gemini parse error: {gemini_data}")

            usage = gemini_data.get("usageMetadata", {})
            usage_data["prompt_tokens"] = usage.get("promptTokenCount", 0)
            usage_data["completion_tokens"] = usage.get("candidatesTokenCount", 0)
            usage_data["total_tokens"] = usage.get("totalTokenCount", 0)

        # Gedanken einbetten, falls vorhanden
        if thought_log:
            assistant_reply = f"<thought>{thought_log}</thought>\n{assistant_reply}"

        # OpenAI-kompatibles Format für Jarvis (Plasmoid) zusammenbauen
        openai_response = {
            "id": f"chatcmpl-jarvis-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": req_model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": assistant_reply
                },
                "finish_reason": "stop"
            }],
            "usage": usage_data
        }

        # Asymmetrischen Druck im Hintergrund aufbauen (MRI Kupplung)
        background_tasks.add_task(_inject_mri_pressure, latest_prompt, assistant_reply, start_time, req_model)

        return JSONResponse(content=openai_response)

    except Exception as e:
        logger.error(f"[JARVIS-MRI] Fehler in der Schicht {req_model}: {e}")
        hint = ""
        if "ollama" in MODELS.get(req_model, {}).get("type", ""):
            hint = (
                f" Ollama-Basis: {OLLAMA_API_BASE}. "
                "Prüfe OLLAMA_HOST / OLLAMA_LOCAL_HOST in .env und ob das Modell "
                f"'{MODELS[req_model]['target']}' auf diesem Host existiert (ollama list)."
            )
        return JSONResponse({"error": str(e) + hint}, status_code=500)
