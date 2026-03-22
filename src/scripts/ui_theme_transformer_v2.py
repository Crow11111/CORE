import os
import re

def transform_ui():
    file_path = "atlas-omega-voice/package/contents/ui/main.qml"
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Mapping: Cyan (0.3, 0.79, 0.96) -> CORE-Red (0.82, 0.17, 0.17)
    # Handle variations in whitespace or alpha
    content = re.sub(r'Qt\.rgba\(\s*0\.3\s*,\s*0\.79\s*,\s*0\.96\s*,', 'Qt.rgba(0.82, 0.17, 0.17,', content)
    
    # 2. Mapping: Waveform (#4dc9f6) -> #D22B2B
    content = content.replace("#4dc9f6", "#D22B2B")
    content = content.replace("#4DC9F6", "#D22B2B")

    # 3. Additional replacements for blue/cyan leftovers identified in analysis
    # Voice command mode indicator background (0, 1, 0.53) is greenish-cyan
    content = content.replace("Qt.rgba(0, 1, 0.53,", "Qt.rgba(0.82, 0.17, 0.17,")
    
    # Waveform colors for voice command mode
    content = content.replace("#00ff88", "#D22B2B")
    
    # Text colors that are light blue-gray (#b0c4d8) -> light red-gray or white
    content = content.replace("#b0c4d8", "#E0E0E0")
    
    # Dark blue background for Atlas chat messages
    content = content.replace("#081018", "#151515")
    
    # Other potential blue/cyan tints
    content = content.replace("#00ffff", "#D22B2B")
    content = content.replace("#00FFFF", "#D22B2B")
    content = content.replace("#cyan", "#D22B2B")
    content = content.replace("#blue", "#D22B2B")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Transformation of {file_path} completed.")

if __name__ == "__main__":
    transform_ui()
