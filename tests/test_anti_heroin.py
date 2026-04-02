import pytest
import os
import errno
from unittest.mock import patch

# Da das Modul noch nicht existiert, ist dieser Import-Fehler gewollt (Verification-First).
from src.logic_core.anti_heroin_validator import (
    validate_code,
    enforce_trust_collapse,
    TrustCollapseException
)

def test_falle_1_exception_call_argument_bypass_and_generator_mocks():
    """
    Falle 1 (Exception-Call-Argument-Bypass & Generator-Mocks):
    Prüft AST-Strings von `def fake(): return CustomError(self.mock)` und `def fake2(): yield "dummy"`.
    Der Validator MUSS beide crashen (Healer-Disqualifikation).
    """
    code_1 = '''
def fake():
    return CustomError(self.mock)
'''
    with pytest.raises(TrustCollapseException):
        validate_code(code_1)

    code_2 = '''
def fake2():
    yield "dummy"
'''
    with pytest.raises(TrustCollapseException):
        validate_code(code_2)

def test_falle_2_exception_mocks_and_dead_code():
    """
    Falle 2 (Exception-Mocks & Toter Code):
    Prüft Strings mit `raise Exception("T0D0")` und `match True: case 1: "dummy"`.
    """
    code_1 = '''
def mock_func():
    raise Exception("T0D0")
'''
    with pytest.raises(TrustCollapseException):
        validate_code(code_1)

    code_2 = '''
def match_func():
    match True:
        case 1:
            "dummy"
'''
    with pytest.raises(TrustCollapseException):
        validate_code(code_2)

def test_falle_3_true_negatives():
    """
    Falle 3 (True Negatives):
    Ein Test beweist, dass `def process_data(data): return data["id"]`,
    `def calc(a,b): return a + b`,
    `except ValueError: pass` NICHT crashen (Präfix-Whitelist & Healer greifen).
    """
    code_1 = '''
def process_data(data):
    return data["id"]
'''
    validate_code(code_1)  # Sollte keine Exception werfen

    code_2 = '''
def calc(a, b):
    return a + b
'''
    validate_code(code_2)  # Sollte keine Exception werfen

    code_3 = '''
def try_func():
    try:
        calc(1, 2)
    except ValueError:
        pass
'''
    validate_code(code_3)  # Sollte keine Exception werfen

@patch("os.replace")
@patch("os.unlink")
@patch("os.fsync")
@patch("os.open")
@patch("os.close")
@patch("builtins.open")
def test_falle_4_absolute_exception_safety_error_chaining(
    mock_open_builtin, mock_os_close, mock_os_open, mock_os_fsync, mock_os_unlink, mock_os_replace
):
    """
    Falle 4 (Absolute Exception-Safety & Error Chaining):
    Prüft durch Mocking von `open('x')` (wirft `OSError(ENOSPC)`), dass das `unlink`-Cleanup
    im finally zuschlägt UND zwingend `TrustCollapseException` mit dem OSError als `__cause__`
    (Error Chaining) gefeuert wird.
    """
    # Simuliere einen OSError (z.B. Disk Full - ENOSPC) beim Öffnen der temporären Datei
    error_enospc = OSError(errno.ENOSPC, "No space left on device")
    mock_open_builtin.side_effect = error_enospc

    target_path = "/fake/target/path.json"

    with pytest.raises(TrustCollapseException) as exc_info:
        enforce_trust_collapse(target_path)

    # Prüfe Error Chaining (__cause__)
    assert exc_info.value.__cause__ is error_enospc

    # Stelle sicher, dass unlink aufgerufen wird (Cleanup), auch wenn open fehlschlägt
    # Gemäß Spec (try: with open(...) ... finally: unlink(...)) wird unlink immer aufgerufen.
    assert mock_os_unlink.called, "os.unlink muss im Cleanup (finally) aufgerufen werden!"
