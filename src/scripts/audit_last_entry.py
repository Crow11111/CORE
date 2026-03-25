import asyncio
import json
from src.network.chroma_client import get_chroma_client

async def query_last_entry():
    """
    Fragt die ChromaDB ab und ermittelt den Zeitstempel des letzten Eintrags
    in den relevanten Collections, basierend auf einem 'timestamp' Metadatenfeld.
    """
    try:
        chroma_client = await get_chroma_client()
        if not chroma_client:
            print("FEHLER: Konnte keine Verbindung zur ChromaDB herstellen.")
            return

        collections_to_check = ["core_directives", "simulation_evidence"]
        latest_timestamps = {}

        for collection_name in collections_to_check:
            try:
                collection = chroma_client.get_collection(name=collection_name)

                # Holen aller Einträge mit Metadaten.
                # 'n_results' muss so hoch sein, dass alle Einträge erfasst werden.
                # Wir gehen hier von einer überschaubaren Anzahl aus.
                results = collection.get(include=["metadatas"])

                timestamps = []
                if results and results["metadatas"]:
                    for metadata in results["metadatas"]:
                        if metadata and "timestamp_utc" in metadata:
                            timestamps.append(metadata["timestamp_utc"])

                if timestamps:
                    latest_timestamp = max(timestamps)
                    latest_timestamps[collection_name] = latest_timestamp
                else:
                    latest_timestamps[collection_name] = "Keine Einträge mit Zeitstempel gefunden."

            except Exception as e:
                # Dieser Fehler tritt auf, wenn die Collection nicht existiert.
                latest_timestamps[collection_name] = f"Fehler beim Abrufen der Collection: {e}"

        print("\n--- ChromaDB Audit: Zeitstempel der letzten Erkenntnisse ---")
        for collection, ts in latest_timestamps.items():
            print(f"Collection '{collection}': {ts}")
        print("----------------------------------------------------------")

    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")

if __name__ == "__main__":
    asyncio.run(query_last_entry())

