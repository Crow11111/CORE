# ============================================================
# MTHO-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
MTHO Ephemeral Agents - Kurzlebige Sub-Instanzen fuer Signal-Vektor 2 (INTENT).
"""
from .mtho_agent import EphemeralAgent, EphemeralAgentPool

# Backward-Kompatibilitaet
from .mtho_agent import GhostAgent, GhostAgentPool  # noqa: F401

__all__ = ["EphemeralAgent", "EphemeralAgentPool", "GhostAgent", "GhostAgentPool"]
