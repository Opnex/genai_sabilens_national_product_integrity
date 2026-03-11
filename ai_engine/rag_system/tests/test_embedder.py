"""
tests/test_embedder.py
-----------------------
Unit tests for vectorstore/embedder.py.

These tests do NOT require a GPU or network access.  The sentence-transformers
library is expected to be installed; the model is loaded once per test session.

Verifies:
  - Embedder instantiates and loads the configured model
  - embed() returns the correct number of vectors at the right dimension
  - embed_single() returns a single vector at the right dimension
  - All vectors are L2-normalised (required for ChromaDB cosine metric)
  - Semantically similar texts produce higher cosine similarity than dissimilar ones
  - Batch embedding and single embedding produce consistent vectors

Run:
    pytest tests/test_embedder.py -v
    (skipped automatically if sentence-transformers is not installed)
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest

# Skip entire module if sentence-transformers is not installed
st = pytest.importorskip("sentence_transformers", reason="sentence-transformers not installed")

from vectorstore.embedder import Embedder


# ── Module-level fixture: load the model once for all tests ───────────────────

@pytest.fixture(scope="module")
def embedder():
    """Instantiate Embedder once per test session to avoid repeated model loads."""
    return Embedder()


# ── Helper ────────────────────────────────────────────────────────────────────

def cosine_similarity(a: list, b: list) -> float:
    """Compute cosine similarity between two L2-normalised vectors."""
    dot   = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(y * y for y in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)

def l2_norm(v: list) -> float:
    return math.sqrt(sum(x * x for x in v))


# ══════════════════════════════════════════════════════════════════════════════
# Embedder initialisation
# ══════════════════════════════════════════════════════════════════════════════

class TestEmbedderInit:

    def test_embedder_instantiates(self, embedder):
        assert embedder is not None

    def test_dimension_is_positive(self, embedder):
        assert embedder.dimension > 0

    def test_dimension_is_384_for_minilm(self, embedder):
        """all-MiniLM-L6-v2 produces 384-dim vectors."""
        assert embedder.dimension == 384


# ══════════════════════════════════════════════════════════════════════════════
# embed() — batch encoding
# ══════════════════════════════════════════════════════════════════════════════

class TestBatchEmbed:

    TEXTS = [
        "Product: KELLOGG'S CORN FLAKES. NAFDAC No: A8-4114. Category: Cereals and Cereal Products.",
        "Product: LIPTON YELLOW LABEL TEA. NAFDAC No: 01-0132. Category: Beverages.",
        "Product: Vaseline blueseal pure petroleum jelly original. NAFDAC No: 02-0385. Category: Cosmetics.",
        "Product: INDOMIE INSTANT NOODLES CHICKEN FLAVOR. NAFDAC No: 01-0877.",
        "Product: DANGOTE SUGAR REFINED GRANULATED WHITE SUGAR. NAFDAC No: A8-100798.",
    ]

    def test_returns_list(self, embedder):
        vectors = embedder.embed(self.TEXTS)
        assert isinstance(vectors, list)

    def test_correct_count(self, embedder):
        vectors = embedder.embed(self.TEXTS)
        assert len(vectors) == len(self.TEXTS)

    def test_correct_dimension(self, embedder):
        vectors = embedder.embed(self.TEXTS)
        for v in vectors:
            assert len(v) == embedder.dimension

    def test_all_vectors_are_floats(self, embedder):
        vectors = embedder.embed(self.TEXTS)
        for v in vectors:
            assert all(isinstance(x, float) for x in v)

    def test_all_vectors_l2_normalised(self, embedder):
        """normalize_embeddings=True must produce unit vectors (L2 norm ≈ 1.0)."""
        vectors = embedder.embed(self.TEXTS)
        for i, v in enumerate(vectors):
            norm = l2_norm(v)
            assert abs(norm - 1.0) < 1e-5, \
                f"Vector {i} not L2-normalised: norm={norm}"

    def test_single_text_batch(self, embedder):
        vectors = embedder.embed(["single text"])
        assert len(vectors) == 1
        assert len(vectors[0]) == embedder.dimension

    def test_empty_batch_returns_empty(self, embedder):
        vectors = embedder.embed([])
        assert vectors == [] or len(vectors) == 0


# ══════════════════════════════════════════════════════════════════════════════
# embed_single() — single query encoding
# ══════════════════════════════════════════════════════════════════════════════

class TestEmbedSingle:

    def test_returns_list(self, embedder):
        v = embedder.embed_single("indomie noodles")
        assert isinstance(v, list)

    def test_correct_dimension(self, embedder):
        v = embedder.embed_single("kelloggs corn flakes nigeria")
        assert len(v) == embedder.dimension

    def test_all_floats(self, embedder):
        v = embedder.embed_single("vaseline cosmetics")
        assert all(isinstance(x, float) for x in v)

    def test_l2_normalised(self, embedder):
        v = embedder.embed_single("dangote sugar sweeteners")
        assert abs(l2_norm(v) - 1.0) < 1e-5


# ══════════════════════════════════════════════════════════════════════════════
# Semantic consistency checks
# ══════════════════════════════════════════════════════════════════════════════

class TestSemanticConsistency:
    """
    Verify that embeddings encode meaningful semantic relationships.
    These are soft checks — we test direction of similarity, not exact values.
    """

    def test_identical_text_has_max_similarity(self, embedder):
        text = "KELLOGG'S CORN FLAKES NAFDAC A8-4114 Cereals"
        v1 = embedder.embed_single(text)
        v2 = embedder.embed_single(text)
        sim = cosine_similarity(v1, v2)
        assert sim > 0.999

    def test_similar_products_more_similar_than_dissimilar(self, embedder):
        """
        'indomie noodles cereal' should be closer to 'corn flakes breakfast cereal'
        than to 'vaseline petroleum jelly cosmetics'.
        """
        query   = embedder.embed_single("indomie noodles cereal")
        similar = embedder.embed_single("corn flakes breakfast cereal")
        differ  = embedder.embed_single("vaseline petroleum jelly cosmetics skin")
        assert cosine_similarity(query, similar) > cosine_similarity(query, differ)

    def test_batch_and_single_produce_consistent_vectors(self, embedder):
        """
        embed([text])[0] and embed_single(text) should produce the same vector.
        """
        text    = "LIPTON YELLOW LABEL TEA Beverages NAFDAC 01-0132"
        batch   = embedder.embed([text])[0]
        single  = embedder.embed_single(text)
        sim     = cosine_similarity(batch, single)
        assert sim > 0.999, f"Batch and single vectors diverged: sim={sim}"
