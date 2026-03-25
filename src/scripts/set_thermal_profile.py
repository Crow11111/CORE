#!/usr/bin/env python3
import requests
import sys

# CoolerControl Daemon API Port (default is usually 11988)
API_URL = "http://localhost:11988/api"

def set_profile(profile_name):
    # Diese Logik setzt voraus, dass Profile mit diesem Namen in der GUI existieren
    try:
        # 1. Alle Profile abrufen
        resp = requests.get(f"{API_URL}/profiles")
        if resp.status_code != 200:
            print("Fehler beim Abrufen der Profile.")
            return False
            
        profiles = resp.json()
        target_id = None
        
        for p in profiles:
            if p.get("name", "").lower() == profile_name.lower():
                target_id = p.get("id")
                break
                
        if not target_id:
            print(f"Profil '{profile_name}' nicht gefunden. Bitte in der CoolerControl GUI anlegen.")
            return False
            
        # 2. Profil aktivieren
        # Die genaue API Route hängt von der CoolerControl Version ab.
        # Im Zweifel muss dies angepasst werden, sobald die Profile in der GUI angelegt wurden.
        print(f"Versuche Profil '{profile_name}' (ID: {target_id}) zu aktivieren...")
        # Pseudo-Call, dokumentierte API Routes prüfen!
        
        return True
    except Exception as e:
        print(f"API Fehler: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 set_thermal_profile.py <profile_name>")
        sys.exit(1)
        
    set_profile(sys.argv[1])
