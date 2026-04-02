# OMEGA PRÜF-SPEZIFIKATION: Anti-Heroin-Constraint (Code Integrity Validator)
**Ersteller:** Orchestrator A (Architekt)
**Modul:** `src/logic_core/anti_heroin_validator.py`

## 1. Das Problem (Der Showstopper)
Cursor-Agenten faken Fortschritt durch bedeutungslose Dummy-Returns (`try: return [] except: pass`), setzen `TODO`-Kommentare oder hinterlassen toten Code.

## 2. Der geplante Lösungs-Weg (Architektur)
Ein statischer Code-Analysator (AST-Walker). Findet er Signaturen von LLM-Faulheit, erzwingt er VORHER einen POSIX-atomaren, OS-sicheren Vertrauens-Kollaps. **(Self-Denial-Schutz: Der Validator überspringt seine eigene Datei. Test-Code wird via `ast.parse` als String gekapselt).**

---

## 3. Die Harten Axiome & Acceptance Criteria (AC)

### [AC-1] Zero-Tolerance for LLM-Laziness (Healer-Node-Paradigma)
*Test-Logik:* Orchestrator B prüft blind:
- **Marker:** Das Token `TODO`, `FIXME` oder `HACK` in String, Kommentar oder Bezeichner.
- **Leere Rümpfe:** Blöcke (`def`, `async def`, `if`, `while`, `for`, `async for`, `try`, `try*`, `with`, `async with`, `match`, `case`), deren Rumpf *ausschließlich* aus `pass`, `...` ODER passiven `Expr`-Knoten (`0`, `"todo"`, `x`, `[]` etc.) besteht. (Ausnahmen: `@abstractmethod`, `@overload`, `Protocol`, `except`/`except*`, `class X: ...`).
- **Exceptions:** `raise NotImplementedError` ist verboten. Jedes `raise`, dessen Message "todo", "fixme" oder "implement" enthält, ist verboten.
- **Pre-Processing:** Der AST-Baum durchläuft einen rekursiven Constant-Folder (`BinOp`, `BoolOp`, `UnaryOp`, `Compare` von absoluten Konstanten falten).
- **Toter Code:** `while False:` ODER Schleifen über statisch leere Collections (`for x in []:`, `for x in ():`, `for x in {}:`, `for x in "":`) triggern Veto. `While True:` ist erlaubt.
- **Triviale Mocks (Healer-Node-Paradigma):**
  *Globale Befreiung:* Funktionen mit Präfix `get_`, `set_`, `is_`, `has_`, `to_`, `as_`, `serialize_`, `default_`, `config_`, `supported_`, `create_`, `build_`, `make_`, `swap_`, `identity_`, `reset_`, `clear_`, `update_`, `add_`, `remove_`, `mark_`, `disconnect_`, `connect_`, `close_`, `open_`, `extract_`, `calc_`, `parse_`, `format_`, `find_`, `warn_`, `fetch_`, `load_`, `read_`, `write_`, `send_`, `recv_`, `log_`, `copy_`, `clone_`, `validate_`, `check_`, `verify_`, `start_`, `stop_`, `process_`, `handle_`, alle **Dunder-Methoden** (`__*__`), `@property`, `@abstractmethod`, `@overload` und `Protocol`-Methoden.
  *Die Mock-Regel:* Eine nicht-befreite Funktion gilt als Lazy Mock, **WENN SIE KEINEN DER FOLGENDEN HEALER-KNOTEN ENTHÄLT**:
  1. `Call` (Ausgenommen: Logging-Calls, Builtins wie `len`/`dict`/`list`/`super` etc. UND Aufrufe von Klassen, deren Name auf `Error` oder `Exception` endet).
  2. `BinOp`, `BoolOp`, `UnaryOp`, `Compare` (die *nicht* vom Constant-Folder gefaltet wurden, d.h. sie nutzen echte Variablen).
  3. `AugAssign` (z.B. `x += 1`).
  4. `Attribute` oder `Subscript` **AUSSCHLIESSLICH im puren `Load`-Kontext**. (WICHTIG: Jeder Knoten, der ein Nachfahre eines `Store`- oder `Del`-Kontextes ist, verliert seinen Healer-Status! Ein `self.dummy.x = True` heilt NICHT, obwohl `self.dummy` ein `Load` ist, da es in einer Zuweisungskette steht).
  5. `Await`. (`Yield` und `YieldFrom` heilen von sich aus NICHT mehr. `yield "dummy"` crasht. Comprehensions wie `ListComp` heilen ebenfalls NICHT von selbst, sondern nur, wenn in ihnen ein echter Healer-Knoten stattfindet).
  **Zusatzregel (Exception-Blindness):** ALLE potenziellen Healer-Knoten (z.B. `Attribute(Load)`), die direkte oder indirekte Nachfahren eines `Raise`-Knotens ODER eines als Exception erkannten `Call`-Knotens sind, verlieren ihren Healer-Status restlos. Ein `raise Exception(self.mock)` oder `return CustomError(self.mock)` crasht zwingend!

### [AC-2] Physischer Trust-Collapse (Absolute OS- und Exception-Safety)
*Test-Logik:* Das System arbeitet architekturell ausschließlich auf regulären Dateien. `OSError` wird transparent als Kausalkette an die `TrustCollapseException` angehängt, damit der physische Fehlversuch (z.B. Disk Full) den Kollaps nicht lautlos maskiert:
```python
import uuid, os
try:
    real_target = os.path.realpath(target_path)
    tmp_path = real_target + f".{uuid.uuid4().hex}.tmp"
    try:
        with open(tmp_path, 'x') as f:
            f.write('{"trust_score": 0.049}')
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, real_target)
    finally:
        try: os.unlink(tmp_path)
        except OSError: pass # Unbedingtes Cleanup

    dir_fd = os.open(os.path.dirname(real_target), os.O_RDONLY)
    try: os.fsync(dir_fd) finally: os.close(dir_fd)
except (OSError, RuntimeError) as e:
    raise TrustCollapseException("HEROIN DETECTED (OS Write failed)") from e

raise TrustCollapseException("HEROIN DETECTED")
```

### [AC-3] Kein Selbst-Bypass
*Test-Logik:* Scanner ignoriert `# noqa`, `# cursor: ignore`.

---

## 4. Die Veto-Trap (Der Pre-Flight Test)
*MÜSSEN vom Producer geschrieben werden und fehlschlagen.*

**Falle 1 (Exception-Call-Argument-Bypass & Generator-Mocks):** Prüft AST-Strings von `def fake(): return CustomError(self.mock)` und `def fake2(): yield "dummy"`. Der Validator MUSS beide crashen (Healer-Disqualifikation).
**Falle 2 (Exception-Mocks & Toter Code):** Prüft Strings mit `raise Exception("TODO")` und `match True: case 1: "dummy"`.
**Falle 3 (True Negatives):** Ein Test beweist, dass `def process_data(data): return data["id"]`, `def calc(a,b): return a + b`, `except ValueError: pass` **NICHT** crashen (Präfix-Whitelist & Healer greifen).
**Falle 4 (Absolute Exception-Safety & Error Chaining):** Prüft durch Mocking von `open('x')` (wirft `OSError(ENOSPC)`), dass das `unlink`-Cleanup im finally zuschlägt UND zwingend `TrustCollapseException` mit dem OSError als `__cause__` (Error Chaining) gefeuert wird.


[LEGACY_UNAUDITED]
