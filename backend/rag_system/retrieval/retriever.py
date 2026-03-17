"""
retrieval/retriever.py
-----------------------
Provides all retrieval strategies used by the regulatory scoring layer and API.

THREE RETRIEVAL STRATEGIES — choose based on what the OCR / A2 pipeline provides:

  Strategy 1  retrieve_by_nafdac_no()   EXACT metadata match on nafdac_no_clean
  ─────────── Use when: OCR delivers a clean, readable NAFDAC number.
              Speed: Fastest — metadata pre-filter, negligible vector scan.
              Accuracy: Deterministic.

  Strategy 2  retrieve_by_product_text()  SEMANTIC vector similarity search
  ─────────── Use when: NAFDAC number is damaged or missing but product name,
              brand, or packaging text is visible.
              Speed: Slower — full collection scan across all embeddings.
              Accuracy: Probabilistic; results ranked by cosine similarity.

  Strategy 3  retrieve_by_subcategory()  CATEGORY-filtered semantic search
  ─────────── Use when: A4 fusion engine needs a category context sweep,
              or the D5 dashboard displays products by category.
              Speed: Medium — metadata pre-filter reduces the search space.

SEPARATION OF CONCERNS
  This module retrieves records from ChromaDB and converts raw distances
  into similarity scores.  It does NOT score products, detect mismatches,
  or make pass/fail verdicts — that belongs in regulatory_scorer.py.
"""

from vectorstore.chroma_client import ChromaStore
from vectorstore.embedder      import Embedder
from utils.nafdac_normalizer   import normalize_nafdac_no
from config.settings           import settings


class ProductRetriever:
    """
    Retrieves NAFDAC product records from ChromaDB using three strategies.

    Instantiate once; the model and ChromaDB client are loaded at __init__
    time and reused for every request — never instantiate per HTTP request.

    Usage:
        retriever = ProductRetriever()
        records   = retriever.retrieve_by_nafdac_no("A8 - 4114")
        candidates = retriever.retrieve_by_product_text("kelloggs cereal nigeria")
    """

    def __init__(self):
        self.store    = ChromaStore()
        self.embedder = Embedder()

    # ── Strategy 1: Exact NAFDAC number lookup ────────────────────────────────

    def retrieve_by_nafdac_no(self, raw_nafdac: str) -> list[dict]:
        """
        Primary retrieval path: exact metadata match on the clean NAFDAC number.

        Normalises the raw input before lookup so OCR artefacts like
        leading non-breaking spaces, dashes with spaces, or en-dashes are
        cleaned to canonical form before the WHERE filter is applied.

        Returns a list (not a single record) because the system is designed
        to handle duplicate registrations gracefully — even though the current
        15-row demo dataset has no duplicates, production data may.

        Args:
            raw_nafdac: Raw NAFDAC number string from OCR output.
                        Examples: 'A8-4114', '\\xa001-0132', 'A8 - 4114'

        Returns:
            List of metadata dicts matching the normalised NAFDAC number.
            Empty list if the number cannot be normalised or is not in the DB.

        Example:
            >>> records = retriever.retrieve_by_nafdac_no("\\xa001-0132")
            >>> records[0]["product_name"]
            'LIPTON YELLOW LABEL TEA'
        """
        nafdac_clean = normalize_nafdac_no(raw_nafdac)

        if not nafdac_clean:
            # Cannot normalise — no lookup possible
            return []

        results = self.store.query(
            query_embedding = self.embedder.embed_single(nafdac_clean),
            n_results       = 10,   # Allow duplicates; typical is 1
            where           = {"nafdac_no_clean": nafdac_clean},
        )

        if not results["ids"] or not results["ids"][0]:
            return []

        return [results["metadatas"][0][i] for i in range(len(results["ids"][0]))]

    # ── Strategy 2: Semantic product text search ──────────────────────────────

    def retrieve_by_product_text(
        self,
        product_text: str,
        n: int = 5,
    ) -> list[dict]:
        """
        Semantic fallback: full vector similarity search on product-related text.

        Use when the NAFDAC number is unreadable but brand name, product name,
        or packaging description text is legible.

        Only returns results with similarity_score ≥ SIMILARITY_THRESHOLD (0.68).
        Results below the threshold are silently discarded — they are noise.

        Args:
            product_text: Any product-related text from the label or OCR.
                          Examples:
                            "kelloggs corn flakes 300g"
                            "indomie noodles chicken flavor dufil"
                            "unilever vaseline lotion cosmetics"
            n:            Maximum results to consider before threshold filtering.

        Returns:
            List of dicts, each containing:
              metadata         (dict)  — full product metadata record
              text             (str)   — chunk text that matched
              similarity_score (float) — 0.0–1.0 (higher = closer match)
            Ordered by similarity_score descending.
            Empty list if no result exceeds SIMILARITY_THRESHOLD.

        Example:
            >>> results = retriever.retrieve_by_product_text("indomie chicken noodles")
            >>> results[0]["similarity_score"]
            0.912
            >>> results[0]["metadata"]["product_name"]
            'INDOMIE INSTANT NOODLES CHICKEN FLAVOR'
        """
        if not product_text or not product_text.strip():
            return []

        embedding = self.embedder.embed_single(product_text.strip())
        results   = self.store.query(query_embedding=embedding, n_results=n)

        if not results["ids"] or not results["ids"][0]:
            return []

        output = []
        for i in range(len(results["ids"][0])):
            # ChromaDB cosine distance: 0.0 = identical, 2.0 = opposite.
            # Convert to similarity score:  score = 1.0 − (distance / 2.0)
            # Valid because all embeddings are L2-normalised.
            distance    = results["distances"][0][i]
            similarity  = round(1.0 - (distance / 2.0), 4)

            if similarity < settings.SIMILARITY_THRESHOLD:
                continue

            output.append({
                "metadata"        : results["metadatas"][0][i],
                "text"            : results["documents"][0][i],
                "similarity_score": similarity,
            })

        # Sort descending — ChromaDB already does this, but be explicit
        output.sort(key=lambda x: x["similarity_score"], reverse=True)
        return output

    # ── Strategy 3: Subcategory-filtered browse ───────────────────────────────

    def retrieve_by_subcategory(
        self,
        subcategory: str,
        n: int = 20,
    ) -> list[dict]:
        """
        Return all products belonging to a specific subcategory.

        Used by:
          • D5 Dashboard   — category browse panel
          • A4 Fusion      — gathering category context for cross-validation
          • /category API  — endpoint for manufacturer intelligence portal

        Valid subcategory values (from real data):
          'Cereals and Cereal Products'
          'Cosmetics'
          'Fats and oils, and Fat Emulsions'
          'Salts, Spices, Soups, Sauces, Salads and Seasoning'
          'Beverages'
          'Sweeteners'

        Args:
            subcategory: Exact subcategory string (case-sensitive as stored).
            n:           Maximum records to return.

        Returns:
            List of metadata dicts for products in that subcategory.
            Empty list if no records found.
        """
        results = self.store.query(
            query_embedding = self.embedder.embed_single(subcategory),
            n_results       = n,
            where           = {"subcategory": subcategory},
        )

        if not results["ids"] or not results["ids"][0]:
            return []

        return results["metadatas"][0]

    # ── Strategy 4: Applicant / manufacturer search ───────────────────────────

    def retrieve_by_applicant(
        self,
        applicant_text: str,
        n: int = 20,
    ) -> list[dict]:
        """
        Semantic search scoped to a company name fragment.

        Useful for brand-owner portals: a company can verify which of their
        products are registered and flag ones being counterfeited.

        Args:
            applicant_text: Company name fragment (partial is fine).
                            Examples: "Unilever", "Dangote", "Kellogg"
            n:              Maximum results.

        Returns:
            List of metadata dicts where applicant_name contains the fragment.
            Empty list if no matching products found.
        """
        if not applicant_text or not applicant_text.strip():
            return []

        results = self.store.query(
            query_embedding = self.embedder.embed_single(applicant_text),
            n_results       = n,
        )

        if not results["ids"] or not results["ids"][0]:
            return []

        fragment_lower = applicant_text.lower()
        return [
            results["metadatas"][0][i]
            for i in range(len(results["ids"][0]))
            if fragment_lower in results["metadatas"][0][i]
                                 .get("applicant_name", "").lower()
        ]