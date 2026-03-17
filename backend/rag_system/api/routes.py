"""
api/routes.py
-------------
FastAPI router — all HTTP endpoints for the SabiLens NAFDAC RAG service.

SINGLE RESPONSIBILITY
  This module handles HTTP concerns only: request parsing, routing, error
  codes, and response serialisation.  All business logic lives in:
    retrieval/retriever.py          (finding records)
    retrieval/regulatory_scorer.py  (computing verdicts)
    retrieval/subcategory_alignment.py (category comparison)

ENDPOINTS
  POST  /verify/product          Main scan endpoint (D3 mobile app)
  GET   /verify/lookup/{nafdac}  Raw NAFDAC lookup (D5 dashboard)
  POST  /verify/search           Semantic text search fallback
  GET   /verify/category/{name}  Category browse (manufacturer portal / D5)
  GET   /verify/health           Health + collection count check (D7 DevOps)

CONSUMERS
  D1 Backend Lead  — integrates this router into the main FastAPI app
  D3 Mobile App    — calls POST /verify/product after every scan
  D5 Dashboard     — calls GET /verify/lookup and GET /verify/category
  D7 DevOps        — calls GET /verify/health in uptime monitoring
"""

from fastapi  import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing   import Optional

from retrieval.retriever import ProductRetriever
from retrieval.regulatory_scorer import compute_verification_score

# ── Router setup ──────────────────────────────────────────────────────────────

router = APIRouter(prefix="/verify", tags=["Product Verification"])

# Single instance — loaded once when the module is first imported.
# Model + ChromaDB client loading is expensive; NEVER instantiate per-request.
_retriever = ProductRetriever()


# ── Request / Response schemas ─────────────────────────────────────────────────

class VerifyRequest(BaseModel):
    """
    Payload sent by the D1 backend after A2 OCR processing of a scanned label.

    Both fields are produced by the A1 (visual classification) and A2 (OCR)
    pipelines and forwarded here for regulatory scoring.
    """
    nafdac_no: str = Field(
        ...,
        description=(
            "Raw NAFDAC number extracted by OCR. May contain leading "
            "whitespace, non-breaking spaces, dashes with spaces, etc. "
            "Normalisation is applied internally."
        ),
        example="A8-4114",
    )
    scanned_subcategory: str = Field(
        ...,
        description=(
            "Product subcategory identified by the A1/A2 classification pipeline. "
            "Raw text is acceptable — alias normalisation is applied internally."
        ),
        example="Cereals and Cereal Products",
    )


class ExpiryCheckResult(BaseModel):
    """Nested expiry-layer result included in VerifyResponse."""
    is_valid:       bool
    is_near_expiry: bool
    expiry_date:    Optional[str] = None
    days_remaining: Optional[int] = None
    severity:       str
    message:        str


class AlignmentResult(BaseModel):
    """Nested subcategory-alignment result included in VerifyResponse."""
    is_match:        bool
    scanned_norm:    str
    registered_norm: str
    mismatch_type:   Optional[str] = None
    severity:        str
    message:         str


class VerifyResponse(BaseModel):
    """
    Full verification verdict returned to the D1 backend.

    Key fields for A4 Fusion Engine:
      verification_score — 0.0–1.0 signal weight
      severity           — 'NONE', 'WARNING', 'HIGH', 'CRITICAL'

    Key fields for D6 N-ATLAS translation:
      detail             — full English explanation to translate to
                           Yoruba / Hausa / Pidgin

    Key fields for D5 Dashboard display:
      matched_record     — full product metadata to render in the UI
    """
    nafdac_no:            str
    verified:             bool
    verification_score:   float = Field(ge=0.0, le=1.0)
    status_code:          str
    severity:             str
    summary:              str
    detail:               str
    expiry_check:         Optional[ExpiryCheckResult] = None
    alignment:            Optional[AlignmentResult]   = None
    matched_record:       Optional[dict]              = None
    duplicate_count:      int   = Field(
        default=0,
        description="Number of DB records sharing this NAFDAC number."
    )


class SearchRequest(BaseModel):
    """Input for semantic product text search (used when NAFDAC number is unreadable)."""
    product_text: str = Field(
        ...,
        description="Any product-related text visible on the label.",
        example="kelloggs corn flakes hardboard pack",
    )
    n: int = Field(
        default=5, ge=1, le=20,
        description="Maximum number of results to return.",
    )


class SearchResult(BaseModel):
    """One ranked result from the semantic text search endpoint."""
    similarity_score: float
    metadata:         dict
    chunk_text:       str


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("/product", response_model=VerifyResponse)
async def verify_product(request: VerifyRequest):
    """
    Main product verification endpoint — called after every scan in the mobile app.

    Pipeline executed on each call:
      1. Retrieve DB record(s) by NAFDAC number  (exact metadata match)
      2. Run four-layer verification scoring
      3. Return structured verdict

    Returns HTTP 200 in ALL cases, including fakes and mismatches.
    The verdict is communicated in the response body, not via HTTP status codes.
    HTTP 5xx codes indicate infrastructure failures only.

    Called by: D1 Backend → D3 Mobile App scan flow
    """
    try:
        records = _retriever.retrieve_by_nafdac_no(request.nafdac_no)
        result  = compute_verification_score(
            nafdac_no           = request.nafdac_no,
            scanned_subcategory = request.scanned_subcategory,
            db_records          = records,
        )

        return VerifyResponse(
            nafdac_no        = request.nafdac_no,
            duplicate_count  = len(result.get("all_records", [])),
            **{k: v for k, v in result.items() if k not in ("all_records",)},
        )

    except Exception as exc:
        raise HTTPException(
            status_code = 500,
            detail      = f"Verification pipeline failed: {exc}",
        )


@router.get("/lookup/{nafdac_no}", response_model=list[dict])
async def lookup_nafdac(nafdac_no: str):
    """
    Direct NAFDAC number lookup — returns the raw database record(s).

    Used by the D5 Regulatory Dashboard to display full product details
    when an enforcement officer enters a NAFDAC number manually.

    Returns HTTP 404 if the number is not found or cannot be normalised.

    Called by: D5 Dashboard, NAFDAC enforcement portal
    """
    records = _retriever.retrieve_by_nafdac_no(nafdac_no)

    if not records:
        raise HTTPException(
            status_code = 404,
            detail      = (
                f"NAFDAC number '{nafdac_no.strip().upper()}' not found "
                f"in the product database."
            ),
        )
    return records


@router.post("/search", response_model=list[SearchResult])
async def search_products(request: SearchRequest):
    """
    Semantic product text search — fallback when NAFDAC number is unreadable.

    Use when OCR cannot extract a clean NAFDAC number but brand name, product
    name, or packaging description text is visible.  Returns ranked candidates.

    Called by: D3 Mobile App (fallback scan flow), D5 Dashboard (product search)
    """
    results = _retriever.retrieve_by_product_text(
        product_text = request.product_text,
        n            = request.n,
    )
    return [
        SearchResult(
            similarity_score = r["similarity_score"],
            metadata         = r["metadata"],
            chunk_text       = r["text"],
        )
        for r in results
    ]


@router.get("/category/{subcategory}", response_model=list[dict])
async def get_products_by_category(
    subcategory: str,
    n: int = Query(default=20, ge=1, le=100, description="Max results"),
):
    """
    Return all registered products in a given subcategory.

    Valid subcategory values:
      'Cereals and Cereal Products'
      'Cosmetics'
      'Fats and oils, and Fat Emulsions'
      'Salts, Spices, Soups, Sauces, Salads and Seasoning'
      'Beverages'
      'Sweeteners'

    Called by: D5 Dashboard (category browse), A4 Fusion Engine
    """
    records = _retriever.retrieve_by_subcategory(subcategory=subcategory, n=n)

    if not records:
        raise HTTPException(
            status_code = 404,
            detail      = f"No products found for subcategory '{subcategory}'.",
        )
    return records


@router.get("/health")
async def health_check():
    """
    Health check endpoint for D7 DevOps monitoring.

    Returns HTTP 200 with collection stats when healthy,
    HTTP 503 when ChromaDB is inaccessible.

    Called by: D7 DevOps uptime monitoring, deployment health checks
    """
    try:
        count = _retriever.store.count()
        return {
            "status"          : "healthy",
            "collection"      : "nafdac_food_products",
            "documents_indexed": count,
            "message"         : (
                f"RAG system operational with {count} product(s) indexed."
            ),
        }
    except Exception as exc:
        raise HTTPException(
            status_code = 503,
            detail      = f"RAG system unhealthy: {exc}",
        )