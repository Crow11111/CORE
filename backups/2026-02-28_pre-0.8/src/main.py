import logging
from fastapi import FastAPI
from dotenv import load_dotenv

# Env laden
load_dotenv()

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Router importieren
from src.api.whatsapp_bridge import router as whatsapp_router

app = FastAPI(
    title="ATLAS AGI Core",
    description="Einstiegspunkt für WhatsApp Bridge und Sensor Bus",
    version="1.0.0"
)

# Router mounten
app.include_router(whatsapp_router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "agi-core"}
