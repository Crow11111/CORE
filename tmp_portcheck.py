import socket, time

def check_port(host, port, timeout=5):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((host, port))
        s.close()
        return result == 0
    except Exception as e:
        return False

host = "192.168.178.54"

# Port 3000 (AdGuard Web UI)
p3000 = check_port(host, 3000)
print("Port 3000 (AdGuard Web UI):", "OFFEN" if p3000 else "GESCHLOSSEN")

# Port 53 (DNS)
p53 = check_port(host, 53)
print("Port 53 (DNS TCP):", "OFFEN" if p53 else "GESCHLOSSEN")

# Port 8123 (HA)
p8123 = check_port(host, 8123)
print("Port 8123 (HA):", "OFFEN" if p8123 else "GESCHLOSSEN")

# HTTP GET auf Port 3000
import requests, urllib3
urllib3.disable_warnings()
try:
    r = requests.get("http://" + host + ":3000", timeout=10, verify=False)
    print("\nHTTP GET http://" + host + ":3000")
    print("Status:", r.status_code)
    print("Headers:", dict(r.headers))
    print("Body (first 500 chars):", r.text[:500])
except Exception as e:
    # Try HTTPS
    try:
        r = requests.get("https://" + host + ":3000", timeout=10, verify=False)
        print("\nHTTPS GET https://" + host + ":3000")
        print("Status:", r.status_code)
        print("Headers:", dict(r.headers))
        print("Body (first 500 chars):", r.text[:500])
    except Exception as e2:
        print("\nHTTP/HTTPS auf Port 3000 fehlgeschlagen:")
        print("HTTP Error:", str(e))
        print("HTTPS Error:", str(e2))
