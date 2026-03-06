FROM node:20-slim

WORKDIR /app

# Installiere Tools für Shell und socat für die TCP-zu-stdio Brücke
RUN apt-get update && apt-get install -y socat bash curl && rm -rf /var/lib/apt/lists/*

# Installiere den offiziellen Filesystem-Server (und optional Shell)
RUN npm install -g @modelcontextprotocol/server-filesystem

# Erstelle Workspace-Verzeichnis
RUN mkdir -p /workspace

EXPOSE 8001

# socat bindet TCP Port 8001 an die Standardein-/ausgabe des MCP Servers
CMD ["socat", "TCP-LISTEN:8001,fork,reuseaddr", "EXEC:'npx -y @modelcontextprotocol/server-filesystem /workspace'"]
