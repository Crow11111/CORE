# harden_firewall.ps1
# MTHO_CORE: Phase 1 Zero-Trust Firewall Script

Write-Host "=== MTHO_CORE: Zero-Trust Firewall Konfiguration ===" -ForegroundColor Cyan

Write-Host "[*] Bereinige alte CORE-Regeln..."
Remove-NetFirewallRule -DisplayName "CORE Inbound SSH" -ErrorAction SilentlyContinue
Remove-NetFirewallRule -DisplayName "CORE Ollama API" -ErrorAction SilentlyContinue

Write-Host "[*] Setze strikte Inbound-Ports (22, 11434)..."
New-NetFirewallRule -DisplayName "CORE Inbound SSH" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 22 | Out-Null
New-NetFirewallRule -DisplayName "CORE Ollama API" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 11434 | Out-Null

Write-Host "[+] Zero-Trust Firewall Regeln fuer Port 22 und 11434 erfolgreich hinzugefuegt." -ForegroundColor Green

Write-Host "=== Firewall Hardening abgeschlossen ===" -ForegroundColor Cyan
Write-Host "Druecken Sie eine beliebige Taste, um dieses Fenster zu schliessen..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
