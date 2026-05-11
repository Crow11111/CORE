import chromadb
from chromadb.config import Settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def purge_hallucinations():
    try:
        # ChromaDB Client auf Port 32779 (aus VPS_HOST_PORT_CONTRACT.md bzw lokaler Config)
        client = chromadb.HttpClient(host='localhost', port=32779)
        
        collections = client.list_collections()
        for col_obj in collections:
            col_name = col_obj.name
            logger.info(f"Prüfe Collection: {col_name}")
            col = client.get_collection(col_name)
            
            # Hole Metadaten um nach Dateinamen zu filtern
            results = col.get(
                where={"$or": [
                    {"source": "docs/04_PROCESSES/OMEGA_LANDKARTE_DER_KAUSALITAET.md"},
                    {"source": "src/scripts/ftoe_causality_iterator.py"}
                ]}
            )
            
            if results and results['ids']:
                logger.info(f"Lösche {len(results['ids'])} halluzinierte Dokumente aus {col_name}")
                col.delete(ids=results['ids'])
            else:
                logger.info(f"Keine Heroin-Artefakte in {col_name} gefunden.")
                
    except Exception as e:
        logger.error(f"Fehler bei der Bereinigung: {e}")

if __name__ == "__main__":
    purge_hallucinations()
