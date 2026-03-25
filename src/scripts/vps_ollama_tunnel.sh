#!/bin/bash
# Stellt einen SSH-Tunnel zu Ollama auf dem VPS (OC Brain) her.
# Das OC Brain uebernimmt die 768dim (Agency) Last, Dreadnought ist nur Client.

KEY="/home/mth/.ssh/id_ed25519_hostinger"
USER="root"
HOST="187.77.68.250"

echo ">> Baue SSH Tunnel fuer OC Brain Ollama auf (Local 11434 -> VPS 11434)..."
ssh -f -N -L 11434:127.0.0.1:11434 -i "$KEY" -o StrictHostKeyChecking=no -o ExitOnForwardFailure=yes "$USER@$HOST"

if [ $? -eq 0 ]; then
    echo ">> Tunnel aktiv. VPS-Ollama ist nun auf http://localhost:11434 erreichbar."
else
    echo ">> FEHLER beim Tunnel-Aufbau! Laeuft ggf. ein lokaler Dienst auf 11434?"
fi
