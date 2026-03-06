import re

with open('src/config/mtho_state_vector.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Remove Legacy layer
text = re.sub(r'# -{75}\n# Legacy MTHO Layer.*?MTHO_PAIRINGS = \{\n.*?\n\}\n*', '', text, flags=re.DOTALL)

# 2. Fix TETRALOGIE dictionary to only have the first mtho key
text = re.sub(r'\"mtho\": \"([MTHO])\", \"mtho\": \"[A-Z]\",', r'\"mtho\": \"\1\",', text)

# 3. Fix SIMULATION_EVIDENCE_STATS to only have the MTHO line
text = re.sub(r'\"mtho_verteilung\": \{\"L\": 19, \"P\": 13, \"I\": 13, \"S\": 13\}, # Legacy keys kept for stats compatibility\n\s+\"mtho_verteilung\":', '\"mtho_verteilung\":', text)

with open('src/config/mtho_state_vector.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Fixed mtho_state_vector.py')
