# -*- coding: utf-8 -*-
r"""
OMEGA TENSOR CONTRACTION CORE
-----------------------------
Hardware-deterministische Tensor-Kontraktion via PyTorch.
Ersetzt 1D-String-Addition durch kategorientheoretische Tensor-Kontraktion (\Psi = S \times P).
Integriert PRISM-Wellenmechanik und spektrale GHC-Attention.
"""

import torch
import logging

logger = logging.getLogger("OMEGA_TENSOR")

# 1. Hardware-Determinismus (Keine adaptiven Heuristiken)
torch.manual_seed(42)
if torch.cuda.is_available():
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.use_deterministic_algorithms(True, warn_only=True)

def contract_S_and_P(symmetry_S: list[float], perturbation_P: list[float]) -> list[float]:
    """
    Tensor-Kontraktion im komplexen Raum (torch.complex64).
    S-Vektor und P-Vektor werden über das elementweise Hadamard-Produkt verschränkt
    und anschließend auf die L2-Norm zurückskaliert.
    """
    if len(symmetry_S) != len(perturbation_P):
        logger.error(f"Dimensions-Mismatch: S={len(symmetry_S)}, P={len(perturbation_P)}")
        raise ValueError("Axiom-Verletzung: P und S existieren nicht im selben Tensor-Raum.")

    # Umwandlung der Inputs in komplexe Tensoren
    S_tensor = torch.tensor(symmetry_S, dtype=torch.complex64)
    P_tensor = torch.tensor(perturbation_P, dtype=torch.complex64)

    # Elementweises Hadamard-Produkt (Psi = S * P)
    Psi = S_tensor * P_tensor

    # L2-Norm-Skalierung
    norm_Psi = torch.linalg.vector_norm(Psi)
    
    if norm_Psi > 0:
        Psi = Psi / norm_Psi
    else:
        # Fallback auf reines S, falls P zu vollständiger Auslöschung führt
        norm_S = torch.linalg.vector_norm(S_tensor)
        if norm_S > 0:
            Psi = S_tensor / norm_S
        else:
            Psi = S_tensor

    # Rückführung in den Float-Raum für die Resonanz-Domäne (Axiom A6)
    return Psi.real.tolist()

def spectral_ghc_attention(tensor: torch.Tensor, filter_weights: torch.Tensor) -> torch.Tensor:
    """
    Spektrale GHC-Attention (Gated Harmonic Convolutions).
    Wandelt Tensoren via FFT in den Frequenzraum, multipliziert spektrale Filtergewichte,
    maskiert/löscht destruktive Interferenzen und transformiert via IFFT zurück.
    """
    if tensor.shape != filter_weights.shape:
        raise ValueError("Tensor und Filter müssen identische Dimensionen für das Hadamard-Produkt aufweisen.")

    # 1. FFT in den Frequenzraum
    freq_tensor = torch.fft.fft(tensor)

    # 2. Spektrale Filterung (Hadamard-Produkt mit statischen/gelernten Gewichten)
    filtered_freq = freq_tensor * filter_weights

    # 3. Maskierung destruktiver Interferenzen
    # Wir filtern schwache Signale heraus, die durch Phasenauslöschung entstanden sind
    magnitudes = torch.abs(filtered_freq)
    threshold = torch.mean(magnitudes) * 0.1  # Statischer Cutoff ohne adaptive Heuristik
    gate_mask = magnitudes > threshold
    
    # Gating anwenden
    gated_freq = filtered_freq * gate_mask

    # 4. Inverse FFT
    output_tensor = torch.fft.ifft(gated_freq)

    # Projektion zurück auf die reellen Koordinaten
    return output_tensor.real
