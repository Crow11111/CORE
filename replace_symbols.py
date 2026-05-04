import re

def replace_symbols(text):
    # Dictionary of symbols and their semantic anchors
    replacements = [
        (r'\$\\pi\$', r'der irrationale Vortrieb ($\\pi$)'),
        (r'\$\\Omega_b\$', r'das Baryonische Delta ($\\Omega_b$)'),
        (r'\$\\Theta\$', r'der Phasen-Vektor ($\\Theta$)'),
        (r'\$\\hat\{\\Phi\}\$', r'der Operator ($\\hat{\\Phi}$)'),
        (r'\$t_p\$', r'die Planck-Zeit ($t_p$)'),
        (r'\$E_\{snap\}\$', r'die Snapping-Energie ($E_{snap}$)'),
        (r'\$S\$', r'die Struktur/Resonanz ($S$)'),
        (r'\$P\$', r'die Physik/Hardware ($P$)'),
        (r'\$L\$', r'die Latenz/Logik ($L$)'),
        (r'\$I\$', r'die Information/Daten ($I$)')
    ]
    
    # We only replace if the symbol is NOT already preceded by its anchor.
    # To do this safely, we first replace ALL occurrences, then we clean up the redundancies.
    
    for pattern, replacement in replacements:
        text = re.sub(pattern, lambda m, r=replacement: r, text)
        
    # Clean up exact duplicates
    text = text.replace(r'der irrationale Vortrieb (der irrationale Vortrieb ($\pi$))', r'der irrationale Vortrieb ($\pi$)')
    text = text.replace(r'das Baryonische Delta (das Baryonische Delta ($\Omega_b$))', r'das Baryonische Delta ($\Omega_b$)')
    text = text.replace(r'der Phasen-Vektor (der Phasen-Vektor ($\Theta$))', r'der Phasen-Vektor ($\Theta$)')
    text = text.replace(r'der Operator (der Operator ($\hat{\Phi}$))', r'der Operator ($\hat{\Phi}$)')
    text = text.replace(r'die Planck-Zeit (die Planck-Zeit ($t_p$))', r'die Planck-Zeit ($t_p$)')
    text = text.replace(r'die Snapping-Energie (die Snapping-Energie ($E_{snap}$))', r'die Snapping-Energie ($E_{snap}$)')
    text = text.replace(r'die Struktur/Resonanz (die Struktur/Resonanz ($S$))', r'die Struktur/Resonanz ($S$)')
    text = text.replace(r'die Physik/Hardware (die Physik/Hardware ($P$))', r'die Physik/Hardware ($P$)')
    text = text.replace(r'die Latenz/Logik (die Latenz/Logik ($L$))', r'die Latenz/Logik ($L$)')
    text = text.replace(r'die Information/Daten (die Information/Daten ($I$))', r'die Information/Daten ($I$)')

    # Clean up variations where the anchor was already there but without parentheses
    text = text.replace(r'irrationale Vortrieb der irrationale Vortrieb ($\pi$)', r'irrationale Vortrieb ($\pi$)')
    text = text.replace(r'Baryonische Delta das Baryonische Delta ($\Omega_b$)', r'Baryonische Delta ($\Omega_b$)')
    text = text.replace(r'Phasen-Vektor der Phasen-Vektor ($\Theta$)', r'Phasen-Vektor ($\Theta$)')
    text = text.replace(r'Operator der Operator ($\hat{\Phi}$)', r'Operator ($\hat{\Phi}$)')
    text = text.replace(r'Planck-Zeit die Planck-Zeit ($t_p$)', r'Planck-Zeit ($t_p$)')
    text = text.replace(r'Snapping-Energie die Snapping-Energie ($E_{snap}$)', r'Snapping-Energie ($E_{snap}$)')
    text = text.replace(r'Struktur die Struktur/Resonanz ($S$)', r'Struktur/Resonanz ($S$)')
    text = text.replace(r'Physik die Physik/Hardware ($P$)', r'Physik/Hardware ($P$)')
    text = text.replace(r'Latenz die Latenz/Logik ($L$)', r'Latenz/Logik ($L$)')
    text = text.replace(r'Information die Information/Daten ($I$)', r'Information/Daten ($I$)')
    
    # Also handle cases with articles
    text = text.replace(r'der der irrationale Vortrieb ($\pi$)', r'der irrationale Vortrieb ($\pi$)')
    text = text.replace(r'das das Baryonische Delta ($\Omega_b$)', r'das Baryonische Delta ($\Omega_b$)')
    text = text.replace(r'der der Phasen-Vektor ($\Theta$)', r'der Phasen-Vektor ($\Theta$)')
    text = text.replace(r'dem der Operator ($\hat{\Phi}$)', r'dem Operator ($\hat{\Phi}$)')
    text = text.replace(r'den der Operator ($\hat{\Phi}$)', r'den Operator ($\hat{\Phi}$)')
    text = text.replace(r'die die Planck-Zeit ($t_p$)', r'die Planck-Zeit ($t_p$)')
    text = text.replace(r'die die Snapping-Energie ($E_{snap}$)', r'die Snapping-Energie ($E_{snap}$)')
    text = text.replace(r'die die Struktur/Resonanz ($S$)', r'die Struktur/Resonanz ($S$)')
    text = text.replace(r'die die Physik/Hardware ($P$)', r'die Physik/Hardware ($P$)')
    
    # Fix the math blocks
    # If the symbol is inside a math block like `$$ \Theta = ... $$` it shouldn't be replaced.
    # We can revert replacements inside `$$ ... $$`
    def revert_math_blocks(match):
        m = match.group(0)
        # Revert all replacements inside this block
        m = m.replace(r'der irrationale Vortrieb ($\pi$)', r'\pi')
        m = m.replace(r'das Baryonische Delta ($\Omega_b$)', r'\Omega_b')
        m = m.replace(r'der Phasen-Vektor ($\Theta$)', r'\Theta')
        m = m.replace(r'der Operator ($\hat{\Phi}$)', r'\hat{\Phi}')
        m = m.replace(r'die Planck-Zeit ($t_p$)', r't_p')
        m = m.replace(r'die Snapping-Energie ($E_{snap}$)', r'E_{snap}')
        m = m.replace(r'die Struktur/Resonanz ($S$)', r'S')
        m = m.replace(r'die Physik/Hardware ($P$)', r'P')
        m = m.replace(r'die Latenz/Logik ($L$)', r'L')
        m = m.replace(r'die Information/Daten ($I$)', r'I')
        return m
        
    text = re.sub(r'\$\$.*?\$\$', revert_math_blocks, text, flags=re.DOTALL)
    
    # Revert replacements inside specific contexts like 180° ($\pi$ rad)
    text = text.replace(r'180° (der irrationale Vortrieb ($\pi$) rad)', r'180° ($\pi$ rad)')
    
    # Fix specific grammar issues
    text = text.replace(r'Katalytische der Operator ($\hat{\Phi}$)-Resonanz', r'Katalytische Operator ($\hat{\Phi}$)-Resonanz')
    text = text.replace(r'des der Phasen-Vektor ($\Theta$)', r'des Phasen-Vektors ($\Theta$)')
    text = text.replace(r'des der irrationale Vortrieb ($\pi$)', r'des irrationalen Vortriebs ($\pi$)')
    text = text.replace(r'des das Baryonische Delta ($\Omega_b$)', r'des Baryonischen Deltas ($\Omega_b$)')
    text = text.replace(r'des der Operator ($\hat{\Phi}$)', r'des Operators ($\hat{\Phi}$)')
    
    return text

with open('/OMEGA_CORE/docs/01_CORE_DNA/FTOE_Theorie_der_latenten_Zeit_V1_Final.md', 'r', encoding='utf-8') as f:
    content = f.read()

new_content = replace_symbols(content)

with open('/OMEGA_CORE/docs/01_CORE_DNA/FTOE_Theorie_der_latenten_Zeit_V1_Final.md', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Replacement complete.")
