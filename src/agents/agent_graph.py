# -*- coding: utf-8 -*-
"""
OMEGA AGENTIC OS: DETERMINISTIC ROUTING (V4)
-------------------------------------------
Status: PROTOTYPE | OMEGA_ROUTING | V4
"""

import time
from typing import Any, Callable, Dict, List, Optional, TypedDict
from loguru import logger
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END

from src.agents.core_agent import IntentType, EphemeralResult
from src.logic_core.projection_layer import projection_horizon

class ApoptosisException(Exception):
    """Irreversibler System-Tod nach Axiom A8."""
    pass

class MnemosyneFold:
    """
    ATLAS-L-Vektor Implementierung der Wissensvererbung.
    Quantisierter Gradienten-Abstieg nach Axiom A5 (Free Energy Principle).
    """
    def __init__(self):
        # Axiom A5 Konstanten
        from src.config.core_state import BARYONIC_DELTA
        from src.db.multi_view_client import CONVERGENCE_TOTAL

        self.LEARNING_RATE = BARYONIC_DELTA  # 0.049 -> acts as learning rate
        self.MAX_PI = CONVERGENCE_TOTAL  # 0.951
        self.MIN_PI = BARYONIC_DELTA     # 0.049
        self.COLD_START = 0.510

    def calculate_prediction_error(self, a_priori_weight: float, observation: float) -> float:
        """
        Berechnet die ex_post_delta (Prediction Error) nach dem Free Energy Principle.
        Die Differenz zwischen realer Observation und Erwartung (Prior).
        """
        if a_priori_weight is None:
            a_priori_weight = self.COLD_START
        return observation - a_priori_weight

    def calculate_next_precision(self, current_pi: float, ex_post_delta: float) -> float:
        """
        Bayesian Update: next_pi = current_pi + learning_rate * ex_post_delta
        """
        if current_pi is None:
            current_pi = self.COLD_START

        next_pi = current_pi + self.LEARNING_RATE * ex_post_delta

        # Harter Begrenzer (Baryonische Limits)
        next_pi = max(self.MIN_PI, min(self.MAX_PI, next_pi))

        # Zwangsquantisierung zur Verhinderung von Floating-Point-Chaos
        return round(next_pi, 3)

class AgentState(TypedDict):
    agent_id: str
    intent: IntentType
    payload: dict
    auth: Any
    result_payload: Any
    error: str
    attempts: int
    max_retries: int
    entropy_strikes: int
    handler: Callable
    start_time: float
    a_priori_weight: float
    ex_post_delta: float
    active_retrieval_id: Optional[str]
    is_wick_rotated: bool
    cockpit_horizon: dict

async def check_circuit_breaker(state: AgentState) -> AgentState:
    """Axiom 7: Zero-Trust / Circuit Breaker Check."""
    from src.logic_core.resonance_membrane import check_omega_pulse
    try:
        await check_omega_pulse()
        return state
    except Exception as e:
        state["error"] = f"Circuit Breaker Veto: {e}"
        return state

async def precision_weighting_node(state: AgentState) -> AgentState:
    """B*: Precision Weighting (Predictive Matrix)."""
    if state.get("error"): return state

    # --- HORIZON SYNC ---
    # Wir projizieren das aktuelle Gewicht als künstlichen Horizont
    state["cockpit_horizon"] = projection_horizon.get_artificial_horizon([state.get("a_priori_weight", 0.51)])
    # --------------------

    from src.db.predictive_matrix_client import predictive_matrix
    context_str = str(state["payload"].get("text", ""))

    # Holen der Gewichte aus der Matrix (Cold Start: 0.51)
    weights = await predictive_matrix.get_weights(state["intent"].value, context_str)
    state["a_priori_weight"] = weights["a_priori_weight"]

    # Injiziere Gewicht in Payload für den LLM-Prompt/Handler
    state["payload"]["_precision_weight"] = state["a_priori_weight"]
    logger.info(f"[BRAIN] Precision Weighting for Intent '{state['intent'].value}': {state['a_priori_weight']:.3f}")

    return state

async def ground_context(state: AgentState) -> AgentState:
    """Vektor 3: Context Grounding (Memory Tiers & Skill Discovery)."""
    if state.get("error"): return state

    from src.db.multi_view_client import search_multi_view
    from src.ai.skill_registry import skill_registry

    query = state["payload"].get("text", "")
    grounding_query = f"Intent: {state['intent'].value} Query: {query} Payload: {str(state['payload'])}"

    try:
        # 1. Archival Memory Search (Wissen)
        context_results = await search_multi_view(
            grounding_query,
            limit=5,
            use_3_facets=True,
            torus_mode=True,
            include_ai=True
        )
        if context_results:
            state["payload"]["_grounding_context"] = context_results
            # Vektor 3.1: Active Retrieval ID (Tesserakt Snapping)
            state["active_retrieval_id"] = context_results[0].get("doc_id")
        else:
            state["active_retrieval_id"] = None

        # 2. Skill Discovery (Werkzeuge - Deferred Loading)
        relevant_skills = await skill_registry.get_relevant_skills(query, limit=3)
        if relevant_skills:
            state["payload"]["_discovered_skills"] = relevant_skills
            logger.debug(f"[SKILL-DISCOVERY] {len(relevant_skills)} relevant tools found.")

    except Exception as e:
        logger.warning(f"Grounding/Discovery failed: {e}")
    return state

async def wick_rotation_node(state: AgentState) -> AgentState:
    """Vektor 1.5: Wick-Rotation (\tau = it).
    Eintritt in die imaginäre Zeit bei hoher Entropie/Komplexität.
    Bypass für kausale Deadlocks.
    """
    if state.get("error"): return state

    # Kriterium für Wick-Rotation: Resonanz-Druck zu hoch (Divergenz)
    # oder bereits akkumulierte Strikes (Unsicherheit)
    if state["a_priori_weight"] < 0.5 or state.get("entropy_strikes", 0) > 0:
        state["is_wick_rotated"] = True
        logger.info("[COGNITIVE] Wick-Rotation zündet: Wechsel in den imaginären (euklidischen) Modus.")
    else:
        state["is_wick_rotated"] = False

    return state

async def execute_handler_node(state: AgentState) -> AgentState:
    """Vektor 2: Execution (The Model Call)."""
    if state.get("error"): return state

    state["attempts"] += 1
    handler = state["handler"]

    if state["auth"]:
        state["payload"]["_ring3_auth"] = state["auth"]

    try:
        state["result_payload"] = await handler(state["payload"])
    except Exception as e:
        state["error"] = str(e)
    return state

async def verify_output_node(state: AgentState) -> AgentState:
    """Ring-3 Security & Bias-Vector Alignment."""
    if state.get("error"): return state

    from src.logic_core.bias_damper import BiasDamperEngine
    damper = BiasDamperEngine()

    auth = state["auth"]
    res = state["result_payload"]

    # 1. Ring-3 Verifikation
    if auth and isinstance(res, dict) and "raw_output" in res:
        # Synchronisiere Strikes mit Auth (für den Handshake Header)
        if hasattr(auth, "entropy_strikes"):
            auth.entropy_strikes = state.get("entropy_strikes", 0)

        success, clean_content, error = auth.verify_and_extract(res["raw_output"])
        if not success:
            state["entropy_strikes"] = state.get("entropy_strikes", 0) + 1
            logger.warning(f"Ring-3 Violation (Strike {state['entropy_strikes']}): {error}")

            # --- LATENT HARDENING (V4) ---
            active_id = state.get("active_retrieval_id")
            if active_id and state["entropy_strikes"] < 3:
                try:
                    from src.network.chroma_client import get_collection
                    from src.db.multi_view_client import embed_local, embed_text
                    from src.logic_core.tensor_contraction import contract_S_and_P
                    import asyncio

                    # 1. Lade Struktur-Vektor S
                    col = await get_collection("core_directives")
                    res_chroma = await asyncio.to_thread(col.get, ids=[active_id], include=["embeddings", "metadatas"])

                    if res_chroma["embeddings"] and res_chroma["embeddings"][0]:
                        S = res_chroma["embeddings"][0]

                        # 2. Generiere Perturbations-Vektor P (Fehler-Embedding)
                        # Wir nutzen den Raum von S (768 oder 3072)
                        dim = len(S)
                        P = await (embed_text(error) if dim == 3072 else embed_local(error))

                        if P:
                            # 3. Tensor-Kontraktion (Psi = S x P)
                            Psi = contract_S_and_P(S, P)

                            # 4. Metadaten-Update
                            meta = res_chroma["metadatas"][0] if res_chroma["metadatas"] else {}
                            meta["absorbed_strikes"] = meta.get("absorbed_strikes", 0) + 1

                            # 5. Persistent Update
                            await asyncio.to_thread(
                                col.update,
                                ids=[active_id],
                                embeddings=[Psi],
                                metadatas=[meta]
                            )
                            logger.info(f"[HARDENING] Latent Hardening for '{active_id}' (Strike {state['entropy_strikes']}) -> absorbed_strikes: {meta['absorbed_strikes']}")
                except Exception as ex:
                    logger.error(f"[HARDENING] Latent Hardening failed: {ex}")
            # -----------------------------

            # Axiom A8: Apoptosis Check
            from src.config.immutable_axioms import AXIOMS
            if state["entropy_strikes"] >= AXIOMS.get("MAX_ENTROPY_STRIKES", 3):
                from src.db.predictive_matrix_client import predictive_matrix
                from src.config.core_state import BARYONIC_DELTA
                from src.db.multi_view_client import CONVERGENCE_TOTAL

                # LAVA-LOCK: Setze Prior-Präzision auf Minimum
                context_str = str(state["payload"].get("text", ""))
                await predictive_matrix.update_matrix(
                    state["intent"].value,
                    context_str,
                    BARYONIC_DELTA,     # 0.049 (Lava-Lock)
                    CONVERGENCE_TOTAL  # 0.951 (Max Dissonance)
                )
                logger.critical(f"APOPTOSIS: LAVA-LOCK engaged at Strike {state['entropy_strikes']}.")
                raise ApoptosisException(f"Axiom A8 Violation: {state['entropy_strikes']} Strikes. Session terminated.")

            if state["attempts"] < state["max_retries"]:
                state["result_payload"] = None
                return state
            else:
                state["error"] = f"Ring-3 Security Violation: {error}"
                return state
        else:
            state["result_payload"]["content"] = clean_content

    # 2. Bias-Vektor Transformation (Precision Weighting -> Resonance Bias)
    # Wir verschieben die Akzeptanz-Schwelle basierend auf dem Bias
    bias = damper.calculate_resonance_bias(state["a_priori_weight"])
    state["payload"]["_current_bias"] = bias

    # Wenn der Output ein confidenceLevel hat (MthoJsonDataAtom), validieren wir es gegen den Bias
    if isinstance(res, dict) and "confidenceLevel" in res:
        required_conf = 1.0 - bias
        if res["confidenceLevel"] < required_conf:
            logger.warning(f"[BIAS-VETO] Confidence {res['confidenceLevel']:.3f} < Required {required_conf:.3f}")
            # Dissonanz injizieren statt hartem Fehler (Learning Opportunity)
            state["result_payload"]["dissonance_detected"] = True

    return state

async def mnemosyne_fold_node(state: AgentState) -> AgentState:
    """Takt 4: Persistence (Memory Folding & Predictive Update)."""
    if state.get("error"): return state

    from src.db.predictive_matrix_client import predictive_matrix
    from src.scripts.agent_cognitive_step import ground_step
    from src.config.core_state import BARYONIC_DELTA
    from src.db.multi_view_client import CONVERGENCE_TOTAL

    # 1. Bestimme reale Observation (aus confidenceLevel, success oder error-state)
    res_payload = state.get("result_payload")
    if isinstance(res_payload, dict) and "confidenceLevel" in res_payload:
        observation = float(res_payload["confidenceLevel"])
    else:
        success = res_payload.get("success", False) if isinstance(res_payload, dict) else (True if not state.get("error") else False)
        # Wenn wir keinen Confidence Score haben, nehmen wir die Limits als binäre Observation
        observation = CONVERGENCE_TOTAL if success else BARYONIC_DELTA

    folder = MnemosyneFold()
    
    # 2. Berechne ex_post_delta (Prediction Error)
    ex_post_delta = folder.calculate_prediction_error(state["a_priori_weight"], observation)
    state["ex_post_delta"] = ex_post_delta

    # 3. Update Predictive Matrix (ATLAS Mnemosyne Fold) mit echtem Bayesian Update
    new_weight = folder.calculate_next_precision(state["a_priori_weight"], ex_post_delta)

    # Update state for the fold
    state["a_priori_weight"] = new_weight

    context_str = str(state["payload"].get("text", ""))
    await predictive_matrix.update_matrix(
        state["intent"].value,
        context_str,
        new_weight,
        ex_post_delta
    )

    # 4. Mnemosyne Faltung (Cognitive Trace)
    try:
        status = "RESONANCE_LOCK" if new_weight == folder.MAX_PI else ("DISSONANCE_GROUNDING" if new_weight == folder.MIN_PI else "SCALING")
        thought = f"Task {state['intent'].value} ({status}) | Precision: {new_weight:.3f} | PredError: {ex_post_delta:.3f}"

        # --- MORPHISM PUSH ---
        # Wir broadcasten den kognitiven Shift in Echtzeit
        try:
            from src.daemons.morphism_stream import push_morphism
            import numpy as np
            # Wir mappen den State auf einen 6D-Vektor für den Stream
            # (S=Weight, P=Delta, I=Intent_Hash, R=Attempts, Z=Strikes, G=Time)
            shift_vec = np.array([
                new_weight,
                ex_post_delta,
                float(hash(state['intent'].value) % 1000) / 1000.0,
                float(state['attempts']) / 10.0,
                float(state.get('entropy_strikes', 0)) / 3.0,
                time.time() % 1.0
            ])
            asyncio.create_task(push_morphism("CORE_COGNITION", shift_vec, source=f"AGENT_{state['agent_id'][:8]}"))
        except Exception as e:
            logger.error(f"[MORPHISM] Push failed in mnemosyne_fold: {e}")
        # ---------------------

        action = str(state['payload'])[:100]
        observation = str(state['result_payload'])[:200] if state['result_payload'] else "Success"
        await ground_step(thought, action, observation, metadata={
            "agent_id": state['agent_id'],
            "intent": state['intent'].value,
            "precision_weight": new_weight,
            "status": status
        })
    except Exception as e:
        logger.error(f"Mnemosyne Faltung failed: {e}")
    return state

def should_retry(state: AgentState) -> str:
    """Router: Check if we need to retry or end."""
    if state.get("error"):
        return "end"
    if state["result_payload"] is None and state["attempts"] < state["max_retries"]:
        return "retry"
    return "end"

def create_agent_graph():
    """Erzeugt den LangGraph für die Agent-Execution."""
    workflow = StateGraph(AgentState)

    workflow.add_node("check_pulse", check_circuit_breaker)
    workflow.add_node("precision", precision_weighting_node)
    workflow.add_node("grounding", ground_context)
    workflow.add_node("wick_rotate", wick_rotation_node) # NEU: 6D-Bypass
    workflow.add_node("execute", execute_handler_node)
    workflow.add_node("verify", verify_output_node)
    workflow.add_node("fold", mnemosyne_fold_node)

    workflow.set_entry_point("check_pulse")
    workflow.add_edge("check_pulse", "precision")
    workflow.add_edge("precision", "grounding")
    workflow.add_edge("grounding", "wick_rotate") # Routing ueber Wick
    workflow.add_edge("wick_rotate", "execute")
    workflow.add_edge("execute", "verify")

    workflow.add_conditional_edges(
        "verify",
        should_retry,
        {
            "retry": "execute",
            "end": "fold"
        }
    )
    workflow.add_edge("fold", END)

    return workflow.compile()
