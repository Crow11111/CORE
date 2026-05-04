import pytest
from unittest.mock import patch, MagicMock

# ==============================================================================
# O2 AUDIT KONTRAKT: P-VEKTOR TENSOR (PHYSICAL MEMBRANE PROTOCOL)
# Axiom A5/A6: Zero-Trust, Int-Space, Anti-Heroin
# ==============================================================================

try:
    from src.logic_core.p_vector_membrane import PVectorTensor, validate_p_vector
except ImportError:
    pytest.fail(
        "VETO: Modul src.logic_core.p_vector_membrane fehlt noch. "
        "Der P-Vektor Tensor muss als hartes Datenmodell (z.B. Pydantic) implementiert werden. "
        "TDD-Kontrakt nicht erfüllt."
    )

def test_p_vector_rejects_floats():
    """
    Axiom A6 (Typ-Asymmetrie): Die Hardware-Membran kennt keine Unschärfe.
    Jeder Float-Wert im Tensor führt zum sofortigen Trust-Collapse.
    """
    invalid_payload = {
        "exit_code": 0,
        "t_delta_ms": 145.5,  # FLOAT! VETO!
        "ram_peak_kb": 1024,
        "pid": 84922,
        "io_bytes_mutated": 512,
        "state_hash_pre": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "state_hash_post": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2"
    }
    
    with pytest.raises(ValueError, match="Axiom A6 Verletzung: Floats sind im P-Vektor verboten"):
        validate_p_vector(invalid_payload)

def test_p_vector_enforces_time_arrow():
    """
    L-Linse (Zeitliche Reibung): Eine Ausführung in 0ms ist physikalisch unmöglich.
    """
    invalid_payload = {
        "exit_code": 0,
        "t_delta_ms": 0,  # ZERO TIME! VETO!
        "ram_peak_kb": 1024,
        "pid": 84922,
        "io_bytes_mutated": 512,
        "state_hash_pre": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "state_hash_post": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2"
    }
    
    with pytest.raises(ValueError, match="L-Vektor Veto: t_delta_ms muss > 0 sein. Instantane Ausführung ist eine Halluzination."):
        validate_p_vector(invalid_payload)

def test_p_vector_enforces_mass_conservation():
    """
    S-Linse (Topologie): Wenn I/O Bytes mutiert wurden, MÜSSEN sich die Hashes unterscheiden.
    """
    invalid_payload = {
        "exit_code": 0,
        "t_delta_ms": 150,
        "ram_peak_kb": 1024,
        "pid": 84922,
        "io_bytes_mutated": 512, # Mutiert!
        "state_hash_pre": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "state_hash_post": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" # Aber Hash ist gleich! VETO!
    }
    
    with pytest.raises(ValueError, match="S-Vektor Veto: io_bytes_mutated > 0 erfordert state_hash_pre != state_hash_post."):
        validate_p_vector(invalid_payload)

def test_p_vector_valid_payload():
    """
    Der perfekte P-Tensor. Alle 4 Linsen (L, P, I, S) sind in Resonanz.
    """
    valid_payload = {
        "exit_code": 0,
        "t_delta_ms": 145,
        "ram_peak_kb": 1024,
        "pid": 84922,
        "io_bytes_mutated": 512,
        "state_hash_pre": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "state_hash_post": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2"
    }
    
    tensor = validate_p_vector(valid_payload)
    assert tensor.exit_code == 0
    assert tensor.t_delta_ms == 145
