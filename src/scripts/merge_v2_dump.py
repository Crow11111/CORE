import os
import re

base_dir = "docs/06_FTOE_LEHRBUCH/144_MATRIX_TEILDOKUMENTE/v2_Ontologie_der_Zahlen/"
output_file = "docs/06_FTOE_LEHRBUCH/144_MATRIX_TEILDOKUMENTE/v2_Ontologie_der_Zahlen_STRUKTURIERT_DUMP.md"

files = [f for f in os.listdir(base_dir) if f.endswith('.md')]

def get_sort_key(filename):
    if filename.startswith("HAUPTKAPITEL"):
        match = re.search(r'HAUPTKAPITEL_(\d+)_', filename)
        if match:
            return (int(match.group(1)), 0)
    elif filename.startswith("TEILDOKUMENT"):
        match = re.search(r'TEILDOKUMENT_(\d+)_(\d+)_', filename)
        if match:
            return (int(match.group(1)), int(match.group(2)))
    return (999, 999)

sorted_files = sorted(files, key=get_sort_key)

with open(output_file, 'w', encoding='utf-8') as outfile:
    outfile.write("# STRUKTURIERTER DUMP: V2 Ontologie der Zahlen\n\n")
    outfile.write("> **Hinweis:** Geordnet nach Hauptkapitel und fortlaufenden Teildokumenten (1.0 -> 1.1 -> 1.12 -> 2.0 etc.).\n\n")
    
    # Inhaltsverzeichnis
    outfile.write("## Inhaltsverzeichnis\n\n")
    for f in sorted_files:
        outfile.write(f"- {f}\n")
        
    outfile.write("\n" + "="*80 + "\n\n")
    
    for f in sorted_files:
        filepath = os.path.join(base_dir, f)
        with open(filepath, 'r', encoding='utf-8') as infile:
            content = infile.read()
            outfile.write(f"<!-- START FILE: {f} -->\n")
            outfile.write(f"## DATEI-QUELLE: `{f}`\n\n")
            outfile.write(content)
            outfile.write(f"\n<!-- END FILE: {f} -->\n")
            outfile.write("\n" + "="*80 + "\n\n")

print(f"Strukturierter Dump erstellt: {output_file}")
