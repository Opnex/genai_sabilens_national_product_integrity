"""
main.py
-------
Entry point for the SabiLens NAFDAC Food Product RAG System.

TWO MODES
  ingest (default) — Load the Excel database, build chunks, embed, store in ChromaDB.
  serve            — Start the FastAPI verification server.

USAGE
  # First-time setup or after the database file is updated:
  python main.py --mode ingest

  # Start the API server (requires prior ingestion):
  python main.py --mode serve

  # Or run uvicorn directly for full control:
  uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload

INGESTION NOTES
  • Safe to re-run: upsert() never creates duplicates.
  • With 15 products, ingestion completes in well under a minute on CPU.
  • Output files written:
      data/processed/nafdac_chunks.json    — human-readable chunk dump
      data/processed/ingestion_report.json — row counts, warnings, stats
      chroma_db/                           — persistent ChromaDB storage
"""

import argparse
import json
from pathlib import Path
from datetime import datetime


def run_ingestion() -> None:
    """
    Execute the full ingestion pipeline end-to-end:
      Load Excel → Build chunks → Save JSON → Embed → Upsert to ChromaDB
    """
    # ── Local imports keep startup fast when running --mode serve ────────────
    from ingestion.excel_loader  import load_database
    from ingestion.chunk_builder import build_chunks, save_chunks
    from vectorstore.chroma_client import ChromaStore
    from vectorstore.embedder import Embedder
    from config.settings import settings

    print("\n" + "=" * 70)
    print("  SabiLens — NAFDAC Food Product RAG Ingestion Pipeline")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")

    # Ensure output directories exist before writing to them
    Path("./data/processed").mkdir(parents=True, exist_ok=True)
    Path(settings.CHROMA_PERSIST_DIR).mkdir(parents=True, exist_ok=True)

    # ── Step 1/5  Load and validate the Excel database ────────────────────────
    print("[Step 1/5] Loading NAFDAC database Excel file…")
    entries, load_report = load_database()

    # ── Step 2/5  Build ProductChunk objects ──────────────────────────────────
    print("\n[Step 2/5] Building product chunks…")
    chunks, chunk_stats = build_chunks(entries)

    # ── Step 3/5  Save chunks to JSON for audit ───────────────────────────────
    print("\n[Step 3/5] Saving audit JSON…")
    save_chunks(chunks, settings.CHUNKS_JSON_PATH)

    # ── Step 4/5  Generate embedding vectors ─────────────────────────────────
    print("\n[Step 4/5] Generating embedding vectors…")
    embedder   = Embedder()
    texts      = [c.text for c in chunks]
    embeddings = embedder.embed(texts)
    print(f"[Embedder] Generated {len(embeddings)} vector(s)  "
          f"(dimension: {len(embeddings[0])})")

    # ── Step 5/5  Upsert into ChromaDB ────────────────────────────────────────
    print("\n[Step 5/5] Upserting into ChromaDB…")
    store = ChromaStore()
    store.ingest(chunks, embeddings)

    # ── Write ingestion report ────────────────────────────────────────────────
    report = {
        "ingestion_timestamp"  : datetime.now().isoformat(),
        "database_path"        : settings.DATABASE_PATH,
        "embedding_model"      : settings.EMBEDDING_MODEL,
        "loader_report"        : load_report,
        "chunk_stats"          : chunk_stats,
        "final_document_count" : store.count(),
    }
    with open(settings.INGESTION_REPORT_PATH, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)

    print(f"\n[Report] Ingestion report saved to: {settings.INGESTION_REPORT_PATH}")

    print("\n" + "=" * 70)
    print(" INGESTION COMPLETE")
    print(f"  Products loaded   : {load_report['entries_built']}")
    print(f"  Chunks built      : {chunk_stats['chunks_built']}")
    print(f"  Duplicates skipped: {chunk_stats['duplicates_skipped']}")
    print(f"  DB total          : {store.count()} document(s)")
    print(f"  Warnings          : {len(load_report.get('warnings', []))}")
    print("=" * 70 + "\n")


def run_server() -> None:
    """Start the FastAPI verification server via uvicorn."""
    import uvicorn
    from config.settings import settings

    print("\n" + "=" * 70)
    print(f"  SabiLens — NAFDAC Verification API")
    print(f"  URL:  http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"  Docs: http://localhost:{settings.API_PORT}/docs")
    print("=" * 70 + "\n")

    uvicorn.run(
        "api.app:app",
        host      = settings.API_HOST,
        port      = settings.API_PORT,
        reload    = False,
        log_level = "info",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description = "SabiLens NAFDAC Food Product RAG System",
        formatter_class = argparse.RawDescriptionHelpFormatter,
        epilog = """
Examples:
  python main.py --mode ingest    # Ingest database (run once, or after updates)
  python main.py --mode serve     # Start API server
  python main.py                  # Default: ingest
        """,
    )
    parser.add_argument(
        "--mode",
        choices = ["ingest", "serve"],
        default = "ingest",
        help    = "Operation mode (default: ingest)",
    )
    args = parser.parse_args()

    if args.mode == "ingest":
        run_ingestion()
    else:
        run_server()


if __name__ == "__main__":
    main()