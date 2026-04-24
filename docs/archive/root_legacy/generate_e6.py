import itertools
import math

def generate_e6_roots():
    roots = []
    # Using the standard R^8 representation of E8, E6 is the set of roots orthogonal to e7+e8 and e7-e8? No, that's D6.
    # E6 is orthogonal to e6-e7 and e6+e7+e8...
    # Let's use the R^6 representation:
    # 40 roots from D5: (±1, ±1, 0, 0, 0, 0)
    for pos in itertools.combinations(range(5), 2):
        for signs in [(1,1), (1,-1), (-1,1), (-1,-1)]:
            vec = [0]*6
            vec[pos[0]] = signs[0]
            vec[pos[1]] = signs[1]
            roots.append(vec)
            
    # 32 roots: (±1/2, ±1/2, ±1/2, ±1/2, ±1/2, ±√3/2)
    # where the number of minus signs in the first 5 coordinates is EVEN
    for signs in itertools.product([1, -1], repeat=5):
        if sum(1 for s in signs if s == -1) % 2 == 0:
            for last_sign in [1, -1]:
                vec = [s/2 for s in signs] + [last_sign * math.sqrt(3)/2]
                roots.append(vec)
                
    return roots

r = generate_e6_roots()
print(f"Generated {len(r)} roots.")
