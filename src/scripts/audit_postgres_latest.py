import asyncio
import sys
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv
import os

# Modul-Pfad anpassen
sys.path.append(str(Path(__file__).parent.parent.parent))

async def query_postgres_latest():
    """Verbindet sich mit der PostgreSQL-Datenbank und holt die letzten 10 Einträge."""
    load_dotenv()

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("FEHLER: DATABASE_URL nicht in .env gefunden.")
        return

    try:
        engine = create_async_engine(db_url, echo=False)

        async with engine.connect() as conn:
            # Annahme: Es gibt eine Tabelle 'documents' mit einer Spalte 'created_at'.
            # Wir müssen vielleicht den tatsächlichen Tabellen- und Spaltennamen anpassen.
            # Zuerst prüfen wir, welche Tabellen überhaupt da sind.

            table_query = text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
            result_tables = await conn.execute(table_query)
            tables = [row[0] for row in result_tables]

            print("--- Gefundene Tabellen in der PostgreSQL-Datenbank ---")
            print(tables)
            print("--------------------------------------------------")

            target_table = None
            if 'documents' in tables:
                target_table = 'documents'
            elif 'entries' in tables:
                target_table = 'entries'
            # Fügen Sie hier weitere mögliche Namen hinzu

            if not target_table:
                print("\nFEHLER: Keine der erwarteten Tabellen ('documents', 'entries') gefunden.")
                return

            print(f"\n--- Letzte 10 Einträge aus Tabelle '{target_table}' ---")

            # Annahme: Es gibt eine Spalte 'created_at'.
            # Wir holen die letzten 10 Einträge, sortiert nach diesem Zeitstempel.
            query = text(f"SELECT id, created_at, metadata FROM {target_table} ORDER BY created_at DESC LIMIT 10")

            result = await conn.execute(query)

            for row in result:
                # Konvertiere das Row-Objekt in ein besser lesbares Dictionary
                row_dict = row._asdict()
                print(f"ID: {row_dict.get('id')}, Erstellt am: {row_dict.get('created_at')}, Metadaten: {row_dict.get('metadata')}")

            print("-------------------------------------------------")

    except Exception as e:
        print(f"Ein Fehler bei der Abfrage von PostgreSQL ist aufgetreten: {e}")

if __name__ == "__main__":
    asyncio.run(query_postgres_latest())
