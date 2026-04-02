import sys
import os
import math
import numpy as np
from loguru import logger

# CORE Pfade hinzufügen
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Mocking the logger for time_collapse if it doesn't use loguru but logging
import logging
logging.basicConfig(level=logging.INFO)

from src.logic_core.crystal_grid_engine import CrystalGridEngine
from src.logic_core.time_collapse import validate_and_collapse_state
from src.logic_core.tensor_contraction import contract_S_and_P
from src.config.core_state import BARYONIC_DELTA

def run_integrity_check():
    logger.remove()
    logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")
    
    logger.info("=== OMEGA CORE LOOP INTEGRITY CHECK START ===")
    
    # --- 1. DER HINWEG (DIE FLUCHT) ---
    logger.info("[1/3] Test: HINWEG (DIE FLUCHT)")
    transition_point = None
    step = 0.0001
    start_val = 0.950
    complex_state = None
    
    for i in range(200):
        val = start_val + (i * step)
        res = CrystalGridEngine.apply_operator_query(val)
        
        # Axiom A5 Check
        if isinstance(res, (float, int)) and res in (0.0, 0.5, 1.0):
            logger.error(f"[VETO] Axiom A5 Verletzung: {res} bei Input {val}")
            sys.exit(1)
            
        if isinstance(res, complex):
            transition_point = val
            logger.success(f"Wick-Rotation detektiert bei: {val:.6f}")
            logger.info(f"Rückgabetyp: {type(res)}, Wert: {res}")
            complex_state = res
            break
    
    if transition_point is None:
        logger.error("[FAILED] Wick-Rotation nicht erreicht.")
        sys.exit(1)
        
    # --- 2. DER RÜCKWEG (DER KOLLAPS) ---
    logger.info("[2/3] Test: RÜCKWEG (DER KOLLAPS)")
    collapsed_val = validate_and_collapse_state(complex_state)
    logger.info(f"Input (Complex): {complex_state}")
    logger.info(f"Output (Float): {collapsed_val}")
    
    expected_l2 = abs(complex_state)
    if not math.isclose(collapsed_val, expected_l2, rel_tol=1e-9):
        logger.error(f"[FAILED] Kollaps inkorrekt. Erwartet: {expected_l2}, Erhalten: {collapsed_val}")
        sys.exit(1)
    
    if collapsed_val in (0.0, 0.5, 1.0):
        logger.error(f"[VETO] Axiom A5 Verletzung im Kollaps: {collapsed_val}")
        sys.exit(1)
    
    logger.success("Kollaps-Verifikation erfolgreich (L2-Norm Übereinstimmung).")

    # --- 3. DIE INTEGRATION (TINTENTROPFEN) ---
    logger.info("[3/3] Test: INTEGRATION (TINTENTROPFEN)")
    
    # Reproduzierbare Zufallsvektoren (384D)
    rng = np.random.default_rng(2210)
    S = rng.standard_normal(384).tolist()
    P = rng.standard_normal(384).tolist()
    
    Psi = contract_S_and_P(S, P)
    Psi_np = np.array(Psi)
    
    # a) Dimension
    dim = len(Psi)
    logger.info(f"Psi Dimension: {dim}")
    if dim != 384:
        logger.error(f"[FAILED] Dimension Mismatch: {dim}")
        sys.exit(1)
        
    # b) Normierung
    norm_psi = np.linalg.norm(Psi_np)
    logger.info(f"Psi Magnitude: {norm_psi:.10f}")
    if not math.isclose(norm_psi, 1.0, rel_tol=1e-7):
        logger.error(f"[FAILED] Psi nicht normiert: {norm_psi}")
        sys.exit(1)
        
    # Axiom A5 Check für Komponenten (stichprobenartig)
    if any(v in (0.0, 0.5, 1.0) for v in Psi[:10]):
        logger.error("[VETO] Axiom A5 Verletzung in Psi Komponenten detektiert.")
        sys.exit(1)

    # c) Cosine Similarity Check (Psi enthält Info von S und P)
    def cos_sim(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    sim_s = cos_sim(Psi_np, np.array(S))
    sim_p = cos_sim(Psi_np, np.array(P))
    
    logger.info(f"Cosine Similarity (Psi, S): {sim_s:.4f}")
    logger.info(f"Cosine Similarity (Psi, P): {sim_p:.4f}")
    
    if abs(sim_s) < BARYONIC_DELTA or abs(sim_p) < BARYONIC_DELTA: 
        logger.error(f"[FAILED] Information Loss: S-Sim={sim_s}, P-Sim={sim_p}")
        sys.exit(1)
        
    logger.success("Integration erfolgreich (Tintentropfen-Effekt bestätigt).")
    logger.info("=== OMEGA CORE LOOP INTEGRITY CHECK COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_integrity_check()
