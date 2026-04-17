# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import os
import asyncio
import subprocess
from typing import Optional, List
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from loguru import logger
from pydantic import BaseModel, Field

# CORE-Kontext
from src.logic_core.z_vector_damper import shell_protected, RuntimeVetoException
from src.network.openclaw_client import send_message_to_agent_async, is_configured as is_oc_configured
from src.ai.model_registry import (
    GEMINI_HEAVY,
    GEMINI_FLASH,
    GEMINI_TRIAGE, 
    GEMINI_FLASH_LITE,
    GEMMA_TRIAGE,
    GEMMA_REASONING,
    OLLAMA_MODEL,
    OLLAMA_HOST,
    OLLAMA_LOCAL
)

load_dotenv("/OMEGA_CORE/.env")

class TriageResult(BaseModel):
    intent: str = Field(description="The primary intent. Options: 'home_control', 'omega_work', 'chat', 'unknown'")
    skill_required: str = Field(description="Required skill: 'simple_coder', 'heavy_reasoner', 'wiki_expert', 'stupid_coder'", default="stupid_coder")
    target_entity: str = Field(description="If 'home_control', extract the target HA entity or domain, otherwise empty.", default="")
    action: str = Field(description="If 'home_control', the action to perform (e.g. turn_on, turn_off), otherwise empty.", default="")
    thought: Optional[str] = Field(None, description="Internal reasoning buffer to prevent thought_signature errors")

class ResilientLLMInterface:
    """
    Skill-basiertes Routing & Resilienz-Layer.
    """
    def __init__(self, ollama_model: str, ollama_base_url: str, local_fallback_url: Optional[str] = None):
        self.scout_llm = ChatOllama(model=ollama_model, base_url=ollama_base_url, temperature=0.7)
        self.local_llm = None
        if local_fallback_url:
            from src.ai.model_registry import OLLAMA_HEAVY
            self.local_llm = ChatOllama(model=OLLAMA_HEAVY, base_url=local_fallback_url, temperature=0.7)
            
        # Cloud Workers
        self.cloud_heavy = ChatGoogleGenerativeAI(model=GEMINI_HEAVY, temperature=0.3)
        self.cloud_flash = ChatGoogleGenerativeAI(model=GEMINI_FLASH, temperature=0.4)
        self.cloud_lite = ChatGoogleGenerativeAI(model=GEMINI_FLASH_LITE, temperature=0.1)

    async def ainvoke_by_skill(self, messages: List[BaseMessage], skill: str = "stupid_coder") -> str:
        """
        Wählt den Worker basierend auf dem benötigten Skill.
        """
        logger.info(f"[LLM-ORCHESTRATOR] Routing task to skill: {skill}")
        
        # 1. Wiki Expert (Claude Code Local)
        if skill == "wiki_expert":
            return await self._call_wiki_expert(messages)

        # 2. Heavy Reasoner (Gemini 3.1 Pro)
        if skill == "heavy_reasoner":
            try:
                res = await self.cloud_heavy.ainvoke(messages)
                return res.content
            except Exception as e:
                logger.error(f"Heavy Reasoner failed, falling back: {e}")
                skill = "simple_coder" # Auto-Downgrade

        # 3. Simple Coder (Gemini 3.1 Flash Lite - Tier 2)
        if skill == "simple_coder":
            try:
                res = await self.cloud_lite.ainvoke(messages)
                return res.content
            except Exception as e:
                logger.error(f"Simple Coder failed, falling back: {e}")
                skill = "stupid_coder"

        # 4. Stupid Coder (Gemma 4 / Ollama Local)
        if skill == "stupid_coder":
            # Versuche Local (Dreadnought) -> Scout -> VPS
            if self.local_llm:
                try: return (await self.local_llm.ainvoke(messages)).content
                except: pass
            try: return (await self.scout_llm.ainvoke(messages)).content
            except: pass
            
        return "FEHLER: Kein passender Worker für Skill '" + skill + "' gefunden."

    async def _call_wiki_expert(self, messages: List[BaseMessage]) -> str:
        """Ruft das lokale OMEGA-WIKI via Claude Code auf."""
        prompt = messages[-1].content
        logger.info(f"[WIKI-EXPERT] Searching OMEGA_WIKI for: {prompt[:50]}...")
        try:
            # Karpathy-Style: Claude Code im Wiki-Verzeichnis ausführen
            cmd = ["claude", "-p", f"Nutze das OMEGA_WIKI um folgende Frage zu beantworten: {prompt}"]
            result = subprocess.run(cmd, cwd="/home/mth/OMEGA_WIKI", capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                return result.stdout
            return f"Wiki-Fehler: {result.stderr}"
        except Exception as e:
            return f"Wiki-Exception: {e}"

class LLMInterface:
    def __init__(self):
        scout_url = OLLAMA_HOST
        scout_model = OLLAMA_MODEL
        local_url = OLLAMA_LOCAL
        local_model = GEMMA_TRIAGE

        # Triage Engines
        self.triage_local = ChatOllama(model=local_model, base_url=local_url, temperature=0.1).with_structured_output(TriageResult)
        self.triage_cloud = ChatGoogleGenerativeAI(model=GEMINI_FLASH_LITE, temperature=0.1).with_structured_output(TriageResult)

        self.worker_pool = ResilientLLMInterface(
            ollama_model=scout_model,
            ollama_base_url=scout_url,
            local_fallback_url=local_url
        )

    @shell_protected(estimated_tokens_per_call=1000)
    def run_triage(self, user_input: str) -> TriageResult:
        """Semantische Skill-Triage."""
        logger.info(f"Semantische Triage für: '{user_input}'")
        
        # --- LEXICAL FAST PATH (HOME CONTROL) ---
        fast_path = {
            "bad": "light.bad", "küche": "light.led_kuche", "flur": "light.flur",
            "deckenlampe": "light.deckenlampe", "stehlampe": "light.stehlampe"
        }
        for k, v in fast_path.items():
            if k in user_input.lower():
                action = "turn_off" if "aus" in user_input.lower() else "turn_on"
                return TriageResult(intent="home_control", skill_required="stupid_coder", target_entity=v, action=action)

        # --- LLM TRIAGE ---
        prompt = (
            "Du bist der OMEGA-Orchestrator. Analysiere die Anfrage und entscheide, welcher Worker-Skill benötigt wird.\n\n"
            "INTENTS:\n"
            "- 'home_control': Smart Home Befehle (Licht, Heizung).\n"
            "- 'omega_work': Produktive Arbeit am OMEGA System, Architektur, Code, Logik.\n"
            "- 'chat': Smalltalk oder allgemeine Fragen.\n\n"
            "SKILLS:\n"
            "- 'wiki_expert': Für tiefes OMEGA-Wissen, Axiome, Theorie (nutzt lokales Wiki).\n"
            "- 'heavy_reasoner': Für komplexe Code-Änderungen oder Architektur-Entscheidungen (Gemini 3.1 Pro).\n"
            "- 'simple_coder': Für Standard-Coding oder einfache Logik (Gemini 3.1 Flash Lite).\n"
            "- 'stupid_coder': Für repetitive Aufgaben oder einfache Home-Befehle (Gemma 4 Lokal).\n\n"
            f"Anfrage: '{user_input}'"
        )

        try:
            # 1. Versuch: Cloud (Tier 2)
            result = self.triage_cloud.invoke([SystemMessage(content=prompt)])
            if result and result.intent != "unknown": return result
        except:
            pass

        try:
            # 2. Versuch: Lokal (Dreadnought)
            return self.triage_local.invoke([SystemMessage(content=prompt)])
        except Exception as e:
            logger.error(f"Triage komplett fehlgeschlagen: {e}")
            return TriageResult(intent="unknown", skill_required="stupid_coder")

    async def invoke_heavy_reasoning(self, system_prompt: str, user_input: str) -> str:
        """Haupt-Einstiegspunkt für produktive Arbeit."""
        # 1. Triage
        triage = self.run_triage(user_input)
        
        # 2. Worker auswählen
        messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_input)]
        return await self.worker_pool.ainvoke_by_skill(messages, skill=triage.skill_required)

# Singleton
core_llm = LLMInterface()
