"""
vectorstore/embedder.py
-----------------------
Thin, reusable wrapper around a SentenceTransformer embedding model.

SINGLE RESPONSIBILITY
  Convert text strings → fixed-size float vectors.
  Nothing else.  No ChromaDB, no Greenbook logic, no retrieval here.

WHY ISOLATE THIS?
  • Model loading is expensive (~300–500 ms on first call).
    Load once at module level, reuse for all subsequent requests.
  • Swapping models (MiniLM → MPNet, or adding a multilingual model for
    Yoruba/Hausa/Pidgin support) requires editing exactly one file.
  • The retrieval layer and ingestion pipeline share the same Embedder
    instance so embeddings are guaranteed consistent.

MODEL NOTES
  Default: all-MiniLM-L6-v2
    • 384-dimensional output vectors
    • ≈ 80 MB model size
    • ≈ 10–30 ms per batch on CPU
    • Strong cosine-similarity performance on product and brand name text

  Override via environment variable EMBEDDING_MODEL for:
    • Higher accuracy : 'all-mpnet-base-v2'          (768-dim, 3× slower)
    • Multilingual    : 'paraphrase-multilingual-MiniLM-L12-v2'

NORMALISATION
  normalize_embeddings=True is set in both embed() and embed_single() so
  all vectors are L2-normalised before storage.  This is required for
  ChromaDB's cosine distance metric to behave correctly.
"""

from sentence_transformers import SentenceTransformer
from config.settings import settings


class Embedder:
    """
    Loads a SentenceTransformer model once and exposes two methods:
      embed()        — batch encode many texts (ingestion path)
      embed_single() — encode one text string (retrieval path)

    Usage:
        embedder = Embedder()

        # Bulk ingestion
        vectors = embedder.embed(["Product: Indomie...", "Product: Dangote Sugar..."])

        # Single query at retrieval time
        vec = embedder.embed_single("indomie noodles kelloggs corn flakes")
    """

    def __init__(self):
        print(f"[Embedder] Loading model: {settings.EMBEDDING_MODEL}")
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.dimension: int = self.model.get_sentence_embedding_dimension()
        print(f"[Embedder] ✅  Model ready  — embedding dimension: {self.dimension}")

    def embed(self, texts: list[str]) -> list[list[float]]:
        """
        Batch-embed a list of text strings.  Used during ingestion.

        Processes in batches of EMBEDDING_BATCH_SIZE (default 64) to balance
        memory usage and throughput.  The progress bar is printed to stdout
        so ingestion logs show how far through the dataset we are.

        With 15 products this completes in under a second; the batch size
        matters for production-scale datasets with thousands of products.

        Args:
            texts: List of chunk text strings to embed.

        Returns:
            List of float vectors in the same order as the input texts.
            Each vector has length == self.dimension (384 for MiniLM).
        """
        return (
            self.model.encode(
                texts,
                batch_size         = settings.EMBEDDING_BATCH_SIZE,
                show_progress_bar  = True,
                convert_to_numpy   = True,
                normalize_embeddings = True,   # Required for cosine similarity
            ).tolist()
        )

    def embed_single(self, text: str) -> list[float]:
        """
        Embed a single query string.  Used at retrieval time.

        This is faster than calling embed([text]) because it skips
        batch-processing overhead.

        Args:
            text: Any product-related search string.  Examples:
                    "kelloggs corn flakes nigeria"
                    "unilever deodorant cosmetics"
                    "A8-4114"  (raw NAFDAC number typed by user)

        Returns:
            Single float vector of length self.dimension.
        """
        return (
            self.model.encode(
                [text],
                normalize_embeddings = True,
            )[0].tolist()
        )