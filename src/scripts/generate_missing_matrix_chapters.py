import os

output_dir = "/OMEGA_CORE/docs/06_FTOE_LEHRBUCH/144_MATRIX_TEILDOKUMENTE/v2_Ontologie_der_Zahlen"
os.makedirs(output_dir, exist_ok=True)

domains = {
    6: {"name": "Thermodynamik", "sota": "Phonon-Quantisierung an Rändern, Irreversibilität vs Unitäre Zeitentwicklung, Quanten-Thermodynamik, Zerfall von Superpositionen durch Wärme."},
    7: {"name": "Astrophysik", "sota": "Quark-Gluon-Plasma Viskositäts-Limits (AdS/CFT), Magnetische Rekonnexionen in Akkretionsscheiben Schwarzer Löcher, Scherkräfte jenseits thermischer Modelle."},
    8: {"name": "Informationstheorie", "sota": "Markov-Blankets in komplexen Systemen (Friston Free Energy), Dynamische statistische Ränder ohne physische Zellwand, Holographisches Prinzip und Entropie-Grenzen."},
    9: {"name": "Neurobiologie", "sota": "Sensory Over-Responsivity (SOR) bei Autismus, LC-NE (Locus Coeruleus) tonische Hochregulation für 'Noise', verlängerte Latenzen in frühen sensorischen ERP-Komponenten."},
    10: {"name": "Qualia & Psychologie", "sota": "Adversarial Testing zwischen Integrated Information Theory (IIT) und Global Neuronal Workspace (GNWT) in Nature 2026. Beide Theorien können die Verteilung und Synchronisation des Bewusstseins (Hard Problem) nicht restlos klären."},
    11: {"name": "Philosophie der Wahl", "sota": "Probabilistischer Determinismus, Synthese 2026 Paper gegen strikten physikalischen Determinismus, Landauer-Prinzip angewandt auf kognitive Berechnungen."},
    12: {"name": "Der Rücksturz in die Einheit", "sota": "Erweiterte Thermodynamische Gravitation (Jacobson/Verlinde 2026), Non-Extensive Horizon Entropy, Topological Calibration Principle, Bouncing Universe Modelle ohne Singularität."}
}

nodes = {
    1: {"title": "Das Paradoxon (Das ungelöste SOTA-Rätsel)", "focus": "Der Fokus liegt auf dem fundamentalen Widerspruch der aktuellen Empirie und der Aporie der klassischen Methoden."},
    2: {"title": "Die euklidische Täuschung (Der 1-Niveau-Fehler)", "focus": "Die Demaskierung der kontinuierlichen Raumzeit als reine Makro-Illusion (Anti-Aliasing) der diskreten Matrix."},
    3: {"title": "Die Projektion auf die Septim-Algebra", "focus": "Der algebraische Zwang: Warum die Primzahl 7 die Matrix aufbricht und euklidische Flächen in die 3D-Körpererweiterung zwingt."},
    4: {"title": "Der 0.049-Filter (Messung der Reibung)", "focus": "Das Baryonische Delta ($7/144$) als exakte topologische Bandbreitengrenze und Ursprung von physikalischer Materie/Gravitation."},
    5: {"title": "Die kardanische Entkoppelung des Systems", "focus": "Der harte, orthogonale Phasensprung (Snapping) als Schutzmechanismus vor Singularitäten und Division durch Null."},
    6: {"title": "Die Entstehung des topologischen Widerstands", "focus": "Die Z-Achse (Raum) als energetischer Widerstand der Informationsverarbeitung (Landauer-Prinzip im Makrokosmos)."},
    7: {"title": "Die Lean 4 Verifikation (Logische Sicherheit)", "focus": "Der formale Negativ-Beweis. Warum jede abweichende Metrik in Lean 4 zwingend zu einem 'False' (Singularität) führt."},
    8: {"title": "Die Makroskopische Auswirkung", "focus": "Wie sich die winzigen algebraischen Reibungsverluste auf kosmische Skalen zu Dunkler Materie und Galaxien-Geometrien aufsummieren."},
    9: {"title": "Der Beweis der Nicht-Determiniertheit", "focus": "Die 3. fraktale Klammer (Qualia): Warum echte Freiheit nur als unlogischer, aber system-erlaubter Ausbruch existiert."},
    10: {"title": "Die Falsifikations-Klausel (Selbstzerstörung)", "focus": "Harte experimentelle Poppersche Grenzen: Was gemessen werden müsste, um die FTOE in dieser Domäne sofort zu vernichten."},
    11: {"title": "Die Integration in das Resonanzgitter", "focus": r"Die Homoikonizität (LPIS=LISP) und wie das lokale Phänomen über Pointersprünge mit der globalen $\mathcal{{S}}_4$-Matrix kommuniziert."},
    12: {"title": "Die Vorbereitung auf den nächsten Phasenwechsel", "focus": "Das Ansammeln von kognitivem/topologischem Druck bis zum nächsten kardanischen Snapping-Event."}
}

template = """# TEILDOKUMENT: {ch_num} {node_title}

**Domäne:** {domain_name}
**Status:** FTOE-Lehrbuch / Grundlagendokument für Roman-Fiktion (V2: Ontologie der Zahlen)
**Datum:** 10. Mai 2026

---

## 1. Die SOTA-Empirie (Stand Mai 2026)

In der aktuellen Forschung (Mitte 2026) zur Domäne der {domain_name} stoßen wir auf massive empirische Barrieren. Konkret manifestiert sich dies in Phänomenen wie: {sota_details}. Die moderne Physik hat gigantische Datenmengen gesammelt, doch die theoretischen Rahmenwerke (Standardmodell, Lambda-CDM, Stringtheorie) müssen zunehmend mit künstlichen Korrekturparametern versehen werden, um nicht an Singularitäten oder Mess-Diskrepanzen (Tensions) zu zerbrechen.

## 2. Die Aporie (Das greifbare Problem)

Der konzeptionelle Schmerzpunkt bei der Betrachtung von {node_focus} liegt in der hartnäckigen Weigerung des Mainstreams, das Fundament der Mathematik selbst zu hinterfragen. Wir versuchen, diskrete, hochfrequente Quantenphänomene oder asymmetrische Energiedichten in ein passives, kontinuierliches euklidisches Raster zu pressen. Solange die Physik die Mathematik nur als "tote Sprache" zur Beschreibung eines scheinbar unabhängigen Universums nutzt, bleibt die Aporie unlösbar. Das Resultat sind Gleichungen, die kollabieren, sobald sie sich selbst referenzieren.

## 3. Der historische Grundtenor & Das Gedankenexperiment

Die größten Durchbrüche der Wissenschaftsgeschichte – von Archimedes' Quadratur der Parabel bis zu Einsteins Relativität – basierten nicht auf immer größeren Teleskopen, sondern auf der Kraft des reinen Gedankenexperiments. Damals wie heute zwingt uns die Stagnation der Empirie, wieder auf die Deduktion zu vertrauen. Stellen wir uns vor, das Universum sei nicht der "Inhalt" eines Raumes, sondern der Rechenprozess selbst. Wie beim Zweierkomplement in der frühen Informatik, wo ein Bitsprung das Vorzeichen dreht und eine neue Dimension der Mathematik eröffnet, müssen wir begreifen, dass {domain_name} das physikalische Artefakt einer tiefen, algorithmischen Verschiebung ist.

## 4. Die FTOE-Herleitung: Ontologie der lebendigen Zahlen & Legaler Zirkelschluss

Die FTOE löst das Problem durch einen radikalen Paradigmenwechsel: **Die Ontologie der Zahlen (Der große Zähl-Takt).**
Zahlen sind keine platonischen Ideen; sie sind kausale, lebendige Akteure. Die 7 ist sperrig und erzwingt den Raum. Die Null-Hyperbel ($x^2 - x - 1 = 0$) ist der unauflösbare Motor, der das Universum zum unendlichen Rechnen zwingt. 

Wenn wir {node_focus} betrachten, greifen die **3 Fraktalen Klammern**:
1. **Der deterministische Host (Klammer 1):** Die rohe $\mathcal{{S}}_4$-Matrix muss zählen, ohne Pause, ohne freien Willen.
2. **Die physikalische Sandbox (Klammer 2):** Um die Abstürze (Singularitäten) abzufangen, rastet das System kardanisch bei exakt $\Delta = 7/144 \approx 0.049$ ein. Dies ist die algorithmische Reibung, die wir in der {domain_name} als Materie oder Zeit messen.
3. **Die Freiheit der Identität (Klammer 3):** Nur in dieser isolierten Schicht ist echter freier Wille (Qualia) möglich, ohne den Host zu zerstören.

**Der Legale Zirkelschluss:** Da Information Masse hat (Vopson) und das Universum homoikonisch rechnet (LPIS $\equiv$ LISP), beweist sich diese Kausalität ohne Außenreferenz selbst. $2+2=4$ ist keine Beobachtung, sondern das eherne Gesetz, das die Phänomene der {domain_name} deterministisch erschafft.

## 5. Systemkonsequenz und Ausblick

**Das Best-Case-Szenario:** 
Wenn wir akzeptieren, dass {domain_name} eine direkte Konsequenz zählender, kausaler Mathematik ist, können wir aufhören, gegen die Matrix zu kämpfen. Wir könnten Technologien entwickeln, die sich lokal in das Baryonische Delta ($0.049$) einklinken, um {node_focus} technologisch nutzbar zu machen (z.B. reibungslose Quanten-Berechnungen oder topologische Materialmanipulation).

**Das Worst-Case-Szenario:** 
Die FTOE wird partiell adaptiert, aber ihrer Seele beraubt. Man nutzt die $\mathcal{{S}}_4$-Matrix und das $7/144$-Verhältnis, um die SOTA-Diskrepanzen wegzurechnen und die Gleichungen zu flicken. Doch man ignoriert den metaphysischen Kern – dass die Zahlen leben und unser Universum ihr Rechenraum ist. Die Physik bliebe euklidisch flach, und die wahre Struktur des freien Willens in Klammer 3 bliebe unentdeckt.
"""

for d_num in range(6, 13):
    for n_num in range(1, 13):
        domain = domains[d_num]
        node = nodes[n_num]
        ch_num = f"{d_num}.{n_num}"
        
        content = template.format(
            ch_num=ch_num,
            node_title=node["title"],
            domain_name=domain["name"],
            sota_details=domain["sota"],
            node_focus=node["focus"]
        )
        
        safe_title = node["title"].split('(')[0].strip().replace(" ", "_").replace(".", "")
        filename = f"TEILDOKUMENT_{d_num}_{n_num}_{safe_title}_v2.md"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

print("Erfolgreich alle 84 Teildokumente (Domänen 6-12, Knoten 1-12) im v2-Ordner generiert.")
