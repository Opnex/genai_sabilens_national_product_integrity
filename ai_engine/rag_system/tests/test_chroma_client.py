"""
tests/test_chroma_client.py
----------------------------
Integration tests for vectorstore/chroma_client.py.

Uses ChromaDB's in-memory EphemeralClient (no disk I/O) so tests are fast,
isolated, and leave no side effects on the persistent chroma_db/ directory.

The test module patches settings.CHROMA_PERSIST_DIR with a temp directory
so ChromaStore() uses an ephemeral store automatically.

Verifies:
  - ChromaStore instantiates and creates/opens the collection
  - ingest() upserts chunks without errors
  - count() reflects the correct number of stored documents
  - query() returns results with the expected shape
  - query() with a WHERE filter returns only matching metadata records
  - Duplicate upsert (re-ingest same IDs) does NOT create duplicates
  - reset_collection() wipes the collection back to 0 documents
  - Mismatched chunks/embeddings raises a clear ValueError

Run:
    pytest tests/test_chroma_client.py -v
    (skipped if chromadb is not installed)
"""
import sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
chromadb = pytest.importorskip("chromadb", reason="chromadb not installed")

from ingestion.schema import ProductChunk


# ── Helpers ────────────────────────────────────────────────────────────────────

DIMENSION = 4   # Tiny vectors — tests don't require real embeddings

def _unit_vec(values: list) -> list[float]:
    """Return a simple L2-normalised vector from raw values."""
    import math
    norm = math.sqrt(sum(x * x for x in values))
    return [x / norm for x in values]

def _make_chunk(chunk_id: str, nafdac: str, product: str, subcategory: str, expiry: str) -> ProductChunk:
    return ProductChunk(
        chunk_id        = chunk_id,
        text            = f"Product: {product}. NAFDAC No: {nafdac}. Category: {subcategory}.",
        metadata        = {
            "nafdac_no"        : nafdac,
            "nafdac_no_clean"  : nafdac,
            "product_name"     : product,
            "product_name_upper": product.upper(),
            "subcategory"      : subcategory,
            "presentation"     : "Test Presentation",
            "applicant_name"   : "Test Applicant Ltd",
            "country"          : "Nigeria",
            "manufacturer"     : "Test Manufacturer Ltd",
            "expiry_date_raw"  : f"{expiry} 00:00:00",
            "expiry_date_iso"  : expiry,
        },
        subcategory     = subcategory,
        nafdac_no_clean = nafdac,
        expiry_date_iso = expiry,
    )


# Pre-built fixtures mirroring real products
CHUNK_CORN_FLAKES = _make_chunk("abc001", "A8-4114", "KELLOGG'S CORN FLAKES",
                                 "Cereals and Cereal Products", "2029-07-30")
CHUNK_LIPTON      = _make_chunk("abc002", "01-0132", "LIPTON YELLOW LABEL TEA",
                                 "Beverages", "2026-03-28")
CHUNK_VASELINE    = _make_chunk("abc003", "02-0385", "Vaseline blueseal petroleum jelly",
                                 "Cosmetics", "2028-12-20")
CHUNK_INDOMIE     = _make_chunk("abc004", "01-0877", "INDOMIE INSTANT NOODLES CHICKEN FLAVOR",
                                 "Cereals and Cereal Products", "2027-01-26")

ALL_CHUNKS     = [CHUNK_CORN_FLAKES, CHUNK_LIPTON, CHUNK_VASELINE, CHUNK_INDOMIE]
ALL_EMBEDDINGS = [
    _unit_vec([1.0, 0.1, 0.0, 0.0]),
    _unit_vec([0.1, 1.0, 0.0, 0.0]),
    _unit_vec([0.0, 0.1, 1.0, 0.0]),
    _unit_vec([0.9, 0.2, 0.0, 0.1]),
]


# ── Fixture: fresh ephemeral ChromaStore for each test ────────────────────────

@pytest.fixture
def store(tmp_path, monkeypatch):
    """
    Provide a fresh ChromaStore backed by a temp directory for each test.
    Uses a unique collection name per test to guarantee isolation.
    """
    import uuid
    from config import settings as settings_module
    monkeypatch.setattr(settings_module.settings, "CHROMA_PERSIST_DIR", str(tmp_path))
    monkeypatch.setattr(settings_module.settings, "CHROMA_COLLECTION_NAME",
                        f"test_{uuid.uuid4().hex[:8]}")
    from vectorstore.chroma_client import ChromaStore
    return ChromaStore()


# ══════════════════════════════════════════════════════════════════════════════
# Initialisation
# ══════════════════════════════════════════════════════════════════════════════

class TestChromaStoreInit:

    def test_store_instantiates(self, store):
        assert store is not None

    def test_initial_count_is_zero(self, store):
        assert store.count() == 0

    def test_collection_attribute_exists(self, store):
        assert store.collection is not None


# ══════════════════════════════════════════════════════════════════════════════
# ingest() — upsert
# ══════════════════════════════════════════════════════════════════════════════

class TestIngest:

    def test_ingest_4_chunks(self, store):
        store.ingest(ALL_CHUNKS, ALL_EMBEDDINGS)
        assert store.count() == 4

    def test_ingest_single_chunk(self, store):
        store.ingest([CHUNK_CORN_FLAKES], [ALL_EMBEDDINGS[0]])
        assert store.count() == 1

    def test_ingest_is_idempotent(self, store):
        """
        Re-ingesting the same chunks must NOT create duplicates (upsert semantics).
        """
        store.ingest(ALL_CHUNKS, ALL_EMBEDDINGS)
        store.ingest(ALL_CHUNKS, ALL_EMBEDDINGS)   # Second ingest — same IDs
        assert store.count() == 4

    def test_partial_reingest_updates_count(self, store):
        """Upserting a subset after a full ingest does not reduce the total count."""
        store.ingest(ALL_CHUNKS, ALL_EMBEDDINGS)
        store.ingest([CHUNK_CORN_FLAKES], [ALL_EMBEDDINGS[0]])
        assert store.count() == 4

    def test_mismatched_lengths_raises(self, store):
        with pytest.raises(ValueError, match="Length mismatch"):
            store.ingest(ALL_CHUNKS, ALL_EMBEDDINGS[:2])


# ══════════════════════════════════════════════════════════════════════════════
# query() — vector search
# ══════════════════════════════════════════════════════════════════════════════

class TestQuery:

    def test_query_returns_results_dict(self, store):
        store.ingest(ALL_CHUNKS, ALL_EMBEDDINGS)
        results = store.query(ALL_EMBEDDINGS[0], n_results=2)
        assert isinstance(results, dict)

    def test_query_has_expected_keys(self, store):
        store.ingest(ALL_CHUNKS, ALL_EMBEDDINGS)
        results = store.query(ALL_EMBEDDINGS[0], n_results=2)
        assert "ids"       in results
        assert "documents" in results
        assert "metadatas" in results
        assert "distances" in results

    def test_query_n_results_respected(self, store):
        store.ingest(ALL_CHUNKS, ALL_EMBEDDINGS)
        results = store.query(ALL_EMBEDDINGS[0], n_results=2)
        assert len(results["ids"][0]) == 2

    def test_query_top_result_is_most_similar(self, store):
        """
        Querying with CHUNK_CORN_FLAKES' own embedding should return
        CHUNK_CORN_FLAKES as the top (closest) result.
        """
        store.ingest(ALL_CHUNKS, ALL_EMBEDDINGS)
        results = store.query(ALL_EMBEDDINGS[0], n_results=4)
        top_id = results["ids"][0][0]
        assert top_id == CHUNK_CORN_FLAKES.chunk_id

    def test_query_distances_are_non_negative(self, store):
        store.ingest(ALL_CHUNKS, ALL_EMBEDDINGS)
        results = store.query(ALL_EMBEDDINGS[0], n_results=4)
        for dist in results["distances"][0]:
            assert dist >= 0

    def test_query_top_distance_is_near_zero_for_self(self, store):
        """A vector queried against itself should have cosine distance ≈ 0."""
        store.ingest(ALL_CHUNKS, ALL_EMBEDDINGS)
        results = store.query(ALL_EMBEDDINGS[0], n_results=1)
        top_dist = results["distances"][0][0]
        assert top_dist < 0.01, f"Self-distance too large: {top_dist}"

    def test_query_metadata_contains_product_name(self, store):
        store.ingest(ALL_CHUNKS, ALL_EMBEDDINGS)
        results = store.query(ALL_EMBEDDINGS[0], n_results=1)
        meta = results["metadatas"][0][0]
        assert "product_name" in meta
        assert meta["product_name"] == "KELLOGG'S CORN FLAKES"


# ══════════════════════════════════════════════════════════════════════════════
# query() with WHERE filter
# ══════════════════════════════════════════════════════════════════════════════

class TestQueryWithFilter:

    def test_where_filter_nafdac_no(self, store):
        """Filtering by nafdac_no_clean should return only that product."""
        store.ingest(ALL_CHUNKS, ALL_EMBEDDINGS)
        results = store.query(
            ALL_EMBEDDINGS[0], n_results=4,
            where={"nafdac_no_clean": "A8-4114"}
        )
        assert len(results["ids"][0]) == 1
        assert results["metadatas"][0][0]["nafdac_no_clean"] == "A8-4114"

    def test_where_filter_subcategory(self, store):
        """Filtering by subcategory='Cereals and Cereal Products' → 2 results."""
        store.ingest(ALL_CHUNKS, ALL_EMBEDDINGS)
        results = store.query(
            ALL_EMBEDDINGS[0], n_results=10,
            where={"subcategory": "Cereals and Cereal Products"}
        )
        assert len(results["ids"][0]) == 2
        for meta in results["metadatas"][0]:
            assert meta["subcategory"] == "Cereals and Cereal Products"

    def test_where_filter_nonexistent_nafdac(self, store):
        """Querying for a NAFDAC number not in the collection returns 0 results."""
        store.ingest(ALL_CHUNKS, ALL_EMBEDDINGS)
        results = store.query(
            ALL_EMBEDDINGS[0], n_results=4,
            where={"nafdac_no_clean": "FAKE-999"}
        )
        assert len(results["ids"][0]) == 0


# ══════════════════════════════════════════════════════════════════════════════
# reset_collection()
# ══════════════════════════════════════════════════════════════════════════════

class TestResetCollection:

    def test_reset_clears_all_documents(self, store):
        store.ingest(ALL_CHUNKS, ALL_EMBEDDINGS)
        assert store.count() == 4
        store.reset_collection()
        assert store.count() == 0

    def test_can_ingest_after_reset(self, store):
        store.ingest(ALL_CHUNKS, ALL_EMBEDDINGS)
        store.reset_collection()
        store.ingest([CHUNK_CORN_FLAKES], [ALL_EMBEDDINGS[0]])
        assert store.count() == 1
