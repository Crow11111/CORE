#!/bin/bash
PAYLOAD='{"ref":"refs/heads/master","after":"test123"}'
SECRET='bd2d4e932e44145e60cd686a93b9ba4691948837e450896e26a833f1c8fcd9b9'
SIG=$(echo -n "$PAYLOAD" | openssl dgst -sha256 -hmac "$SECRET" | sed 's/^.* //')
echo "Signature: sha256=$SIG"
curl -s -w "\nHTTP_CODE:%{http_code}\n" -X POST http://localhost:8080/webhook/github -H "Content-Type: application/json" -H "X-GitHub-Event: push" -H "X-Hub-Signature-256: sha256=$SIG" -d "$PAYLOAD"
echo "---DONE---"
