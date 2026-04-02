import asyncio
import os
from dotenv import load_dotenv

# Lade Umgebungsvariablen (DSN für VPS-Postgres)
load_dotenv("/OMEGA_CORE/.env")

from src.db.predictive_matrix_client import predictive_matrix
from src.logic_core.bias_damper import BiasDamperEngine
from src.agents.agent_graph import MnemosyneFold

async def main():
    print("=== EMPIRISCHER BEWEIS: COGNITIVE MATRIX (Axiom 5 & 7) ===")
    
    # 1. Datenbank-Verbindung (Real)
    try:
        await predictive_matrix.client.connect()
        print("[+] SUCCESS: Verbindung zu PostgreSQL (VPS) hergestellt.")
    except Exception as e:
        print(f"[-] ERROR: DB Verbindung fehlgeschlagen: {e}")
        return

    intent = "TEST_EMPIRICAL_PROOF"
    context = "Dies ist ein Test der kardanischen Faltung mit echten Daten."

    # 2. Auslesen / Cold Start
    weights = await predictive_matrix.get_weights(intent, context)
    print(f"\n[1] LESE PREDICTIVE MATRIX (Start-Zustand):")
    print(f"    Prior-Gewicht (π): {weights['a_priori_weight']}")
    print(f"    Letzter Fehler (δ): {weights['ex_post_delta']}")

    # 3. Bias Berechnung
    damper = BiasDamperEngine()
    bias = damper.calculate_resonance_bias(weights["a_priori_weight"])
    print(f"\n[2] BIAS DAMPER ENGINE:")
    print(f"    Aus Gewicht {weights['a_priori_weight']} folgt Skepsis (Bias): {bias}")
    print(f"    -> LLM muss min. {1.0 - bias:.3f} Confidence liefern, um nicht als Dissonanz zu gelten.")

    # 4. Faltung (Mnemosyne Fold)
    folder = MnemosyneFold()
    
    # Simulate a successful observation (e.g., confidence 0.951)
    obs_success = 0.951
    err_success = folder.calculate_prediction_error(weights["a_priori_weight"], obs_success)
    next_pi_success = folder.calculate_next_precision(weights["a_priori_weight"], err_success)
    
    # Simulate a failed observation (e.g., confidence 0.049)
    obs_fail = 0.049
    err_fail = folder.calculate_prediction_error(weights["a_priori_weight"], obs_fail)
    next_pi_fail = folder.calculate_next_precision(weights["a_priori_weight"], err_fail)
    
    print(f"\n[3] FREE ENERGY PRINCIPLE (Bayesian Update):")
    print(f"    Bei Observation {obs_success} (Erfolg): PredError={err_success:.3f} -> π springt auf {next_pi_success}")
    print(f"    Bei Observation {obs_fail} (Scheitern): PredError={err_fail:.3f} -> π fällt auf {next_pi_fail}")

    # 5. Echter Schreibvorgang
    print(f"\n[4] PERSISTENZ (Schreibe echten Erfolg in DB...):")
    await predictive_matrix.update_matrix(intent, context, next_pi_success, err_success)
    
    # 6. Re-Verifikation
    weights_new = await predictive_matrix.get_weights(intent, context)
    print(f"    [+] VERIFIKATION: Neues Gewicht in DB ist exakt: {weights_new['a_priori_weight']}")
    
    await predictive_matrix.client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
