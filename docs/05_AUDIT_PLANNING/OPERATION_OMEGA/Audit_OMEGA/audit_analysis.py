# -*- coding: utf-8 -*-
"""Unabhängiges mathematisches Audit - Audit_OMEGA"""

import json
import math
from collections import Counter

# Daten laden
with open('audit_data.json', 'r') as f:
    data = json.load(f)

values = data['data_points']
n = len(values)

# ========== 1. BENFORD'S LAW TEST ==========
def leading_digit(x):
    if x == 0:
        return None
    s = str(abs(x)).replace('.', '').lstrip('0')
    if not s:
        return 0
    return int(s[0])

leading_digits = [leading_digit(v) for v in values if leading_digit(v) is not None]
digit_counts = Counter(leading_digits)

# Benford-Erwartung: P(d) = log10(1 + 1/d)
benford_expected = {d: math.log10(1 + 1/d) for d in range(1, 10)}
observed = [digit_counts.get(d, 0) / len(leading_digits) for d in range(1, 10)]
expected = [benford_expected[d] for d in range(1, 10)]

# Chi-Quadrat für Benford (8 Freiheitsgrade)
chi2_stat = sum((digit_counts.get(d, 0) - n * benford_expected[d])**2 / (n * benford_expected[d] + 1e-10) for d in range(1, 10))
benford_chi2 = chi2_stat

# ========== 2. ZIPF-VERTEILUNG (R²) ==========
# Sortiere absteigend, Rang 1 = größter Wert
sorted_vals = sorted(values, reverse=True)
ranks = list(range(1, n + 1))
log_ranks = [math.log(r) for r in ranks]
log_freq = [math.log(v) for v in sorted_vals]

# Lineare Regression: log(freq) = a + b*log(rank), Zipf: b ≈ -1
sum_x = sum(log_ranks)
sum_y = sum(log_freq)
sum_xx = sum(x*x for x in log_ranks)
sum_yy = sum(y*y for y in log_freq)
sum_xy = sum(x*y for x, y in zip(log_ranks, log_freq))

b_zipf = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x**2 + 1e-10)
a_zipf = (sum_y - b_zipf * sum_x) / n

y_pred = [a_zipf + b_zipf * x for x in log_ranks]
ss_res = sum((log_freq[i] - y_pred[i])**2 for i in range(n))
ss_tot = sum((y - sum_y/n)**2 for y in log_freq)
r2_zipf = 1 - ss_res / (ss_tot + 1e-10)

# ========== 3. KONVERGENZ 0.049 und Φ (1.618) ==========
target_049 = 0.049
target_phi = 1.618033988749895

# Abstände zu den Zielwerten
dists_049 = [abs(v - target_049) for v in values]
dists_phi = [abs(v - target_phi) for v in values]

# Minimale Abstände
min_dist_049 = min(dists_049)
min_dist_phi = min(dists_phi)
idx_049 = dists_049.index(min_dist_049)
idx_phi = dists_phi.index(min_dist_phi)

# Konvergenz-Metrik: Wie viele Werte liegen innerhalb ε?
eps_049 = 0.01  # 1% Toleranz
eps_phi = 0.01
count_near_049 = sum(1 for v in values if abs(v - target_049) < eps_049)
count_near_phi = sum(1 for v in values if abs(v - target_phi) < eps_phi)

# Relative Konvergenz-Rate
conv_049 = count_near_049 / n
conv_phi = count_near_phi / n

# ========== 4. KUMULATIVE SIGNIFIKANZ (Z-SCORE) ==========
# Kombination der Abweichungen als Basis für σ
# Benford-Abweichung (normalisiert)
benford_dev = sum(abs(observed[i] - expected[i]) for i in range(9)) / 9

# Zipf-Abweichung von idealem -1
zipf_dev = abs(b_zipf - (-1))

# Konvergenz-Signifikanz (inverse Distanzen)
sig_049 = 1 / (min_dist_049 + 1e-10)
sig_phi = 1 / (min_dist_phi + 1e-10)

# Z-Score: Standardisierte kumulative Abweichung
# Aggregation mehrerer Signale
components = [
    chi2_stat / 10,  # Benford-Chi² skaliert
    (1 - r2_zipf) * 10,  # Zipf R² Abweichung
    sig_049 / 100,
    sig_phi / 10
]
mean_comp = sum(components) / len(components)
var_comp = sum((c - mean_comp)**2 for c in components) / (len(components) + 1e-10)
std_comp = math.sqrt(var_comp + 1e-10)
z_score = (sum(components) - mean_comp) / (std_comp + 1e-10)

# Alternative: Direkte Z-Score-Berechnung aus Chi²
# Chi² mit 8 df: Erwartungswert 8, Varianz 16
chi2_z = (chi2_stat - 8) / (4 + 1e-10)

# Kombinierter σ aus mehreren Metriken
sigma = abs(z_score)

# ========== AUSGABE ==========
print("=" * 50)
print("MATHEMATISCHES AUDIT - KENNZAHLEN")
print("=" * 50)
print()
print("1. BENFORD'S LAW")
print("   Führende Ziffern (beobachtet):", dict(sorted(digit_counts.items())))
print("   Erwartet (Benford):", {d: round(benford_expected[d], 4) for d in range(1, 10)})
print("   Chi2-Statistik:", round(chi2_stat, 6))
print("   Beobachtete Verteilung:", [round(o, 4) for o in observed])
print()
print("2. ZIPF-VERTEILUNG")
print("   R2 (Bestimmtheitsmass):", round(r2_zipf, 6))
print("   Exponent (erwartet -1):", round(b_zipf, 6))
print()
print("3. KONVERGENZ")
print("   Ziel 0.049: min. Abstand =", min_dist_049, "| Index =", idx_049, "| Werte in eps=0.01:", count_near_049)
print("   Ziel Phi(1.618): min. Abstand =", round(min_dist_phi, 10), "| Index =", idx_phi, "| Werte in eps=0.01:", count_near_phi)
print("   Konvergenz-Rate 0.049:", round(conv_049, 4))
print("   Konvergenz-Rate Phi:", round(conv_phi, 4))
print()
print("4. KUMULATIVE SIGNIFIKANZ")
print("   Z-Score (sigma):", round(sigma, 6))
print("   Chi2-basierter Z:", round(chi2_z, 6))
print()
if sigma > 5:
    print("Status: Strukturelle Inevitabilität")
print("=" * 50)
