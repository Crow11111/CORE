# Repariert die OpenClaw-Config: ungueltige Keys entfernen, saubere Auth
import paramiko, os, json, base64, time
from dotenv import load_dotenv
load_dotenv()

HOST = os.getenv("VPS_HOST", "").strip()
KEY = os.getenv("VPS_SSH_KEY", "").strip().strip('"')
PWD = os.getenv("VPS_PASSWORD", "").strip().strip('"')
TOKEN = os.getenv("OPENCLAW_GATEWAY_TOKEN", "").strip().strip('"')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
if KEY and os.path.isfile(KEY):
    ssh.connect(HOST, port=22, username="root", key_filename=KEY, timeout=15)
else:
    ssh.connect(HOST, port=22, username="root", password=PWD, timeout=15)
print("[OK] SSH\n")

def run(cmd, timeout=60):
    i, o, e = ssh.exec_command(cmd, timeout=timeout)
    code = o.channel.recv_exit_status()
    return code, o.read().decode("utf-8", "replace").strip(), e.read().decode("utf-8", "replace").strip()

# 1. Container stoppen
print("=== 1. Container stoppen ===")
run("docker stop openclaw-admin openclaw-spine 2>/dev/null")
print("  Gestoppt")

# 2. Config lesen und reparieren
print("\n=== 2. Config reparieren ===")
CORRECT_PATH = "/opt/atlas-core/openclaw-admin/data/openclaw.json"
c, raw, _ = run(f"cat {CORRECT_PATH}")

if raw:
    cfg = json.loads(raw)
    
    # Ungueltige Keys entfernen
    if "gateway" in cfg and "controlUi" in cfg["gateway"]:
        ctrl = cfg["gateway"]["controlUi"]
        # Nur gueltige Keys behalten
        valid_keys = ["enabled", "basePath", "allowedOrigins", 
                      "dangerouslyAllowHostHeaderOriginFallback", 
                      "allowInsecureAuth", "dangerouslyDisableDeviceAuth"]
        for key in list(ctrl.keys()):
            if key not in valid_keys:
                print(f"  Entferne ungueltigen Key: {key}")
                del ctrl[key]
    
    # Saubere Auth-Config (Token-basiert, wie in Doku)
    cfg["gateway"]["auth"] = {
        "mode": "token",
        "token": TOKEN
    }
    
    # controlUi: nur erlaubte Flags
    cfg["gateway"]["controlUi"] = {
        "enabled": True,
        "allowedOrigins": ["*"],
        "dangerouslyAllowHostHeaderOriginFallback": True,
        "allowInsecureAuth": True,
        # dangerouslyDisableDeviceAuth NICHT setzen - stattdessen Token verwenden
    }
    
    # Ollama-Provider mit korrekter URL (localhost, da Container Host-Netzwerk haben sollte)
    # ABER: Standard-Docker-Container koennen localhost nicht erreichen
    # Loesung: Ollama auf 0.0.0.0 binden UND Container mit extra_hosts
    if "models" in cfg and "providers" in cfg["models"]:
        if "ollama" in cfg["models"]["providers"]:
            # Fuer jetzt: Ollama entfernen, da es nicht von Container erreichbar ist
            # Spaeter mit korrektem Netzwerk-Setup wieder hinzufuegen
            print("  Info: Ollama-Provider bleibt, aber Netzwerk muss noch gefixt werden")
    
    # Schreiben
    merged = json.dumps(cfg, indent=2, ensure_ascii=False)
    b64 = base64.standard_b64encode(merged.encode("utf-8")).decode("ascii")
    c, _, err = run(f"echo '{b64}' | base64 -d > {CORRECT_PATH}")
    if c == 0:
        print("  [OK] Config repariert")
    else:
        print(f"  [FAIL] {err}")
else:
    print("  [FAIL] Config nicht lesbar")

# 3. openclaw doctor --fix im Container ausfuehren
print("\n=== 3. Container starten und doctor --fix ===")
run("docker start openclaw-admin")
time.sleep(5)
c, out, _ = run("docker exec openclaw-admin openclaw doctor --fix 2>&1 | tail -20")
print(out[:800])

# 4. Container neustarten
print("\n=== 4. Container neustarten ===")
run("docker restart openclaw-admin openclaw-spine")
time.sleep(5)

# 5. Ollama mit qwen2.5:7b sicherstellen
print("\n=== 5. Ollama pruefen ===")
run("pkill ollama 2>/dev/null; sleep 2")
run("OLLAMA_HOST=0.0.0.0:11434 nohup ollama serve >> /var/log/ollama.log 2>&1 &")
time.sleep(3)
c, out, _ = run("ollama list 2>&1")
print(f"  Modelle: {out}")

if "qwen2.5:7b" not in out:
    print("  Modell pullen...")
    run("ollama pull qwen2.5:7b &")
    print("  (Pull laeuft im Hintergrund)")

# 6. Status
print("\n=== 6. Finaler Status ===")
c, out, _ = run("docker ps --filter name=openclaw --format '{{.Names}} {{.Status}}'")
print(out)

c, out, _ = run("curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 http://127.0.0.1:18789/ 2>&1")
print(f"  Port 18789: HTTP {out}")

ssh.close()
print("\n=== FERTIG ===")
print(f"\nBrowser testen mit Token in URL:")
print(f"  http://187.77.68.250:18789/?token={TOKEN}")
