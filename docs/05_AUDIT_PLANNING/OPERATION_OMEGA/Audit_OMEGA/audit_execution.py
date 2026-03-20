import json
import numpy as np
from scipy import stats
from collections import Counter
import math

# Daten laden
with open('audit_data.json', 'r') as f:
    data = json.load(f)

values = data['data_points']

# 1. Benford's Law Test - Erste Ziffern
def extract_first_digits(numbers):
    first_digits = []
    for num in numbers:
        if num > 0:
            first_digit = int(str(f"{num:.10e}").split('e')[0][0])
            if first_digit != 0:
                first_digits.append(first_digit)
    return first_digits

first_digits = extract_first_digits(values)
digit_counts = Counter(first_digits)

# Benford's Law erwartete Verteilung
benford_expected = {d: math.log10(1 + 1/d) for d in range(1, 10)}

# Chi-Quadrat Test
observed = [digit_counts.get(d, 0) for d in range(1, 10)]
expected = [len(first_digits) * benford_expected[d] for d in range(1, 10)]

chi2_stat, benford_p_value = stats.chisquare(observed, expected)

# 2. Zipf-Verteilung R²
log_ranks = np.log(range(1, len(values) + 1))
log_values = np.log([abs(v) if v > 0 else 1e-10 for v in sorted(values, reverse=True)])

correlation_matrix = np.corrcoef(log_ranks, log_values)
zipf_r_squared = correlation_matrix[0, 1] ** 2

# 3. Konvergenz gegen 0.049 und Phi (1.618)
target_049 = 0.049
target_phi = 1.618034

# Abstand zu 0.049
distances_049 = [abs(v - target_049) for v in values]
min_distance_049 = min(distances_049)
convergence_049 = 1 / (1 + min_distance_049)

# Abstand zu Phi
distances_phi = [abs(v - target_phi) for v in values]
min_distance_phi = min(distances_phi)
convergence_phi = 1 / (1 + min_distance_phi)

# 4. Kumulative Signifikanz Z-Score
# Fibonacci-ähnliche Sequenz erkennen
fibonacci_ratios = []
for i in range(1, len(values)-1):
    if values[i] != 0:
        ratio = values[i+1] / values[i]
        fibonacci_ratios.append(ratio)

# Z-Score berechnen
if len(fibonacci_ratios) > 1:
    mean_ratio = np.mean(fibonacci_ratios)
    std_ratio = np.std(fibonacci_ratios)
    z_score = abs(mean_ratio - target_phi) / (std_ratio / math.sqrt(len(fibonacci_ratios))) if std_ratio > 0 else 0
else:
    z_score = 0

# Strukturelle Analyse
phi_occurrences = sum(1 for v in values if abs(v - target_phi) < 0.001)
constant_049_occurrences = sum(1 for v in values if abs(v - target_049) < 0.001)

# Ergebnisse
print("=== MATHEMATISCHES AUDIT ===")
print(f"Benford's Law Chi²: {chi2_stat:.6f}")
print(f"Benford's Law p-value: {benford_p_value:.6f}")
print(f"Zipf R²: {zipf_r_squared:.6f}")
print(f"Konvergenz 0.049: {convergence_049:.6f}")
print(f"Konvergenz Phi: {convergence_phi:.6f}")
print(f"Z-Score (sigma): {z_score:.6f}")
print(f"Phi-Vorkommen: {phi_occurrences}")
print(f"0.049-Vorkommen: {constant_049_occurrences}")

# Fazit basierend auf Z-Score
if z_score > 5:
    print("Status: Strukturelle Inevitabilität")

# Detailierte Ausgabe für MD-Datei
results = {
    "benford_chi2": chi2_stat,
    "benford_p_value": benford_p_value,
    "zipf_r_squared": zipf_r_squared,
    "convergence_049": convergence_049,
    "convergence_phi": convergence_phi,
    "z_score": z_score,
    "phi_occurrences": phi_occurrences,
    "constant_049_occurrences": constant_049_occurrences,
    "fibonacci_ratios": fibonacci_ratios[:10],  # Erste 10 Ratios
    "first_digits_distribution": dict(digit_counts)
}

with open('audit_results.json', 'w') as f:
    json.dump(results, f, indent=2)