import logging
import math
import torch
from typing import Union, Tuple

logger = logging.getLogger("OMEGA_DAEMON")

def matrix_sqrt_via_eigh(A: torch.Tensor) -> torch.Tensor:
    """
    Berechnet die Matrixwurzel einer symmetrischen positiv semidefiniten Matrix
    über Spektralzerlegung (eigh), da exakte Newton-Schulz-Wurzeln zu langsam sind.

    Args:
        A: Symmetrische, positiv semidefinite Matrix (Tensor).

    Returns:
        Matrixwurzel von A.
    """
    # Nutzt eigh für reelle, symmetrische Matrizen (oder hermitische)
    L, V = torch.linalg.eigh(A)
    # Rauschen / numerische Ungenauigkeiten abfangen (Eigenwerte >= 0)
    L = torch.clamp(L, min=0.0)
    return V @ torch.diag_embed(torch.sqrt(L).to(V.dtype)) @ V.mH

def bures_fidelity(rho: torch.Tensor, sigma: torch.Tensor) -> torch.Tensor:
    """
    Berechnet die Bures-Fidelity zwischen zwei Dichtematrizen (bzw. positiv semidefiniten Matrizen).
    Ersetzt naive Cosine-Similarity im Informationsgravitations-Framework.

    F(rho, sigma) = (Tr sqrt(sqrt(rho) * sigma * sqrt(rho)))^2
    """
    # 1. sqrt(rho) berechnen
    sqrt_rho = matrix_sqrt_via_eigh(rho)

    # 2. M = sqrt(rho) * sigma * sqrt(rho)
    M = sqrt_rho @ sigma @ sqrt_rho

    # 3. Tr(sqrt(M))
    # Da M symmetrisch und PSD ist, ist die Spur der Wurzel gleich der Summe der Wurzeln der Eigenwerte.
    L_M, _ = torch.linalg.eigh(M)
    L_M = torch.clamp(L_M, min=0.0)
    trace_sqrt_M = torch.sum(torch.sqrt(L_M), dim=-1)

    fidelity = trace_sqrt_M ** 2
    return fidelity

def calc_node_relevance(rho: torch.Tensor, sigma: torch.Tensor, activation: torch.Tensor, c: float = 1.0) -> torch.Tensor:
    """
    Berechnet die Knoten-Relevanz auf Basis von Bures-Distanz und MEIE-Informationsmasse.
    Informationsgravitation: Relevanz = D_bures(rho, sigma) * (E / c^2)

    Args:
        rho: Referenz-Zustand (Dichtematrix)
        sigma: Evaluierter Zustand (Dichtematrix)
        activation: Node-Aktivierungstensor (zur E-Berechnung)
        c: Lichtgeschwindigkeit / Limit-Konstante (default 1.0)
    """
    # Bures-Fidelity
    F = bures_fidelity(rho, sigma)

    # Spuren (Traces) berechnen
    tr_rho = torch.diagonal(rho, dim1=-2, dim2=-1).sum(-1)
    tr_sigma = torch.diagonal(sigma, dim1=-2, dim2=-1).sum(-1)

    # Bures-Distanz: D_B = sqrt(Tr(rho) + Tr(sigma) - 2 * sqrt(F))
    # Numerische Stabilität via clamp garantieren
    distance_sq = torch.clamp(tr_rho + tr_sigma - 2.0 * torch.sqrt(F), min=0.0)
    bures_dist = torch.sqrt(distance_sq)

    # MEIE Informationsmasse (m = E/c^2), wobei E = L2-Norm der Aktivierung
    # Nutze Axiom 5 (c != 0) zur Division
    E = torch.linalg.norm(activation, dim=-1)
    m = E / (c ** 2)

    # Finale Informationsgravitations-Relevanz
    relevance = bures_dist * m
    return relevance

class TopologicalContextCompressor:
    """
    Kontext-Kompressor für spektrale GHC-Attention.
    Entropie-basierte Kardinalitätsminimierung.
    WICHTIG: Vermeidet lineares Speicherwachstum (list.append verboten!).
    """
    def __init__(self, capacity: int, hidden_dim: int, noise_threshold: float = 0.1):
        self.capacity = capacity
        self.hidden_dim = hidden_dim
        self.noise_threshold = noise_threshold
        # Deterministischer Zustand: Fester Ringpuffer, keine dynamischen Listen
        self.state = torch.zeros((capacity, hidden_dim), dtype=torch.float32)

    def ingest_token(self, token_tensor: torch.Tensor) -> None:
        """
        Integriert einen neuen Token-Vektor in den topologischen Puffer.
        Linear history.append ist architektonisch verboten (Axiom 5/Entropie-Leak).
        """
        if token_tensor.shape[-1] != self.hidden_dim:
            raise ValueError(f"Token-Dimension {token_tensor.shape[-1]} entspricht nicht dem Hidden-Dim {self.hidden_dim}")

        # Deterministische O(1) Rotation (In-Place Shift)
        self.state = torch.roll(self.state, shifts=-1, dims=0)
        self.state[-1] = token_tensor

    def compress(self) -> torch.Tensor:
        """
        Data Pruning: FFT-Transformation in den Phasenraum.
        Token/Frequenzen, deren Phasen destruktiv interferieren (Rauschen),
        werden maskiert, bevor es über iFFT zurückgesetzt wird.
        """
        # 1. Fourier-Transformation (Zeit -> Phase/Frequenz)
        # dim=0 da wir über die Sequence-Length (Kapazität) transformieren
        freq_state = torch.fft.fft(self.state, dim=0)

        # 2. Amplituden-/Leistungsspektrum berechnen
        power = torch.abs(freq_state) ** 2

        # 3. Entropie-basierte Rausch-Maskierung (Dynamic Thresholding)
        max_power = torch.max(power, dim=0, keepdim=True)[0]
        # Alles unterhalb der Schwelle ist destruktive Interferenz / Rauschen
        noise_mask = power > (self.noise_threshold * max_power)

        # 4. Maskieren der Rausch-Frequenzen
        pruned_freq_state = freq_state * noise_mask

        # 5. Inverse FFT zurück in den linearen / topologischen Raum
        compressed_state = torch.fft.ifft(pruned_freq_state, dim=0).real

        # 6. Zustand updaten
        self.state = compressed_state
        return self.state
