import subprocess
import time

print("Starte Ollama Anfrage (Gemma 4 e4b)...")
proc = subprocess.Popen([
    "ollama", "run", "gemma4:e4b", 
    "Erkläre die Simulationstheorie sehr detailliert in 1000 Wörtern. Nutze all deine Rechenkapazität."
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Länger warten, da das Modell 9.6 GB groß ist und in den VRAM geladen werden muss
time.sleep(12)

print("\n--- NVIDIA-SMI OUTPUT (GPU BEWEIS) ---")
subprocess.run(["nvidia-smi"])
proc.terminate()
