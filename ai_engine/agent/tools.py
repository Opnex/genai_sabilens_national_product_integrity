"""
agent/tools.py
---------------
LlamaIndex FunctionTool wrappers around the existing ProductRetriever methods.

WHY THIS FILE EXISTS
  The agent cannot call retriever methods directly — it needs each capability
  packaged as a named, documented FunctionTool so the ReAct reasoning engine
  can decide at runtime which tool to invoke based on observations.

  Every tool here wraps code that ALREADY EXISTS in retrieval/retriever.py
  and retrieval/subcategory_alignment.py.  No new retrieval logic lives here.

TOOLS DEFINED
  lookup_nafdac_tool        Exact NAFDAC number lookup  (Strategy 1)
  semantic_search_tool      Text similarity search      (Strategy 2)
  browse_category_tool      Category sweep              (Strategy 3)
  check_expiry_tool         Expiry date evaluation
  check_alignment_tool      Subcategory mismatch check

USAGE
  tools = build_tools(retriever)          # retriever = ProductRetriever()
  result = tools["lookup_nafdac"]("A8-4114")
"""

from datetime import date, timedelta
from llama_index.core.tools import FunctionTool

from ai_engine.rag_system.retrieval.retriever           import ProductRetriever
from ai_engine.rag_system.retrieval.subcategory_alignment import check_subcategory_alignment
from ai_engine.rag_system.config.settings               import settings


# ── Shared retriever instance ──────────────────────────────────────────────────
# Passed in from the agent so we share one embedder + ChromaDB connection.


def build_tools(retriever: ProductRetriever) -> dict:
    """
    Build all five agent tools and return them as a named dict.

    Args:
        retriever: A shared ProductRetriever instance (loaded once at startup).

    Returns:
        Dict mapping tool name -> FunctionTool.
        Keys: "lookup_nafdac", "semantic_search", "browse_category",
              "check_expiry", "check_alignment"

    Example:
        retriever = ProductRetriever()
        tools = build_tools(retriever)
        records = tools["lookup_nafdac"].fn("A8-4114")
    """
    # ── Tool 1: Exact NAFDAC lookup ───────────────────────────────────────────

    def lookup_nafdac(nafdac_no: str) -> list:
        """
        Look up a NAFDAC number in the product database.

        Normalises the input (strips non-breaking spaces, fixes dashes)
        before querying so raw OCR output can be passed directly.

        Returns a list of matching product records (usually 1, rarely more).
        Returns an empty list if the number is not found.

        Args:
            nafdac_no: Raw NAFDAC number string.  Examples: 'A8-4114', '01-0132'
        """
        return retriever.retrieve_by_nafdac_no(nafdac_no)

    # ── Tool 2: Semantic product text search ─────────────────────────────────

    def semantic_search(product_text: str, n: int = 5) -> list:
        """
        Search the product database using any text visible on the label.

        Use this when the NAFDAC number is unreadable, damaged, or when
        lookup_nafdac returned an empty result.

        Returns a ranked list of candidate products with similarity scores.
        Results below the similarity threshold (0.68) are automatically filtered.

        Args:
            product_text: Any label text — brand name, product name, description.
                          Examples: 'kelloggs corn flakes', 'indomie chicken noodles'
            n:            Maximum candidates to return (default 5).
        """
        return retriever.retrieve_by_product_text(product_text, n=n)

    # ── Tool 3: Category browse ───────────────────────────────────────────────

    def browse_category(subcategory: str) -> list:
        """
        Return all registered products in a given subcategory.

        Use this when you need to cross-validate a suspicious scan against
        all products in a category, or to provide context for the reasoning.

        Valid subcategory values (exact strings from the database):
            'Cereals and Cereal Products'
            'Cosmetics'
            'Fats and oils, and Fat Emulsions'
            'Salts, Spices, Soups, Sauces, Salads and Seasoning'
            'Beverages'
            'Sweeteners'

        Args:
            subcategory: Exact subcategory name string.
        """
        return retriever.retrieve_by_subcategory(subcategory)

    # ── Tool 4: Expiry check ──────────────────────────────────────────────────

    def check_expiry(expiry_date_iso: str) -> dict:
        """
        Evaluate whether a product registration is expired or near expiry.

        Args:
            expiry_date_iso: ISO date string 'YYYY-MM-DD' from the product record.
                             Pass empty string '' if unavailable.

        Returns:
            Dict with keys:
                is_valid        (bool)        True if not expired
                is_near_expiry  (bool)        True if within 60 days of expiry
                days_remaining  (int | None)  Days until expiry
                severity        (str)         'NONE', 'WARNING', or 'EXPIRED'
                message         (str)         Human-readable status
        """
        if not expiry_date_iso:
            return {
                "is_valid": True, "is_near_expiry": False,
                "expiry_date": None, "days_remaining": None,
                "severity": "NONE", "message": "No expiry date on record.",
            }
        try:
            expiry = date.fromisoformat(expiry_date_iso)
            today  = date.fromisoformat(settings.REFERENCE_DATE)
            delta  = (expiry - today).days
            if delta < 0:
                return {
                    "is_valid": False, "is_near_expiry": False,
                    "expiry_date": expiry_date_iso, "days_remaining": delta,
                    "severity": "EXPIRED",
                    "message": (
                        f"Registration expired on {expiry_date_iso} "
                        f"({abs(delta)} day(s) ago). No longer authorised for sale."
                    ),
                }
            elif delta <= 60:
                return {
                    "is_valid": True, "is_near_expiry": True,
                    "expiry_date": expiry_date_iso, "days_remaining": delta,
                    "severity": "WARNING",
                    "message": (
                        f"Registration expires on {expiry_date_iso} "
                        f"(in {delta} day(s)). Valid but renewal is due soon."
                    ),
                }
            else:
                return {
                    "is_valid": True, "is_near_expiry": False,
                    "expiry_date": expiry_date_iso, "days_remaining": delta,
                    "severity": "NONE",
                    "message": f"Registration valid until {expiry_date_iso} ({delta} day(s) remaining).",
                }
        except (ValueError, TypeError) as exc:
            return {
                "is_valid": True, "is_near_expiry": False,
                "expiry_date": expiry_date_iso, "days_remaining": None,
                "severity": "NONE",
                "message": f"Could not parse expiry date '{expiry_date_iso}': {exc}",
            }

    # ── Tool 5: Subcategory alignment check ───────────────────────────────────

    def check_alignment(scanned_subcategory: str, registered_subcategory: str) -> dict:
        """
        Check whether the scanned product type matches its NAFDAC registration.

        This is the primary counterfeit detection signal. A valid NAFDAC number
        used on a product of the wrong type is the strongest sign of forgery.

        Args:
            scanned_subcategory:    Product type from A1/A2 pipeline (raw text OK).
                                    Examples: 'corn flakes', 'cosmetics', 'cooking oil'
            registered_subcategory: Subcategory stored in the database record.
                                    Examples: 'Cereals and Cereal Products', 'Cosmetics'

        Returns:
            Dict with keys:
                is_match        (bool)        True if categories align
                scanned_norm    (str)         Normalised scanned category
                registered_norm (str)         Normalised registered category
                mismatch_type   (str | None)  Description of the mismatch
                severity        (str)         'NONE' or 'CRITICAL'
                message         (str)         Human-readable alignment result
        """
        return check_subcategory_alignment(scanned_subcategory, registered_subcategory)

    # ── Wrap all five as FunctionTools and return ─────────────────────────────
    return {
        "lookup_nafdac"   : FunctionTool.from_defaults(fn=lookup_nafdac),
        "semantic_search" : FunctionTool.from_defaults(fn=semantic_search),
        "browse_category" : FunctionTool.from_defaults(fn=browse_category),
        "check_expiry"    : FunctionTool.from_defaults(fn=check_expiry),
        "check_alignment" : FunctionTool.from_defaults(fn=check_alignment),
    }
