#!/usr/bin/env python3
"""Testet Gravitator-Routing auf wuji_field."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def main():
    from src.logic_core.gravitator import route, route_to_wuji
    from src.network.chroma_client import query_wuji_field, query_wuji_via_gravitator

    queries = [
        "Simulationstheorie Indizien fuer virtuelle Realitaet",
        "Ring-0 Direktive Bias Check",
        "Session vom gestrigen Gespraech",
    ]

    print("=== GRAVITATOR ROUTE (legacy) ===\n")
    for q in queries:
        targets = route(q, top_k=2)
        print(f"Query: {q[:50]}...")
        for t in targets:
            print(f"  -> {t.name} (type={t.type}, score={t.score:.3f})")
        print()

    print("=== ROUTE_TO_WUJI ===\n")
    for q in queries:
        targets = route_to_wuji(q, top_k=2)
        print(f"Query: {q[:50]}...")
        for t in targets:
            print(f"  -> {t.name} type={t.type} score={t.score:.3f}")
        print()

    print("=== QUERY_WUJI_FIELD (type=evidence) ===\n")
    r = query_wuji_field("Quantencomputer Simulation", n_results=3, type_filter="evidence")
    ids = r.get("ids", [[]])[0]
    docs = r.get("documents", [[]])[0]
    metas = r.get("metadatas", [[]])[0]
    print(f"Treffer: {len(ids)}")
    for i, (uid, doc, meta) in enumerate(zip(ids[:3], docs[:3], metas[:3])):
        print(f"  [{i+1}] {uid} type={meta.get('type')} lpis={meta.get('lpis_base')}")
        print(f"      {str(doc)[:80]}...")
    print()

    print("=== QUERY_WUJI_VIA_GRAVITATOR ===\n")
    r = query_wuji_via_gravitator("Governance und Compliance Regeln", n_results=5, top_k_types=2)
    ids = r.get("ids", [[]])[0]
    metas = r.get("metadatas", [[]])[0]
    print(f"Treffer: {len(ids)}")
    for i, (uid, meta) in enumerate(zip(ids[:5], metas[:5])):
        print(f"  [{i+1}] {uid} type={meta.get('type')} source={meta.get('source_collection')}")
    print("\n=== TEST OK ===")


if __name__ == "__main__":
    main()
