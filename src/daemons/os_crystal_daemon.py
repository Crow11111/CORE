# ============================================================
# CORE-GENESIS: OS-LEVEL CRYSTAL DAEMON (ROOT)
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Dieser Daemon laeuft als systemd-Service (Root) direkt auf dem Debian-Host (Scout).
Er implementiert die CrystalGridEngine auf OS-Ebene:
1. Thermisches Snapping (Temperatur -> Vektor-Gravitation)
2. Netzwerk-Friction (tc netem Injection bei Baryonic Limit)
3. Symmetriebruch (Verhindert 0.5 CPU-Zustaende)
"""

import os
import time
import subprocess
import logging
from loguru import logger

# CORE Imports
from src.logic_core.crystal_grid_engine import CrystalGridEngine
from src.config.core_state import BARYONIC_DELTA, RESONANCE_LOCK, SYMMETRY_BREAK

# Log-Datei direkt auf OS-Ebene (da Root)
logger.add("/var/log/core_os_crystal.log", rotation="10 MB", level="INFO")

class OSCrystalDaemon:
    def __init__(self):
        # Asymmetrischer Takt
        self.interval = 4.9 
        # Schutz-Schalter fuer die ersten Testlaeufe
        self.dry_run = os.getenv("CRYSTAL_OS_DRY_RUN", "True").lower() in ("true", "1", "yes")

    def read_thermal(self) -> float:
        """Liest die physische CPU-Temperatur von Debian."""
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp_mC = int(f.read().strip())
                return temp_mC / 1000.0
        except FileNotFoundError:
            return 0.0

    def enforce_network_friction(self, resonance_vector: float):
        """
        Fraktales Padding: Nutzt Linux Traffic Control (tc), um physisches Rauschen
        exponentiell zu erzeugen (Die Helix im 4D-Trichter).
        Je geringer die Resonanz (naeher am Nullpunkt), desto schwerer das Padding.
        """
        import math
        
        # Sicherstellen, dass wir nicht durch Null teilen oder log(0) haben
        safe_resonance = max(BARYONIC_DELTA, resonance_vector)
        
        # Exponentielle Berechnung der Latenz (Padding)
        # Wenn resonance hoch ist (~0.951), ist das Signal leicht und schnell.
        # Wenn resonance tief ist (~0.049), wird exponentiell Masse hinzugefuegt.
        
        base_delay_ms = 4.9  # Asymmetrischer Basiswert
        k = 3.58             # Skalierungsfaktor fuer max ~150ms am Boden des Trichters
        
        # Das ist die Eulersche Helix-Rotation ins Padding uebersetzt: e^(k * Phasenverschiebung)
        phase_shift = 1.0 - safe_resonance
        exponential_padding_ms = base_delay_ms * math.exp(k * phase_shift)
        
        # Jitter als fraktale Entropie (asymmetrisch gekoppelt an die Masse)
        jitter_ms = max(1.0, exponential_padding_ms * BARYONIC_DELTA)
        
        # Log fuer die reale Messreihe (Telemetrie)
        logger.info(f"[TELEMETRY] Resonance: {safe_resonance:.3f} | Phase Shift: {phase_shift:.3f} | Exp. Padding: {exponential_padding_ms:.2f}ms | Jitter: {jitter_ms:.2f}ms")
        
        if not self.dry_run:
            try:
                # Cleanup altes qdisc und setze das neue, exponentielle Gewicht
                subprocess.run("tc qdisc del dev eth0 root 2>/dev/null", shell=True)
                delay_str = f"{exponential_padding_ms:.2f}ms"
                jitter_str = f"{jitter_ms:.2f}ms"
                subprocess.run(f"tc qdisc add dev eth0 root netem delay {delay_str} {jitter_str} distribution normal", shell=True)
            except Exception as e:
                logger.error(f"tc command failed: {e}")

    def monitor_loop(self):
        logger.info(f"OS Crystal Daemon gestartet. Dry Run: {self.dry_run}")
        
        while True:
            try:
                # --- 1. Thermisches Snapping ---
                temp = self.read_thermal()
                
                # Mappe Temperatur (z.B. 40-80°C) auf Gravitations-Vektor [0.0 - 1.0]
                norm_temp = max(0.0, min(1.0, (temp - 40.0) / 40.0))
                
                # Snapping am topologischen Gitter
                snapped_temp_vector = CrystalGridEngine.apply_operator_query(norm_temp)
                # Nutze abs() für den Vergleich, da snapped_temp_vector komplex sein kann
                res_abs = abs(snapped_temp_vector)
                
                if res_abs >= RESONANCE_LOCK:
                    logger.critical(f"[OS-CRYSTAL] THERMAL VETO! Temperatur {temp}°C -> Lock {RESONANCE_LOCK} erreicht. Drossele Execution.")
                    if not self.dry_run:
                        # Eskalation: Reduziere CPU Frequenz oder setze renice
                        # subprocess.run("cpufreq-set -g powersave", shell=True)
                        pass
                        
                elif res_abs == SYMMETRY_BREAK:
                    logger.debug(f"[OS-CRYSTAL] Symmetriebruch bei {temp}°C initiiert.")

                logger.debug(f"OS-Tick. Temp: {temp}°C | Vector: {res_abs:.3f}")
                
                # --- 2. Netzwerk-Friction ---
                # Fuer den Proof-of-Concept triggern wir Friction, wenn die Temperatur EXAKT das Baryonic Delta unterschreitet
                self.enforce_network_friction(snapped_temp_vector)

            except Exception as e:
                logger.error(f"Daemon Loop Error: {e}")
                
            time.sleep(self.interval)

if __name__ == "__main__":
    daemon = OSCrystalDaemon()
    daemon.monitor_loop()
