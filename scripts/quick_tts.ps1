# Wrapper für CORE TTS
param(
    [Parameter(Mandatory=$true)]
    [string]$Text,
    [string]$Target = "mini",
    [string]$Role = "omega"
)

$env:PYTHONIOENCODING="utf-8"
# Rufe das Python-Modul auf. Wir nehmen an, wir sind im Root.
python -m src.scripts.say_it "$Text" --target "$Target" --role "$Role"
