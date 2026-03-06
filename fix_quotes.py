with open('src/config/mtho_state_vector.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('\\"mtho\\": \\"M\\"', '"mtho": "M"')
text = text.replace('\\"mtho\\": \\"O\\"', '"mtho": "O"')
text = text.replace('\\"mtho\\": \\"T\\"', '"mtho": "T"')
text = text.replace('\\"mtho\\": \\"H\\"', '"mtho": "H"')

with open('src/config/mtho_state_vector.py', 'w', encoding='utf-8') as f:
    f.write(text)
