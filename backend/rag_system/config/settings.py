"""
config/settings.py
------------------
Single source of truth for every tuneable constant in the SabiLens RAG system.

All values are read from environment variables at import time so that the
same codebase can run in dev, staging, and production without code changes.
Override anything by setting the matching env var or dropping a .env file
at the project root (loaded automatically by main.py via python-dotenv).

Usage:
    from config.settings import settings
    print(settings.DATABASE_PATH)   # './data/raw/nafdac_database.xlsx'
"""

import os
from pathlib import Path


class Settings:
    """
    Centralised configuration object.  Instantiate once at module level;
    import the 'settings' singleton everywhere else — never call Settings()
    a second time.
    """

    # ── Data paths ─────────────────────────────────────────────────────────────
    # Primary NAFDAC food-product database (Excel).
    DATABASE_PATH: str = os.getenv(
        "DATABASE_PATH", "./data/raw/nafdac_database.xlsx"
    )
    # JSON audit dump written after each ingestion run.
    CHUNKS_JSON_PATH: str = os.getenv(
        "CHUNKS_JSON_PATH", "./data/processed/nafdac_chunks.json"
    )
    # Human-readable ingestion report (row counts, warnings, category stats).
    INGESTION_REPORT_PATH: str = os.getenv(
        "INGESTION_REPORT_PATH", "./data/processed/ingestion_report.json"
    )

    # ── ChromaDB ────────────────────────────────────────────────────────────────
    # Persistent directory — embeddings survive server restarts.
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    CHROMA_COLLECTION_NAME: str = os.getenv(
        "CHROMA_COLLECTION_NAME", "nafdac_food_products"
    )

    # ── Embedding model ─────────────────────────────────────────────────────────
    # all-MiniLM-L6-v2  : 384-dim, ~80 MB, fast on CPU — good default.
    # all-mpnet-base-v2  : 768-dim, higher accuracy, 3× slower.
    # paraphrase-multilingual-MiniLM-L12-v2 : multilingual (Yoruba/Hausa/Pidgin).
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    # Batch size for bulk embedding — reduce to 32 on low-RAM machines.
    EMBEDDING_BATCH_SIZE: int = int(os.getenv("EMBEDDING_BATCH_SIZE", "64"))

    # ── Retrieval thresholds ────────────────────────────────────────────────────
    # Minimum cosine similarity accepted as a valid semantic match.
    # Results below this are discarded — they are noise, not real matches.
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.68"))

    # ── Date / expiry logic ─────────────────────────────────────────────────────
    # Reference date used when checking whether a product's expiry_date has passed.
    # Unlike the Greenbook dataset, this new database has FUTURE expiry dates
    # (2026–2031), so expiry checks are meaningful and enforced as hard failures.
    # In production set this env var to dynamically reflect today:
    #   export REFERENCE_DATE=$(date +%Y-%m-%d)
    REFERENCE_DATE: str = os.getenv("REFERENCE_DATE", "2026-03-03")

    # ── API ─────────────────────────────────────────────────────────────────────
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_TITLE: str = "SabiLens NAFDAC Food Product RAG API"
    API_VERSION: str = "1.0.0"


# Module-level singleton — import this object, never re-instantiate the class.
settings = Settings()