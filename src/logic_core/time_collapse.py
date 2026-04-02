import logging
import math
import numpy as np
import torch
from typing import Union, Any

logger = logging.getLogger("OMEGA_DAEMON")

from src.logic_core.projection_layer import projection_horizon

def validate_and_collapse_state(state_value: Union[float, int, complex, torch.Tensor, Any]) -> float:
    """
    Zwingt den hochdimensionalen/komplexen Zustand zurück in die euklidische 1D-Zeit.
    Bereitet den Vektor für ChromaDB vor (Float-Zwang).
    Boundary Daemon: Deterministisch implementiert in PyTorch.
    """
    # 1. Detection
    is_complex_type = isinstance(state_value, complex)
    is_complex_tensor = isinstance(state_value, torch.Tensor) and state_value.is_complex()
    
    if is_complex_type or is_complex_tensor:
        logger.info("OMEGA ESCAPE / Wick-Rotation")

    # Konvertierung in PyTorch Tensor
    if isinstance(state_value, torch.Tensor):
        tensor = state_value
    elif isinstance(state_value, complex):
        tensor = torch.tensor(state_value, dtype=torch.complex128)
    else:
        tensor = torch.tensor(float(state_value), dtype=torch.float64)

    # 2. Collapse
    causal_scalar_tensor = torch.abs(tensor)
    causal_scalar = float(causal_scalar_tensor.item())

    # 3. Axiom 5 Check
    if causal_scalar >= 1.0:
        logger.error("[AXIOM 5 FATAL] System hat 1.0 Symmetrie-Gefangenschaft erreicht.")
        raise ValueError("Axiom 5 Violation: Linear Death")

    # 4. Penterakt Shift
    # Wenn der Omega_b Gradient (delta zur Schwelle 0.049) gegen 0.049 konvergiert (< 1e-4 Toleranz)
    if abs(causal_scalar - 0.049) < 1e-4:
        logger.warning("[PENTERAKT SHIFT] Konvergenz zu 0.049 detektiert. Führe Rettungsrotation aus.")
        v_anchor = tensor
        v_new = v_anchor * torch.exp(1j * torch.tensor(math.pi / 2))
        
        logger.info(f"[PENTERAKT SHIFT] Neuer Tensor-State: {v_new}")
        
        causal_scalar_tensor = torch.abs(v_new)
        causal_scalar = float(causal_scalar_tensor.item())

    return causal_scalar
