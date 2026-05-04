import re

with open('/OMEGA_CORE/docs/01_CORE_DNA/FTOE_Theorie_der_latenten_Zeit_V1_Final.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Fixes
text = text.replace(r'Phasen-Vektors der Phasen-Vektor ($\Theta$)', r'Phasen-Vektors ($\Theta$)')
text = text.replace(r'Phasen-Vektor (der Phasen-Vektor ($\Theta$))', r'Phasen-Vektor ($\Theta$)')
text = text.replace(r'Phasen-Vektor der Phasen-Vektor ($\Theta$)', r'Phasen-Vektor ($\Theta$)')
text = text.replace(r'Wert der Phasen-Vektor ($\Theta$)', r'Wert ($\Theta$)')

text = text.replace(r'Planck-Zeit (die Planck-Zeit ($t_p$))', r'Planck-Zeit ($t_p$)')
text = text.replace(r'Planck-Zeit die Planck-Zeit ($t_p$)', r'Planck-Zeit ($t_p$)')

text = text.replace(r'Operator der Operator ($\hat{\Phi}$)', r'Operator ($\hat{\Phi}$)')
text = text.replace(r'Operator (der Operator ($\hat{\Phi}$))', r'Operator ($\hat{\Phi}$)')

text = text.replace(r'Vortrieb der irrationale Vortrieb ($\pi$)', r'Vortrieb ($\pi$)')
text = text.replace(r'Vortrieb (der irrationale Vortrieb ($\pi$))', r'Vortrieb ($\pi$)')

text = text.replace(r'Quantisierung (das Baryonische Delta ($\Omega_b$))', r'Quantisierung ($\Omega_b$)')
text = text.replace(r'Baryonischen Deltas ($\Omega_b = 0.049$)', r'Baryonischen Deltas ($\Omega_b = 0.049$)')

text = text.replace(r'Struktur (die Struktur/Resonanz ($S$))', r'Struktur ($S$)')
text = text.replace(r'Physik (die Physik/Hardware ($P$))', r'Physik ($P$)')

text = text.replace(r'180° (der irrationale Vortrieb ($\pi$) rad)', r'180° ($\pi$ rad)')
text = text.replace(r'der der irrationale Vortrieb ($\pi$)-Rotation', r'der $\pi$-Rotation')

text = text.replace(r'Energie die Snapping-Energie ($E_{snap}$)', r'Energie ($E_{snap}$)')

text = text.replace(r'Reibung der Phasen-Vektor ($\Theta$)', r'Reibung ($\Theta$)')
text = text.replace(r'Latenz, die der irrationale Vortrieb ($\pi$)', r'Latenz, die der irrationale Vortrieb ($\pi$)') # this is fine

text = text.replace(r'die der Phasen-Vektor ($\Theta$) für das Einrasten', r'die der Phasen-Vektor ($\Theta$) für das Einrasten') # this is fine

with open('/OMEGA_CORE/docs/01_CORE_DNA/FTOE_Theorie_der_latenten_Zeit_V1_Final.md', 'w', encoding='utf-8') as f:
    f.write(text)

print("Cleanup complete.")
