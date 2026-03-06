"""
Patch für Pydantic v1 Compat-Layer (pydantic.v1) auf Python 3.14+

PROBLEM:
  Python 3.14 (PEP 649) verwendet "lazy annotations" - __annotations__
  ist im Metaclass-Namespace leer. Stattdessen gibt es __annotate_func__,
  die mit annotationlib.call_annotate_function() aufgerufen werden muss.
  Pydantic v1 (und der pydantic.v1 Compat-Layer in Pydantic v2) weiß das
  nicht und scheitert mit:
    ConfigError: unable to infer type for attribute "..."

LÖSUNG:
  In pydantic/v1/main.py wird die Annotation-Extraktion gepatcht, sodass
  auf Python 3.14+ __annotate_func__ genutzt wird.
  In chromadb/config.py werden Felder ohne Type-Annotations korrigiert.

NUTZUNG:
  python scripts/patch_pydantic_v1_py314.py
  (nach jedem chromadb/pydantic upgrade erneut ausführen)
"""
import sys
import os
import site


def find_site_packages():
    """Findet das site-packages Verzeichnis, in dem pydantic installiert ist."""
    for p in site.getusersitepackages(), *site.getsitepackages():
        if isinstance(p, str) and os.path.isdir(os.path.join(p, "pydantic", "v1")):
            return p
    for p in sys.path:
        if "site-packages" in p and os.path.isdir(os.path.join(p, "pydantic", "v1")):
            return p
    raise FileNotFoundError("pydantic.v1 nicht in site-packages gefunden")


def patch_pydantic_v1_main(sp: str) -> bool:
    target = os.path.join(sp, "pydantic", "v1", "main.py")
    if not os.path.isfile(target):
        print(f"  SKIP: {target} nicht gefunden")
        return False

    with open(target, "r", encoding="utf-8") as f:
        content = f.read()

    marker = "__annotate_func__"
    if marker in content:
        print(f"  OK: {target} bereits gepatcht")
        return True

    if "import sys\n" not in content:
        content = "import sys\n" + content

    old = (
        "            annotations = resolve_annotations("
        "namespace.get('__annotations__', {}), "
        "namespace.get('__module__', None))"
    )
    new = (
        "            raw_annotations = namespace.get('__annotations__', {})\n"
        "            if not raw_annotations and sys.version_info >= (3, 14):\n"
        "                _annotate_func = namespace.get('__annotate_func__')\n"
        "                if _annotate_func is not None:\n"
        "                    import annotationlib\n"
        "                    raw_annotations = annotationlib.call_annotate_function(\n"
        "                        _annotate_func, annotationlib.Format.VALUE\n"
        "                    )\n"
        "            annotations = resolve_annotations("
        "raw_annotations, namespace.get('__module__', None))"
    )

    if old not in content:
        print(f"  WARN: Erwartetes Pattern nicht gefunden in {target}")
        print(f"        Manuelle Prüfung nötig.")
        return False

    content = content.replace(old, new)

    with open(target, "w", encoding="utf-8") as f:
        f.write(content)

    pyc = target + "c"
    if os.path.isfile(pyc):
        os.remove(pyc)

    print(f"  PATCHED: {target}")
    return True


def patch_chromadb_config(sp: str) -> bool:
    target = os.path.join(sp, "chromadb", "config.py")
    if not os.path.isfile(target):
        print(f"  SKIP: {target} nicht gefunden")
        return False

    with open(target, "r", encoding="utf-8") as f:
        content = f.read()

    changed = False

    # Fix: Validator vor dem Feld -> Feld vor dem Validator
    old_validator_order = (
        '    @validator("chroma_server_nofile", pre=True, always=True, allow_reuse=True)\n'
        "    def empty_str_to_none(cls, v: str) -> Optional[str]:\n"
        "        if type(v) is str and v.strip() == \"\":\n"
        "            return None\n"
        "        return v\n"
        "\n"
        "    chroma_server_nofile: Optional[int] = None"
    )
    new_validator_order = (
        "    chroma_server_nofile: Optional[int] = None\n"
        "\n"
        '    @validator("chroma_server_nofile", pre=True, always=True, allow_reuse=True)\n'
        "    def empty_str_to_none(cls, v: str) -> Optional[str]:\n"
        "        if type(v) is str and v.strip() == \"\":\n"
        "            return None\n"
        "        return v"
    )
    if old_validator_order in content:
        content = content.replace(old_validator_order, new_validator_order)
        changed = True

    # Fix: Felder ohne Type-Annotations
    fixes = [
        ('    chroma_coordinator_host = "localhost"', '    chroma_coordinator_host: str = "localhost"'),
        ('    chroma_logservice_host = "localhost"', '    chroma_logservice_host: str = "localhost"'),
        ('    chroma_logservice_port = 50052', '    chroma_logservice_port: int = 50052'),
    ]
    for old_line, new_line in fixes:
        if old_line in content:
            content = content.replace(old_line, new_line)
            changed = True

    if not changed:
        print(f"  OK: {target} bereits gepatcht oder kein Fix nötig")
        return True

    with open(target, "w", encoding="utf-8") as f:
        f.write(content)

    pyc = target + "c"
    if os.path.isfile(pyc):
        os.remove(pyc)

    print(f"  PATCHED: {target}")
    return True


def main():
    if sys.version_info < (3, 14):
        print(f"Python {sys.version} < 3.14 - kein Patch nötig.")
        return

    print(f"Python {sys.version}")
    print("Suche site-packages...")

    try:
        sp = find_site_packages()
    except FileNotFoundError as e:
        print(f"FEHLER: {e}")
        sys.exit(1)

    print(f"  -> {sp}")
    print()

    print("[1/2] Patche pydantic.v1.main ...")
    ok1 = patch_pydantic_v1_main(sp)

    print("[2/2] Patche chromadb.config ...")
    ok2 = patch_chromadb_config(sp)

    print()
    if ok1 and ok2:
        print("FERTIG. ChromaDB sollte jetzt mit Python 3.14 funktionieren.")
        print("Test: python -c \"import chromadb; print(chromadb.PersistentClient(path='./test_chroma'))\"")
    else:
        print("WARNUNG: Nicht alle Patches konnten angewendet werden.")
        sys.exit(1)


if __name__ == "__main__":
    main()
