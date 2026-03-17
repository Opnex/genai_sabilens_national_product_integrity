# SabiLens A3 — RAG System Integration Guide

> **Who this is for:** Developers on modules **A4 (Fusion Engine)**, **D1 (Backend Lead)**,
> **D3 (Mobile App)**, **D5 (Dashboard)**, and **D6 (N-ATLAS Voice)** who need to call
> the A3 RAG API from their own code.

---

## Table of Contents

1. [What A3 Does](#what-a3-does)
2. [Quick Setup](#quick-setup)
3. [Base URL & Interactive Docs](#base-url--interactive-docs)
4. [API Reference](#api-reference)
   - [POST /verify/product](#post-verifyproduct--main-endpoint)
   - [GET /verify/lookup/{nafdac\_no}](#get-verifylookupnafdac_no)
   - [POST /verify/search](#post-verifysearch)
   - [GET /verify/category/{subcategory}](#get-verifycategorysubcategory)
   - [GET /verify/health](#get-verifyhealth)
5. [Response Field Reference](#response-field-reference)
6. [Score & Status Code Reference](#score--status-code-reference)
7. [Integration Examples by Module](#integration-examples-by-module)
   - [A4 Fusion Engine](#a4-fusion-engine)
   - [D1 Backend Lead](#d1-backend-lead)
   - [D3 Mobile App](#d3-mobile-app)
   - [D5 Dashboard](#d5-dashboard)
   - [D6 N-ATLAS Voice](#d6-n-atlas-voice)
8. [Testing the RAG System Locally](#testing-the-rag-system-locally)
9. [Error Handling](#error-handling)
10. [Environment & Configuration](#environment--configuration)

---

## What A3 Does

The A3 module receives a **NAFDAC registration number** and a **product category**
(both extracted from a product label by the A1/A2 scan pipeline), then runs a
four-layer verification check against the NAFDAC database:

| Layer | Check | Result if failed |
|-------|-------|-----------------|
| 1 | NAFDAC number exists in the database | `NOT_FOUND` · score `0.0` |
| 2 | Registration has not expired | `EXPIRED` · score `0.1` |
| 3 | Scanned product type matches registration category | `SUBCATEGORY_MISMATCH` · score `0.2` |
| 4 | All checks pass | `VERIFIED` · score `1.0` |

It returns a structured JSON verdict that every downstream module uses differently.

---

### 4. Start the API server

```bash
python main.py --mode serve
```

The server runs at **`http://localhost:8000`** by default. Keep this terminal open.

### 5. Verify it's working

```bash
curl http://localhost:8000/verify/health
```

Expected:
```json
{
  "status": "healthy",
  "documents_indexed": 15,
  "message": "RAG system operational with 15 product(s) indexed."
}
```

---

## Base URL & Interactive Docs

| Environment | Base URL |
|-------------|----------|
| Local dev   | `http://localhost:8000` |
| Staging     | *(set by D7 DevOps)* |
| Production  | *(set by D7 DevOps)* |

**Interactive API explorer (Swagger UI):**
Open `http://localhost:8000/docs` in your browser.
Every endpoint is testable there without writing any code.

---

## API Reference

---

### `POST /verify/product` — Main Endpoint

The primary endpoint. Call this after every product scan with the NAFDAC number
and the scanned product category. Returns the full verification verdict.

**Request body:**

```json
{
  "nafdac_no": "A8-4114",
  "scanned_subcategory": "corn flakes"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `nafdac_no` | string | Raw NAFDAC number from OCR. Leading spaces, non-breaking spaces, and dashes with spaces are cleaned automatically. |
| `scanned_subcategory` | string | Product type from A1/A2 classifier. Raw text is fine — aliases like `"noodles"`, `"toothpaste"`, `"cooking oil"` are resolved automatically. |

**Response — Verified product:**

```json
{
  "nafdac_no": "A8-4114",
  "verified": true,
  "verification_score": 1.0,
  "status_code": "VERIFIED",
  "severity": "NONE",
  "summary": "'KELLOGG'S CORN FLAKES' is a valid, registered NAFDAC product.",
  "detail": "Verification passed. 'KELLOGG'S CORN FLAKES' by 'KELLOGG TOLARAM NIGERIA LIMTED' is a registered Cereals and Cereal Products product (NAFDAC No: A8-4114).",
  "expiry_check": {
    "is_valid": true,
    "is_near_expiry": false,
    "expiry_date": "2029-07-30",
    "days_remaining": 1244,
    "severity": "NONE",
    "message": "Registration valid until 2029-07-30 (1244 day(s) remaining)."
  },
  "alignment": {
    "is_match": true,
    "scanned_norm": "Cereals and Cereal Products",
    "registered_norm": "Cereals and Cereal Products",
    "mismatch_type": null,
    "severity": "NONE",
    "message": "Product category confirmed: 'Cereals and Cereal Products'."
  },
  "matched_record": {
    "nafdac_no": "A8-4114",
    "nafdac_no_clean": "A8-4114",
    "product_name": "KELLOGG'S CORN FLAKES",
    "subcategory": "Cereals and Cereal Products",
    "presentation": "300G HARDBOARD PACK",
    "applicant_name": "KELLOGG TOLARAM NIGERIA LIMTED",
    "manufacturer": "KT LFTZ ENTERPRISE",
    "country": "Nigeria",
    "expiry_date_iso": "2029-07-30"
  },
  "duplicate_count": 1
}
```

**Response — Category mismatch (counterfeit signal):**

```json
{
  "nafdac_no": "A8-4114",
  "verified": false,
  "verification_score": 0.2,
  "status_code": "SUBCATEGORY_MISMATCH",
  "severity": "CRITICAL",
  "summary": "NAFDAC 'A8-4114' registered for 'Cereals and Cereal Products', not 'cosmetics'.",
  "detail": "CRITICAL: NAFDAC number 'A8-4114' belongs to 'KELLOGG'S CORN FLAKES' (Cereals and Cereal Products). However, the scanned product appears to be 'Cosmetics'. Do not buy.",
  "alignment": {
    "is_match": false,
    "scanned_norm": "Cosmetics",
    "registered_norm": "Cereals and Cereal Products",
    "mismatch_type": "SUBCATEGORY_MISMATCH",
    "severity": "CRITICAL",
    "message": "CRITICAL MISMATCH — NAFDAC number is registered under 'Cereals and Cereal Products' but the scanned product appears to be 'Cosmetics'. Do not purchase this product."
  }
}
```

**Response — Not found:**

```json
{
  "nafdac_no": "FAKE-999",
  "verified": false,
  "verification_score": 0.0,
  "status_code": "NOT_FOUND",
  "severity": "CRITICAL",
  "summary": "NAFDAC number 'FAKE-999' not found in the database.",
  "detail": "The NAFDAC number 'FAKE-999' does not exist in the registered product database. This product has no valid NAFDAC registration. Do not purchase this product.",
  "matched_record": null
}
```

> **HTTP status code is always 200** — even for fakes and mismatches.
> The verdict is communicated through `verified`, `status_code`, and `severity`.
> HTTP 5xx means an infrastructure error in the RAG system itself.

---

### `GET /verify/lookup/{nafdac_no}`

Fetch the raw database record(s) for a given NAFDAC number.
Returns HTTP 404 if the number does not exist.

```
GET /verify/lookup/A8-4114
GET /verify/lookup/01-0132
GET /verify/lookup/02-0385
```

**Response:**
```json
[
  {
    "nafdac_no": "A8-4114",
    "nafdac_no_clean": "A8-4114",
    "product_name": "KELLOGG'S CORN FLAKES",
    "subcategory": "Cereals and Cereal Products",
    "presentation": "300G HARDBOARD PACK",
    "applicant_name": "KELLOGG TOLARAM NIGERIA LIMTED",
    "manufacturer": "KT LFTZ ENTERPRISE",
    "country": "Nigeria",
    "expiry_date_iso": "2029-07-30"
  }
]
```

Returns a list because a single NAFDAC number can have multiple registered
variants (e.g. different sizes). Typically only one record.

---

### `POST /verify/search`

Semantic fallback: search by any product-related text when the NAFDAC number
is damaged or unreadable. Returns candidates ranked by cosine similarity.

**Request body:**
```json
{
  "product_text": "kelloggs corn flakes hardboard pack nigeria",
  "n": 5
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `product_text` | string | — | Any text visible on the label |
| `n` | integer | `5` | Max results to return (1–20) |

**Response:**
```json
[
  {
    "similarity_score": 0.9124,
    "metadata": {
      "product_name": "KELLOGG'S CORN FLAKES",
      "nafdac_no_clean": "A8-4114",
      "subcategory": "Cereals and Cereal Products",
      "expiry_date_iso": "2029-07-30"
    },
    "chunk_text": "Product: KELLOGG'S CORN FLAKES. NAFDAC No: A8-4114. ..."
  }
]
```

Results below the `SIMILARITY_THRESHOLD` (default `0.68`) are excluded automatically.
An empty array means no confident match was found.

---

### `GET /verify/category/{subcategory}`

Returns all registered products in a given subcategory. Optional query
parameter `?n=20` controls the maximum number of results (1–100).

**Valid subcategory values:**

| Subcategory | Products |
|-------------|---------|
| `Cereals and Cereal Products` | Kellogg's Corn Flakes, Coco Pops, Golden Penny Pasta, Indomie Noodles |
| `Cosmetics` | Closeup, Pepsodent, Rexona, Vaseline Blueseal, Vaseline Eventone |
| `Fats and oils, and Fat Emulsions` | Golden Terra Soya Oil, Sedoso Vegetable Oil |
| `Salts, Spices, Soups, Sauces, Salads and Seasoning` | Peppe Terra Paste, Terra Seasoning Cube |
| `Beverages` | Lipton Yellow Label Tea |
| `Sweeteners` | Dangote Sugar |

```
GET /verify/category/Cosmetics
GET /verify/category/Beverages
GET /verify/category/Cereals%20and%20Cereal%20Products?n=10
```

Returns HTTP 404 if no products exist for that category.

---

### `GET /verify/health`

Health check for uptime monitoring and deployment verification.

```
GET /verify/health
```

| HTTP status | Meaning |
|-------------|---------|
| `200` | System healthy, ChromaDB reachable, documents indexed |
| `503` | ChromaDB unreachable or collection empty |

---

## Response Field Reference

Every `POST /verify/product` response contains these fields:

| Field | Type | Description |
|-------|------|-------------|
| `nafdac_no` | string | The raw NAFDAC number you sent in the request |
| `verified` | boolean | `true` only if all 4 layers passed |
| `verification_score` | float (0.0–1.0) | Confidence weight for A4 Fusion Engine |
| `status_code` | string | Machine-readable verdict (see table below) |
| `severity` | string | `NONE` · `WARNING` · `HIGH` · `CRITICAL` |
| `summary` | string | One-line verdict for UI headlines |
| `detail` | string | Full explanation — use for N-ATLAS voice translation |
| `expiry_check` | object \| null | Expiry layer result (null if NOT_FOUND) |
| `expiry_check.is_valid` | boolean | `false` if registration has expired |
| `expiry_check.is_near_expiry` | boolean | `true` if expiring within 60 days |
| `expiry_check.days_remaining` | integer \| null | Days until (or since) expiry |
| `alignment` | object \| null | Category alignment result (null if NOT_FOUND or EXPIRED) |
| `alignment.is_match` | boolean | `false` = counterfeit signal |
| `alignment.scanned_norm` | string | Normalised version of what you sent |
| `alignment.registered_norm` | string | What the NAFDAC number is actually registered for |
| `alignment.message` | string | Human-readable alignment explanation |
| `matched_record` | object \| null | Full product metadata from the database |
| `duplicate_count` | integer | Number of DB records sharing this NAFDAC number |

---

## Score & Status Code Reference

| `status_code` | `verification_score` | `severity` | `verified` | Meaning |
|---------------|---------------------|------------|------------|---------|
| `VERIFIED` | `1.0` | `NONE` | `true` | Authentic product, all checks passed |
| `VERIFIED_NEAR_EXPIRY` | `0.85` | `WARNING` | `true` | Valid but expires within 60 days |
| `SUBCATEGORY_MISMATCH` | `0.2` | `CRITICAL` | `false` | Valid NAFDAC on wrong product type — strong counterfeit signal |
| `EXPIRED` | `0.1` | `HIGH` | `false` | Registration has lapsed — product no longer authorised |
| `NOT_FOUND` | `0.0` | `CRITICAL` | `false` | NAFDAC number does not exist in the database |

---

## Integration Examples by Module

---

### A4 Fusion Engine

You receive the `verification_score` and `severity` as one signal to fuse
with visual, OCR, and other signals.

```python
import requests

def get_regulatory_signal(nafdac_no: str, scanned_category: str) -> dict:
    """
    Call A3 and return the regulatory signal for fusion.
    
    Returns dict with:
      verification_score : float (0.0–1.0) — weight in the fusion formula
      severity           : str             — escalation trigger
      status_code        : str             — for audit logging
      detail             : str             — for N-ATLAS translation
    """
    response = requests.post(
        "http://localhost:8000/verify/product",
        json={
            "nafdac_no": nafdac_no,
            "scanned_subcategory": scanned_category,
        },
        timeout=5,
    )
    response.raise_for_status()
    data = response.json()

    return {
        "verification_score" : data["verification_score"],
        "severity"           : data["severity"],
        "status_code"        : data["status_code"],
        "detail"             : data["detail"],
        "matched_record"     : data.get("matched_record"),
    }


# Usage in your fusion formula:
signal = get_regulatory_signal("A8-4114", "corn flakes")

if signal["severity"] == "CRITICAL":
    # Override fusion — flag as high-risk immediately
    final_verdict = "SUSPICIOUS"
else:
    # Combine with other signals
    regulatory_weight = 0.4
    score = signal["verification_score"] * regulatory_weight  # + other signals
```

**Key decision logic for A4:**

```python
severity = data["severity"]

if severity == "CRITICAL":
    # status is either NOT_FOUND or SUBCATEGORY_MISMATCH
    # Strong fake signal — flag the product regardless of other signals
    pass

elif severity == "HIGH":
    # EXPIRED registration — suspicious but may not be counterfeit
    pass

elif severity == "WARNING":
    # VERIFIED_NEAR_EXPIRY — valid today, flag for follow-up
    pass

elif severity == "NONE":
    # VERIFIED — clean pass, weight regulatory score as positive signal
    pass
```

---

### D1 Backend Lead

Wire the A3 call into the main scan processing pipeline:

```python
import requests
from typing import Optional

A3_BASE_URL = "http://localhost:8000"   # swap for staging/prod URL

def verify_nafdac(nafdac_no: str, scanned_subcategory: str) -> dict:
    """Call A3 verification. Returns full response dict or raises on failure."""
    resp = requests.post(
        f"{A3_BASE_URL}/verify/product",
        json={
            "nafdac_no": nafdac_no,
            "scanned_subcategory": scanned_subcategory,
        },
        timeout=5,
    )
    resp.raise_for_status()
    return resp.json()


def lookup_product(nafdac_no: str) -> Optional[list]:
    """Fetch raw product record(s). Returns None if not found."""
    resp = requests.get(f"{A3_BASE_URL}/verify/lookup/{nafdac_no}", timeout=5)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


def check_a3_health() -> bool:
    """Returns True if the A3 service is up and has products indexed."""
    try:
        resp = requests.get(f"{A3_BASE_URL}/verify/health", timeout=3)
        return resp.status_code == 200
    except requests.RequestException:
        return False
```

---

### D3 Mobile App

Call after a successful label scan. Use `verified`, `severity`, and `summary`
for the UI state — and `detail` for the full explanation screen.

**JavaScript / React Native (fetch):**

```javascript
const A3_BASE_URL = "http://localhost:8000";  // replace with real URL

async function verifyScan(nafdacNo, scannedCategory) {
  const response = await fetch(`${A3_BASE_URL}/verify/product`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      nafdac_no: nafdacNo,
      scanned_subcategory: scannedCategory,
    }),
  });

  if (!response.ok) {
    throw new Error(`A3 API error: ${response.status}`);
  }

  const data = await response.json();

  // Map to your UI state
  return {
    isVerified   : data.verified,
    score        : data.verification_score,
    severity     : data.severity,       // "NONE" | "WARNING" | "HIGH" | "CRITICAL"
    headline     : data.summary,        // one-liner for the scan result card
    explanation  : data.detail,         // full text for the detail screen
    productName  : data.matched_record?.product_name ?? "Unknown",
    expiryDate   : data.matched_record?.expiry_date_iso ?? null,
    statusCode   : data.status_code,
  };
}

// Suggested UI colour mapping:
const SEVERITY_COLOUR = {
  NONE     : "#4CAF50",   // green
  WARNING  : "#FF9800",   // amber
  HIGH     : "#F44336",   // red
  CRITICAL : "#B71C1C",   // dark red
};

// Usage:
const result = await verifyScan("A8-4114", "corn flakes");
setCardColour(SEVERITY_COLOUR[result.severity]);
setHeadline(result.headline);
```

---

### D5 Dashboard

Use the lookup and category endpoints to power the product browser and
enforcement search panels.

```javascript
// Lookup a product by NAFDAC number (enforcement officer search)
async function lookupProduct(nafdacNo) {
  const response = await fetch(
    `http://localhost:8000/verify/lookup/${encodeURIComponent(nafdacNo)}`
  );
  if (response.status === 404) return null;
  return await response.json();   // array of product records
}

// Browse all products in a category (dashboard category panel)
async function getProductsByCategory(subcategory, maxResults = 20) {
  const url = `http://localhost:8000/verify/category/${encodeURIComponent(subcategory)}?n=${maxResults}`;
  const response = await fetch(url);
  if (response.status === 404) return [];
  return await response.json();
}

// Examples:
const cosmetics = await getProductsByCategory("Cosmetics");
const cereals   = await getProductsByCategory("Cereals and Cereal Products");
const product   = await lookupProduct("A8-4114");
```

---

### D6 N-ATLAS Voice

The `detail` field in every response is a complete English sentence ready for
translation to Yoruba, Hausa, or Nigerian Pidgin.

```python
import requests

def get_verdict_for_translation(nafdac_no: str, scanned_category: str) -> dict:
    """
    Returns the text fields needed for N-ATLAS voice translation.
    """
    resp = requests.post(
        "http://localhost:8000/verify/product",
        json={
            "nafdac_no": nafdac_no,
            "scanned_subcategory": scanned_category,
        },
        timeout=5,
    )
    resp.raise_for_status()
    data = resp.json()

    return {
        # Pass 'detail' to your translation model
        "text_to_translate" : data["detail"],

        # Use 'severity' to choose the voice tone (calm / urgent)
        "severity"          : data["severity"],

        # Use 'verified' to choose the audio alert sound
        "play_alert"        : not data["verified"],
    }


# Example outputs for translation:

# VERIFIED:
# "Verification passed. 'KELLOGG'S CORN FLAKES' by 'KELLOGG TOLARAM
#  NIGERIA LIMTED' is a registered Cereals and Cereal Products product."

# SUBCATEGORY_MISMATCH:
# "CRITICAL: NAFDAC number 'A8-4114' belongs to 'KELLOGG'S CORN FLAKES'
#  (Cereals). However, the scanned product appears to be 'Cosmetics'.
#  This is a strong sign of a counterfeit product. Do not buy."

# NOT_FOUND:
# "The NAFDAC number 'FAKE-999' does not exist in the registered product
#  database. This product has no valid NAFDAC registration. Do not purchase
#  this product."
```

---

## Testing the RAG System Locally

### Option 1 — Interactive tester (no server needed)

```bash
# Run all 10 demo scenarios — shows pass/fail summary
python rag_query.py --demo

# Verify one product
python rag_query.py --nafdac "A8-4114" --category "corn flakes"

# Test a counterfeit scenario
python rag_query.py --nafdac "A8-4114" --category "cosmetics"

# Semantic search fallback
python rag_query.py --search "indomie chicken noodles"

# Interactive menu
python rag_query.py
```

### Option 2 — curl against the running server

```bash
# Authentic product
curl -X POST http://localhost:8000/verify/product \
  -H "Content-Type: application/json" \
  -d '{"nafdac_no": "A8-4114", "scanned_subcategory": "corn flakes"}'

# Counterfeit mismatch
curl -X POST http://localhost:8000/verify/product \
  -H "Content-Type: application/json" \
  -d '{"nafdac_no": "A8-4114", "scanned_subcategory": "cosmetics"}'

# Near-expiry warning (Lipton Tea expires 2026-03-28)
curl -X POST http://localhost:8000/verify/product \
  -H "Content-Type: application/json" \
  -d '{"nafdac_no": "01-0132", "scanned_subcategory": "tea"}'

# Fake NAFDAC number
curl -X POST http://localhost:8000/verify/product \
  -H "Content-Type: application/json" \
  -d '{"nafdac_no": "FAKE-9999", "scanned_subcategory": "cereal"}'

# Semantic search
curl -X POST http://localhost:8000/verify/search \
  -H "Content-Type: application/json" \
  -d '{"product_text": "vaseline petroleum jelly unilever", "n": 3}'
```

### Option 3 — Swagger UI

Open `http://localhost:8000/docs` in your browser and use the "Try it out" button
on any endpoint.

---

## Error Handling

| HTTP Status | When it happens | What to do |
|-------------|----------------|------------|
| `200` | Normal — all verdicts including fakes | Read `verified`, `status_code`, `severity` |
| `404` | `/lookup` or `/category` found nothing | Show "product not found" in UI |
| `500` | Internal error in the RAG pipeline | Log and retry; alert D7 DevOps |
| `503` | ChromaDB unreachable or not ingested | A3 is down — contact A3 team |

**Always check the `severity` field**, not just `verified`.  
A product can have `verified: true` but `severity: WARNING` (near-expiry case).

```python
# Recommended check order:
if data["severity"] == "CRITICAL":
    # Immediately flag — either NOT_FOUND or SUBCATEGORY_MISMATCH
    ...
elif data["severity"] in ("HIGH", "WARNING"):
    # Show caution — expired or near-expiry
    ...
elif data["verified"] is True:
    # Clean pass
    ...
```

---

## Environment & Configuration

The A3 team controls these. If you need a different port or the staging URL,
ask the A3 lead or check with D7 DevOps:

| Setting | Default | Description |
|---------|---------|-------------|
| API host | `0.0.0.0` | Bind address |
| API port | `8000` | Port the server listens on |
| Similarity threshold | `0.68` | Minimum cosine similarity for `/search` results |
| Embedding model | `all-MiniLM-L6-v2` | 384-dim sentence transformer |

> **For your integration:** the only thing you need is the base URL.
> Everything else is internal to A3.

---

