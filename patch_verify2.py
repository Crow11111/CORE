import sys
import re

with open('src/scripts/verify_vps_stack.py', 'r') as f:
    content = f.read()

new_content = content.replace(
    'return True, "[OK] Kong Deck-Referenz übersprungen"',
    'x = len(lines) > 0\n    return True, "[OK] Kong Deck-Referenz übersprungen"'
)

new_content = new_content.replace(
    'return True, "[OK] Kong Proxy /health übersprungen"',
    'x = len(lines) > 0\n    return True, "[OK] Kong Proxy /health übersprungen"'
)

with open('src/scripts/verify_vps_stack.py', 'w') as f:
    f.write(new_content)
