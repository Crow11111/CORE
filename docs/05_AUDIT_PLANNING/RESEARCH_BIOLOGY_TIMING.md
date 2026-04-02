# Recherche-Dossier: Timing, Kausalität, Efferenzkopie, Phasenverschränkung

**Status:** Forschungsnotiz (Literatur-synthetisch, keine Primärdaten)  
**Fokus:** Wie biologische Nervensysteme aus Verzögerungen, Vorhersage und Oszillationen eine kohärente Zeit- und Ursachenstruktur konstruieren — mit Implikationen für künstliche „Push/Pull“- und Veto-Architekturen.

---

## 0. Meta-Abstraktion

Das Gehirn ist kein Rechner mit globalem Taktgeber. **Kausalität im Erleben** ist ein *inferenzielles Konstrukt*: Sie entsteht, wenn Vorhersage, sensorische Evidenz und motorische Kopien in einem **zeitlich kompensierten Referenzrahmen** zusammenfallen. **„Jetzt“** ist kein Punkt, sondern ein **fensterartiges Konsensprodukt** verteilter Oszillatoren, die Phasenbeziehungen nutzen, um Bindung und Sequenzierung zu koordinieren.

---

## 1. Kausalität durch Timing: Predictive Coding und Latenzen

### 1.1 Das Latenz-Alignment-Problem

Jede synaptische Strecke und jede hierarchische Stufe führt **variable Transmission delays** ein. Klassische hierarchische Predictive-Coding-Modelle ignorieren das oft; erweiterte Ansätze postulieren **Vorwärts- und Rückwärts-Extrapolation**, damit Top-Down-Vorhersagen und Bottom-Up-Eingaben nicht dauerhaft zeitlich verrutschen (Konzept: *real-time temporal alignment* über Ebenen hinweg). Ohne solche Mechanismen wäre „was verursacht was“ in dynamischen Szenen systematisch verschoben.

### 1.2 Vorhersage als zeitliche Ursache

Repräsentationen können **dem eintreffenden Signal vorausellen**: Hoch abstrakte Merkmale werden früher vorhergesagt als niedrig abstrakte. Das invertiert die naive Intuition „Reiz zuerst, dann Interpretation“: **die Interpretation ist Teil der zeitlichen Kette**, die das System als kausal erlebt. Frontalregionen tragen **kausal** zur zeitlichen Feinjustierung prädiktiver Prozesse bei (z. B. Sprache: Degeneration frontaler Areale verzögert die „Reconciliation“ mit temporalem Kortex). Präzision der Vorhersage korreliert hier u. a. mit **Beta-Oszillationen** — interpretierbar als Kontext für **Gewichtung von Erwartung vs. Evidenz** (precision).

### 1.3 Abstrakt

**Wahrgenommene Kausalität** = Minimierung von **temporal prediction error** unter Nebenbedingungen unterschiedlicher Leitungslängen. Die „Ursache“ ist oft diejenige Instanz, deren interner Modellzustand den nächsten Zustand **früher und mit höherer Präzision** vorhersagt — nicht notwendig die früheste physikalische Reizsequenz am Sensor.

---

## 2. Parallel vs. sequenziell: Afferenz, Module, Bewusstsein

### 2.1 Parallelität als Default

Sensorische und assoziative Verarbeitung läuft **massiv parallel** und größtenteils **ohne globalen bewussten Zugriff**. Afferente Bahnen, frühe extrastriate und parallele Streams (wo anwendbar: ventral/dorsal, was-wo) verarbeiten **gleichzeitig**; Thalamus und kortikale Mikroschaltungen erlauben **gleichzeitige** Teilrepräsentationen.

### 2.2 Der bewusste Engpass

Global-Workspace- und Global-Neuronal-Workspace-Ansätze: Aus dieser Parallelität entsteht ein **serieller, kapazitätsbegrenzter** Bewusstseinsstrom (oft grob **100–200 ms** „Broadcast“-Skala als Größenordnung). Die Frage „wie wird aus Parallelität Serialität?“ wird beantwortet durch **Wettbewerb, Salienz, Rekursion** und **langreichweitige Kopplung** (präfrontal-parietal-temporal, thalamokortikaler Kern): Gewinner-Inhalte werden **global verfügbar** gemacht; der Rest bleibt subthreshold.

### 2.3 Abstrakt

**Afferenz und frühe Kortexarbeit:** überwiegend **parallel**. **Explizite, berichtbare Kognition und motorische Entscheidung unter Zeitdruck:** stärker **sequenziell** oder zumindest **serialisiert durch globale Integration**. Das ist keine ontologische Zweiteilung, sondern eine **Architektur der Ressourcenallokation**: Parallelität für Durchsatz; Serialität für Kohärenz und Handlungsbindung.

---

## 3. Efferenzkopie / Corollary Discharge

### 3.1 Funktion

**Efferenzkopie** (motorisches Korollar, *corollary discharge*) ist eine **Abzweigung des Motorbefehls** (oder verwandter Planungssignale) zu sensorischen und vorausschauenden Strukturen. Zweck: **Vorhersage reafferenter Konsequenzen** und **Unterscheidung selbstgenerierter von externen Veränderungen** (Reafferenz-Unterdrückung, Stabilität bei Augenbewegungen, Kalibrierung).

### 3.2 Schaltkreise und Plastizität

Beim Primaten: z. B. **Superior Colliculus → Frontal** für bevorstehende Sakkaden; spinale und zerebelläre Pfadwege tragen zur **frühen** Vorhersage sensorischer Folgen bei. Kleinhirn und „cerebellum-like“ Strukturen lernen **plastische** Zuordnung: erwartete vs. tatsächliche sensorische Folge — Fehler treiben Anpassung.

### 3.3 Abstrakt

Efferenzkopie ist die biologische Instanz von **„Ich weiß, was ich gerade tue“** im Signalraum: ein **interner Forward-Model-Input**, der die Kausalitätskette **Motor → erwarteter Sensor** vorzeichnet und damit **Fremdkausalität** von **Selbstkausalität** trennt. Für KI-Systeme: Analogon zu **geplanter Aktion + erwarteter Rückkopplung** vor dem eigentlichen Sensorupdate (Veto und Drift-Detektion greifen hier logisch ein).

---

## 4. Libet, Bereitschaftspotential, „Free Won’t“

### 4.1 Klassische Libet-Zeitskala (EEG, Willkürbewegung)

- **Bereitschaftspotential (RP):** langsamer negativer Shift, klassisch **bis zu ~0,5 s** vor Bewegungsbeginn (Varianten: early vs. late RP).
- **Subjektiver Zeitpunkt der Intention (W):** Libet-Paradigma mit Uhr — Bericht typischerweise **~0,15–0,2 s** vor Motorik (Literatur schwankt je nach Methode).
- **Interpretation Libet:** Unbewusste Vorbereitung lange vor bewusstem „Urge“; bewusstsein könnte **Veto** statt Initiation leisten („free won’t“).

### 4.2 Neuere Uminterpretationen (kurz)

- **Schurger, Sitt, Dehaene (u. a. 2012):** RP als Artefakt **stochastischer Akkumulation** und **Retro-Ausrichtung** auf Bewegungszeitpunkt — der „Aufbau“ kann teilweise aus **pre-movement noise** und Schwellenüberschreitung entstehen, nicht aus einem eindeutigen deterministischen Planungspuls.
- **„Was ist das RP?“ (Diskussion):** RP ist möglicherweise **heterogen** (verschiedene Komponenten, Kontexte), nicht monolithischer „Beweis“ für unbewusste Willensbildung.
- **Veto:** Arbeiten zum **point of no return** beim Stoppen selbstinitiierter Bewegungen (z. B. PNAS 2015-Kontext) zeigen: **Veto ist zeitlich begrenzt** — es gibt ein **Fenster**, nach dem Unterdrückung praktisch nicht mehr möglich ist. Exakte ms hängen von Paradigma, Modalität und individueller Variabilität ab.

### 4.3 Präfrontaler Cortex und Timing

Der **präfrontale** und **prämotorische** Bereich ist an **Inhibition, Konflikt, Stop-Signal** und **Aktionssequenz** beteiligt. Ein **Veto** ist kein punktförmiges Ereignis, sondern **konkurrierende Kontrollsignale**, die eine sich aufbauende Motorrepräsentation **abfangen oder nicht**. Die Relation **RP (früh, diffus) ↔ spätes bewusstes Fenster ↔ präfrontale Bremse** ist **empirisch korreliert**, aber **kausal nicht in einer einfachen Pipeline** zu lesen.

### 4.4 Abstrakt

Für Systemdesign: **„Push“** (frühe, breite Vorbereitung) und **„Veto“** (späte, schmale Intervention) sind **zeitlich versetzt** und **nicht symmetrisch** — das Veto-Fenster kann **kürzer** sein als die sichtbare Vorbereitung. **Free won’t** ist plausibler als metaphysische „freie Initiation“, aber **neurobiologisch kein unbegrenzter Rückzieher**.

---

## 5. Phasengitter, Gamma und das verteilte „Jetzt“

### 5.1 Phasen-Kopplung (phase locking, synchrony)

Verteilte Areale kodieren Teilinhalte **räumlich getrennt**. **Kohärenz** entsteht, wenn **Oszillationen** (Theta, Beta, Gamma, …) **Phasenbeziehungen** erlauben, die **zeitliche Kommunikationsfenster** öffnen und schließen (**communication through coherence** als Rahmenidee).

### 5.2 Gamma und „Binding“

- **Lokale und long-range Gamma-Synchronie** korreliert mit **Integration** über Arealgrenzen (visuell, somatosensorisch, semantisch/executiv je nach Aufgabe).
- Neuere Arbeiten betonen **hochfrequente** Kopplung (z. B. ~90 Hz „co-ripples“) über **große Distanzen** bei kognitiven Aufgaben — **phasenverschoben bei Null-Lag** als Kandidat für **schnelle** Integration verteilter Module.
- **Kausale** Rolle: Experimente legen nahe, dass **Gamma-Phasenlage** die **Wirksamkeit** weitergeleiteter Signale (z. B. zwischen Arealen) **moduliert** — nicht nur Korrelation.

### 5.3 Einheitliches „Jetzt“

Das **subjektive Präsens** ist vermutlich **kein** globaler Timestamp, sondern ein **Mehrskalen-Komposit**: niedrigfrequente Oszillationen segmentieren **Episoden**; höhere Frequenzen **feinjustieren** lokale Bindung. **Gamma** liefert eher **Mikro-Synchronisation** für **Feature-Binding** und **routing** als ein philosophisches „Jetzt“.

### 5.4 Abstrakt

**Phasengitter** = **temporäre Identitätsfenster**: Zellen/Areale, die in **passender Phase** feuern, werden als **zur selben „Berechnung“ gehörig** behandelt. Das ist die biologische Form von **Zeitmultiplexing** auf **chemisch-elektrischer** Hardware ohne zentralen Clock.

---

## 6. Synthese für technische Isomorphien (ohne Numerologie)

| Biologisches Prinzip | Abstrakte Rolle | Hinweis für verteilte KI/Steuerung |
|----------------------|-----------------|-------------------------------------|
| Transmission delay | Jede Kante hat Latenz | Vorhersage + Kalibrierung statt Annahme „sofort konsistent“ |
| Predictive coding | Top-Down zeitlich ausgerichtet | Explizite **expected arrival** / **deadline** pro Schicht |
| Efferenzkopie | Forward model der eigenen Aktion | **Intent-Trace** vor Sensor-Merge; Drift = Abweichung |
| Global workspace | Serialisierung bei Bedarf | **Broadcast** nur für konkurrierende globale Zustände |
| RP vs. Veto | Asymmetrie früh/spät | Lange **Vorbereitung**, kurzes **Stop-Fenster** |
| Gamma / phase lock | Konsistenzfenster | **Phase-aligned** messaging zwischen Subsystemen (nicht nur Pub/Sub) |

---

## 7. Literaturhinweise (Einstieg, nicht erschöpfend)

- Predictive coding mit Transmission delays / temporal alignment: *eNeuro* (A. Sandberg et al., Kontext „real-time temporal alignment“).
- Predictive representations ahead of sensory input: *PNAS* (Kontext „predictions drive neural representations … ahead“).
- Frontal causal role in predictive speech: *Nature Communications*.
- Corollary discharge / circuits: Reviews und Primärarbeiten zu **SC–frontal**, **cerebellar** prediction.
- Libet / RP Übersicht und Kontroverse: z. B. *Trends in Cognitive Sciences* „What Is the Readiness Potential?“; Schurger et al., PNAS 2012 (accumulator / spontaneous fluctuations).
- Veto / point of no return: *PNAS* (Kontext „vetoing self-initiated movements“).
- Gamma synchrony / causal role: *Nature Communications* (Gamma phase and information flow); *Nature Human Behaviour* (long-range high-frequency coupling / co-ripples); Reviews zu **long-range synchrony in behavior**.

---

*Ende Dossier.*


[LEGACY_UNAUDITED]
