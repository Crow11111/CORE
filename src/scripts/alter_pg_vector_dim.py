
import asyncio
from src.db.multi_view_client import _run_pg_sql

async def main():
    # We alter the columns to vector(6144) to hold kardanic folded Gemini embeddings
    columns = ["v_keywords", "v_semantics", "v_media"]
    for col in columns:
        sql = f"ALTER TABLE multi_view_embeddings ALTER COLUMN {col} TYPE vector(6144);"
        # Longer timeout for table alteration
        ok, out = await _run_pg_sql(sql, timeout=120)
        print(f"Altered {col}: {ok} {out}")

if __name__ == "__main__":
    asyncio.run(main())
