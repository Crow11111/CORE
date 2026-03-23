#!/usr/bin/env python3

import subprocess
import sys

def verify_dbus():
    try:
        # Use dbus-send to call showNotification on org.omega.atlas /Backend
        print("Sending D-Bus notification to org.omega.atlas /Backend...")
        
        # Method call:
        # qdbus org.omega.atlas /Backend org.kde.plasmashell.JarvisBackend.showNotification "Test Notification" "D-Bus integration works!"
        # or dbus-send:
        cmd = [
            "dbus-send",
            "--session",
            "--print-reply",
            "--dest=org.omega.atlas",
            "/Backend",
            "org.kde.plasmashell.JarvisBackend.showNotification",
            "string:Atlas System",
            "string:D-Bus Integration successfully verified!"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Successfully sent D-Bus message!")
            print(result.stdout)
            sys.exit(0)
        else:
            print("Failed to send D-Bus message.")
            print("Error:", result.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_dbus()
