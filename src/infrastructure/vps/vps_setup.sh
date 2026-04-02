#!/bin/bash
# OMEGA CORE V4: VPS SETUP (FIRECRACKER & EBPF)
# Status: PROTOTYPE | OMEGA_INFRA | V4

set -e

echo "[V4-SETUP] Initialisiere VPS Infrastruktur..."

# 1. Abhängigkeiten installieren
sudo apt-get update
sudo apt-get install -y \
    binutils \
    bridge-utils \
    iptables \
    libelf-dev \
    gcc \
    make \
    python3-pip \
    curl \
    git

# 2. Firecracker installieren
FIRECRACKER_VERSION="v1.7.0"
ARCH=$(uname -m)
curl -L "https://github.com/firecracker-microvm/firecracker/releases/download/${FIRECRACKER_VERSION}/firecracker-${FIRECRACKER_VERSION}-${ARCH}" -o firecracker
chmod +x firecracker
sudo mv firecracker /usr/local/bin/

# 3. eBPF Tools (bpftool, libbpf)
sudo apt-get install -y linux-tools-$(uname -r) linux-headers-$(uname -r)

# 4. Verzeichnisse erstellen
mkdir -p /opt/omega/firecracker/kernels
mkdir -p /opt/omega/firecracker/rootfs
mkdir -p /opt/omega/firecracker/snapshots

echo "[V4-SETUP] Firecracker und eBPF-Abhängigkeiten installiert."

# --- KERNEL & ROOTFS DOWNLOAD (MOCK für Prototyp) ---
# In Produktion würden hier die gehärteten OMEGA-Images geladen.
echo "[V4-SETUP] Lade Basis-Images (Simuliert)..."
touch /opt/omega/firecracker/kernels/vmlinux.bin
touch /opt/omega/firecracker/rootfs/ubuntu.ext4

echo "[V4-SETUP] Fertig. System bereit für PVM-Patching (Vektor 1)."

# --- VSOCK BRIDGE CONFIGURATION ---
# Konfiguriert die Host-Seite für die vsock Kommunikation
echo "[V4-SETUP] Konfiguriere vsock bridge..."
sudo modprobe vhost_vsock
echo "vhost_vsock" | sudo tee -a /etc/modules

# Prüfe vsock device
if [ -c /dev/vhost-vsock ]; then
    echo "[V4-SETUP] vsock device (/dev/vhost-vsock) ist bereit."
else
    echo "[V4-SETUP] WARNUNG: vsock device nicht gefunden. Kernel-Modul ggf. manuell laden."
fi
