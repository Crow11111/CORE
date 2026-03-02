#!/bin/bash
cat > /tmp/chat_req.json << 'JSONEOF'
{"model":"google/gemini-2.5-pro","messages":[{"role":"user","content":"Sag Hallo"}]}
JSONEOF
curl -s -X POST http://127.0.0.1:18789/v1/chat/completions -H 'Content-Type: application/json' -H 'Authorization: Bearer ykKqxCcMM5CPYTS20fxTWyu6RkLkvd5T' -d @/tmp/chat_req.json
