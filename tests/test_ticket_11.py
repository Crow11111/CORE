# -*- coding: utf-8 -*-
"""
TICKET 11 — Kognitive Membran (Cognitive Membrane) Veto-Traps.

Verification-First: Definiert den harten Kontrakt für die Kognitive Membran.
Die Tests schlagen mit expliziten pytest.fail-Meldungen fehl, solange die
Producer die Daemons/Validatoren noch nicht implementiert haben.

Spezifikation: docs/05_AUDIT_PLANNING/TICKET_11_COGNITIVE_MEMBRANE.md
"""
from __future__ import annotations

import importlib
from unittest.mock import MagicMock, patch

import pytest

# Erwartete neue Exceptions / Konstanten
PRE_FLIGHT_VETO_EXC = "PreFlightVetoException"


def _get_validator_module():
    try:
        return importlib.import_module("src.logic_core.anti_heroin_validator")
    except ImportError as exc:
        pytest.fail(f"TICKET 11 Veto: anti_heroin_validator fehlt oder ist kaputt. ({exc})")


def _get_membrane_daemon_module():
    try:
        return importlib.import_module("src.daemons.dread_membrane_daemon")
    except ImportError as exc:
        pytest.fail(f"TICKET 11 Veto: dread_membrane_daemon fehlt oder ist kaputt. ({exc})")


def test_veto_on_missing_memory_hash():
    """
    Trap 1: Mandatory Epistemic Pre-Flight (Säule 2).
    Der Kontrakt verlangt, dass `validate_agent_preflight` existiert und
    einen PreFlightVetoException wirft, wenn `memory_hash` fehlt.
    """
    val_mod = _get_validator_module()

    if not hasattr(val_mod, "validate_agent_preflight"):
        pytest.fail("TICKET 11 Veto: Funktion 'validate_agent_preflight' nicht implementiert.")
    if not hasattr(val_mod, PRE_FLIGHT_VETO_EXC):
        pytest.fail(f"TICKET 11 Veto: Exception '{PRE_FLIGHT_VETO_EXC}' nicht definiert.")

    validate_fn = getattr(val_mod, "validate_agent_preflight")
    ExcClass = getattr(val_mod, PRE_FLIGHT_VETO_EXC)

    # VETO: memory_hash = None
    with pytest.raises(ExcClass) as exc_info:
        validate_fn(agent_id="test_agent_1", memory_hash=None)
    assert "memory_hash" in str(exc_info.value).lower(), "Exception muss fehlenden Hash bemängeln."

    # VETO: memory_hash = "" (Leerstring) oder Whitespace
    with pytest.raises(ExcClass):
        validate_fn(agent_id="test_agent_2", memory_hash="")
    with pytest.raises(ExcClass):
        validate_fn(agent_id="test_agent_3", memory_hash="   ")


def test_apoptosis_at_baryonic_delta():
    """
    Trap 2: Apoptose & Synaptic Pruning (Säule 4 / Kardanischer Operator).
    Kontrakt: `trigger_apoptosis` muss Entropie gegen 0.049 prüfen und
    `purge_noise_event` auslösen, WENN UND NUR WENN Entropie < 0.049.
    """
    daemon_mod = _get_membrane_daemon_module()

    if not hasattr(daemon_mod, "trigger_apoptosis"):
        pytest.fail("TICKET 11 Veto: Funktion 'trigger_apoptosis' nicht in dread_membrane_daemon implementiert.")

    trigger_fn = getattr(daemon_mod, "trigger_apoptosis")

    # Wir mocken purge_noise_event, um zu prüfen ob es gerufen wird
    # Falls die Funktion noch gar nicht existiert, fangen wir das ab
    purge_mock = MagicMock()

    try:
        # Patch den Aufruf innerhalb des Daemons
        with patch("src.daemons.dread_membrane_daemon.purge_noise_event", purge_mock, create=True):

            # Entropie >= 0.049 -> Kardanischer Operator bleibt ruhig (Kein Purge)
            trigger_fn(entropy_value=0.050, event_id="evt_01")
            purge_mock.assert_not_called()

            trigger_fn(entropy_value=0.049, event_id="evt_02")
            purge_mock.assert_not_called()

            # Entropie < 0.049 -> Apoptose (Purge) MUSS ausgelöst werden
            trigger_fn(entropy_value=0.048, event_id="evt_03")
            purge_mock.assert_called_once_with("evt_03")

    except Exception as e:
        pytest.fail(f"TICKET 11 Veto: Logik in trigger_apoptosis ist fehlerhaft oder wirft unerwartete Fehler: {e}")
