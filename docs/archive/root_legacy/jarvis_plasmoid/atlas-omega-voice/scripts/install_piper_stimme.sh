#!/usr/bin/env bash
# Lädt eine Piper-Stimme nach ~/.local/share/jarvis/piper-voices/ (für „Abspielen“ / lokales testVoice).
# Standard: en_GB-alan-medium — Aufruf: install_piper_stimme.sh de_DE-thorsten-high
set -euo pipefail
VOICE_ID="${1:-en_GB-alan-medium}"
DEST="${XDG_DATA_HOME:-$HOME/.local/share}/jarvis/piper-voices"
mkdir -p "$DEST"

declare -A URL_ONNX URL_JSON
URL_ONNX[en_GB-alan-medium]="https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx"
URL_JSON[en_GB-alan-medium]="https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx.json"
URL_ONNX[de_DE-thorsten-high]="https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx"
URL_JSON[de_DE-thorsten-high]="https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx.json"

U="${URL_ONNX[$VOICE_ID]:-}"
J="${URL_JSON[$VOICE_ID]:-}"
if [[ -z "$U" ]]; then
  echo "ATLAS: Unbekannte VOICE_ID '$VOICE_ID'. Bekannt: ${!URL_ONNX[*]}" >&2
  exit 1
fi

echo "ATLAS: Lade $VOICE_ID …"
curl -fL --progress-bar -o "$DEST/${VOICE_ID}.onnx" "$U"
curl -fL --progress-bar -o "$DEST/${VOICE_ID}.onnx.json" "$J"
echo "ATLAS: Fertig: $DEST/${VOICE_ID}.onnx"
