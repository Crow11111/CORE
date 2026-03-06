FROM python:3.11-slim-bookworm

# Architektur: arm64 (Raspi 5) kompatibel
# Slim Image für minimalen Footprint

WORKDIR /app

# Erstelle Struktur für Python-Module
RUN mkdir -p /app/src/edge /app/static/audio

# System-Abhängigkeiten für Coral TPU und Audio
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    usbutils \
    libusb-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Add Google Coral repository
RUN echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | tee /etc/apt/sources.list.d/coral-edgetpu.list \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - \
    && apt-get update \
    && apt-get install -y libedgetpu1-std \
    && rm -rf /var/lib/apt/lists/*

# Python Dependencies
# pychromecast: Audio Casting to Nest Mini
# aiohttp: Web Server / API Client
# requests: Standard HTTP
# tflite-runtime: For Edge TPU (using official wheel for Python 3.11 if available, otherwise fallback)
# Note: tflite-runtime wheels for 3.11/arm64 might need custom index or build.
# For now, we stick to standard pip, checking if tflite-runtime is available.
# If not, we rely on the system libedgetpu and potentially use a custom wheel later.

RUN pip install --no-cache-dir \
    aiohttp \
    requests \
    pychromecast \
    python-dotenv \
    loguru \
    httpx

# Code kopieren (wird vom Context-Root c/MTHO_CORE gestartet)
COPY ./src/edge/ /app/src/edge/
COPY ./src/services/ /app/src/services/

# Setze Python Path, damit "src.edge..." importierbar bleibt
ENV PYTHONPATH=/app

# Start Command
CMD ["python", "-m", "src.edge.scout_main"]
