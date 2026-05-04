import re

with open('/OMEGA_CORE/docs/01_CORE_DNA/FTOE_Theorie_der_latenten_Zeit_V1_Final.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Fixes
text = text.replace('Phasen-Vektors der Phasen-Vektor ($\\Theta$)', 'Phasen-Vektors ($\\Theta$)')
text = text.replace('Katalytische der Operator ($\\hat{\\Phi}$)-Resonanz', 'Katalytische Operator ($\\hat{\\Phi}$)-Resonanz')
text = text.replace('der der irrationale Vortrieb ($\\pi$)-Rotation', 'der $\\pi$-Rotation')
text = text.replace('180° (der irrationale Vortrieb ($\\pi$) rad)', '180° ($\\pi$ rad)')
text = text.replace('Operator der Operator ($\\hat{\\Phi}$)', 'Operator ($\\hat{\\Phi}$)')
text = text.replace('Latenz der der irrationale Vortrieb ($\\pi$)-Rotation', 'Latenz der $\\pi$-Rotation')
text = text.replace('Phasen-Vektor (der Phasen-Vektor ($\\Theta$))', 'Phasen-Vektor ($\\Theta$)')

with open('/OMEGA_CORE/docs/01_CORE_DNA/FTOE_Theorie_der_latenten_Zeit_V1_Final.md', 'w', encoding='utf-8') as f:
    f.write(text)

print("Cleanup 2 complete.")
