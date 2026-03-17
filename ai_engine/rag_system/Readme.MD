# SabiLens — NAFDAC Food Product RAG System

**Module A3 · Greenbook RAG & Regulatory Lead**

A production-ready Retrieval-Augmented Generation (RAG) system that validates
NAFDAC-registered food and consumer product registrations. Given a NAFDAC
number and product type scanned from a product label, the system determines
whether the product is authentic, expired, or a likely counterfeit.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Project Structure](#project-structure)
6. [Running the System](#running-the-system)
   - [Step 1 — Ingest the Database](#step-1--ingest-the-database)
   - [Step 2 — Start the API Server](#step-2--start-the-api-server)
7. [Using the API](#using-the-api)
   - [Verify a Product](#1-verify-a-product-main-endpoint)
   - [Lookup by NAFDAC Number](#2-lookup-by-nafdac-number)
   - [Semantic Search](#3-semantic-product-search)
   - [Browse by Category](#4-browse-by-category)
   - [Health Check](#5-health-check)
8. [Running the Tests](#running-the-tests)
9. [Environment Variables](#environment-variables)
10. [Demo Scenarios](#demo-scenarios)
11. [Troubleshooting](#troubleshooting)

---

## Project Overview

SabiLens A3 scans a product label, extracts the NAFDAC registration number and
product type, then runs a four-layer verification check:

| Layer | Check | Fail Score |
|-------|-------|-----------|
| 1 | NAFDAC number exists in the database | `0.0` — NOT FOUND |
| 2 | Registration has not expired | `0.1` — EXPIRED |
| 3 | Scanned product type matches registered category | `0.2` — MISMATCH |
| 4 | All checks pass | `1.0` — VERIFIED |

A **category mismatch** (Layer 3) is the strongest counterfeit signal — it means
a valid NAFDAC number has been stamped on a completely different type of product.

**Dataset:** 15 NAFDAC-registered Nigerian food and consumer products across
6 subcategories: Cereals, Cosmetics, Fats & Oils, Spices & Seasoning, Beverages,
and Sweeteners.

---

## System Architecture

```
nafdac_database.xlsx
        │
        ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  excel_loader   │────▶│  chunk_builder   │────▶│    embedder     │
│  (clean + load) │     │ (text + metadata)│     │ (MiniLM-L6-v2)  │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                           │ vectors
                                                           ▼
                                                  ┌─────────────────┐
                                                  │   chroma_db/    │
                                                  │  (ChromaDB on   │
                                                  │    disk)        │
                                                  └────────┬────────┘
                                                           │
                                                           ▼
                                          ┌────────────────────────────┐
                                          │         retriever          │
                                          │  ① by NAFDAC number        │
                                          │  ② by product text (semantic)│
                                          │  ③ by subcategory          │
                                          └────────────┬───────────────┘
                                                       │
                                                       ▼
                                          ┌────────────────────────────┐
                                          │     regulatory_scorer      │
                                          │  (4-layer verdict + score) │
                                          └────────────┬───────────────┘
                                                       │
                                                       ▼
                                          ┌────────────────────────────┐
                                          │       FastAPI              │
                                          │   POST /verify/product     │
                                          └────────────────────────────┘
```

---

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.10 or higher | Check with `python3 --version` |
| pip | Latest | Check with `pip --version` |

> **No GPU required.** All embedding and retrieval runs on CPU.
> The first ingestion downloads the `all-MiniLM-L6-v2` model (~80 MB) from
> HuggingFace. An internet connection is needed for that one-time download.

---


## Project Structure

```
sabilens_rag/
│
├── data/
│   ├── raw/
│   │   └── nafdac_database.xlsx          ← Source database (15 products)
│   └── processed/                        ← Auto-created on first ingest
│       ├── nafdac_chunks.json            ← Human-readable chunk dump
│       └── ingestion_report.json         ← Ingest stats and warnings
│
├── ingestion/
│   ├── schema.py                         ← NAFDACEntry and ProductChunk dataclasses
│   ├── excel_loader.py                   ← Load and clean the Excel database
│   └── chunk_builder.py                  ← Convert entries to embeddable text chunks
│
├── vectorstore/
│   ├── embedder.py                       ← SentenceTransformer wrapper
│   └── chroma_client.py                  ← ChromaDB read/write interface
│
├── retrieval/
│   ├── retriever.py                      ← 3 retrieval strategies (NAFDAC/semantic/category)
│   ├── subcategory_alignment.py          ← Category mismatch detection
│   └── regulatory_scorer.py             ← 4-layer verification scoring
│
├── api/
│   ├── app.py                            ← FastAPI application factory
│   └── routes.py                         ← All HTTP endpoints
│
├── utils/
│   └── nafdac_normalizer.py              ← NAFDAC number cleaning utility
│
├── config/
│   └── settings.py                       ← All environment-based configuration
│
├── tests/                                ← Full test suite (7 files)
│   ├── test_nafdac_normalizer.py
│   ├── test_excel_loader.py
│   ├── test_chunk_builder.py
│   ├── test_subcategory_alignment.py
│   ├── test_regulatory_scorer.py
│   ├── test_embedder.py
│   └── test_chroma_client.py
│
├── chroma_db/                            ← Auto-created on first ingest (vector store)
│
├── main.py                               ← Entry point (ingest + serve)
└── requirements.txt
```

---

## Running the System

There are **two steps** to run the system. You only need to run Step 1 once
(or whenever the database file is updated).

---

### Step 1 — Ingest the Database

This step reads `nafdac_database.xlsx`, cleans the data, generates embedding
vectors for all 15 products, and stores everything in ChromaDB on disk.

```bash
python main.py --mode ingest
```

**Expected output:**

```
======================================================================
  SabiLens — NAFDAC Food Product RAG Ingestion Pipeline
  Started: 2026-03-03 12:00:00
======================================================================

[Step 1/5] Loading NAFDAC database Excel file…
[Loader] Reading: ./data/raw/nafdac_database.xlsx
[Loader] Read 15 rows across 9 columns.
[Loader] Built 15 entries.
[Loader] Subcategories: {'Cereals and Cereal Products': 4, 'Cosmetics': 5, ...}

[Step 2/5] Building product chunks…
[ChunkBuilder]Built 15 unique chunks (skipped 0 duplicate(s)).

[Step 3/5] Saving audit JSON…
[ChunkBuilder] Saved 15 chunks to ./data/processed/nafdac_chunks.json

[Step 4/5] Generating embedding vectors…
[Embedder] Loading model: sentence-transformers/all-MiniLM-L6-v2
[Embedder] Model ready — embedding dimension: 384
Batches: 100%|████████████████| 1/1 [00:02<00:00]

[Step 5/5] Upserting into ChromaDB…
[ChromaStore] Collection 'nafdac_food_products' ready.
[ChromaStore] Upsert complete. Collection now contains 15 document(s).

======================================================================
  INGESTION COMPLETE
  Products loaded   : 15
  Chunks built      : 15
  Duplicates skipped: 0
  DB total          : 15 document(s)
  Warnings          : 0
======================================================================
```
---

### Step 2 — Start the API Server

```bash
python main.py --mode serve
```

Or alternatively with uvicorn directly (for development with auto-reload):

```bash
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```

**Expected output:**

```
======================================================================
  SabiLens — NAFDAC Verification API
  URL:  http://0.0.0.0:8000
  Docs: http://localhost:8000/docs
======================================================================

INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

The API is now running. Open your browser at:

- **Interactive docs (Swagger UI):** http://localhost:8000/docs
- **Alternative docs (ReDoc):** http://localhost:8000/redoc

---

## Using the API

All endpoints are prefixed with `/verify`. You can test them using:
- The **Swagger UI** at http://localhost:8000/docs (click any endpoint → "Try it out")
- `curl` commands in a terminal
- Any API client like Postman or Insomnia

---

### 1. Verify a Product *(main endpoint)*

`POST /verify/product`

Runs the full four-layer verification check. This is the primary endpoint
called by the D3 mobile app after every label scan.

**Request body:**
```json
{
  "nafdac_no": "A8-4114",
  "scanned_subcategory": "corn flakes"
}
```

**Example — Authentic product:**
```bash
curl -X POST http://localhost:8000/verify/product \
  -H "Content-Type: application/json" \
  -d '{"nafdac_no": "A8-4114", "scanned_subcategory": "corn flakes"}'
```

**Response:**
```json
{
  "nafdac_no": "A8-4114",
  "verified": true,
  "verification_score": 1.0,
  "status_code": "VERIFIED",
  "severity": "NONE",
  "summary": "'KELLOGG'S CORN FLAKES' is a valid, registered NAFDAC product.",
  "detail": "Verification passed. 'KELLOGG'S CORN FLAKES' by 'KELLOGG TOLARAM NIGERIA LIMTED' is a registered Cereals and Cereal Products product (NAFDAC No: A8-4114).",
  "matched_record": { "product_name": "KELLOGG'S CORN FLAKES", ... }
}
```

**Example — Category mismatch (counterfeit signal):**
```bash
curl -X POST http://localhost:8000/verify/product \
  -H "Content-Type: application/json" \
  -d '{"nafdac_no": "A8-4114", "scanned_subcategory": "cosmetics"}'
```

**Response:**
```json
{
  "verified": false,
  "verification_score": 0.2,
  "status_code": "SUBCATEGORY_MISMATCH",
  "severity": "CRITICAL",
  "summary": "NAFDAC 'A8-4114' registered for 'Cereals and Cereal Products', not 'cosmetics'.",
  "detail": "CRITICAL: NAFDAC number 'A8-4114' belongs to 'KELLOGG'S CORN FLAKES' (Cereals). However, the scanned product appears to be 'Cosmetics'. Do not buy."
}
```

**Example — Unknown NAFDAC number:**
```bash
curl -X POST http://localhost:8000/verify/product \
  -H "Content-Type: application/json" \
  -d '{"nafdac_no": "FAKE-999", "scanned_subcategory": "cereal"}'
```

**Response:**
```json
{
  "verified": false,
  "verification_score": 0.0,
  "status_code": "NOT_FOUND",
  "severity": "CRITICAL"
}
```

---

### 2. Lookup by NAFDAC Number

`GET /verify/lookup/{nafdac_no}`

Returns the raw database record for a given NAFDAC number.
Returns HTTP 404 if not found.

```bash
curl http://localhost:8000/verify/lookup/A8-4114
```

```bash
curl http://localhost:8000/verify/lookup/01-0132
```

---

### 3. Semantic Product Search

`POST /verify/search`

Search by any product-related text when the NAFDAC number is unreadable.
Returns ranked candidates by semantic similarity.

```bash
curl -X POST http://localhost:8000/verify/search \
  -H "Content-Type: application/json" \
  -d '{"product_text": "kelloggs cereal nigeria hardboard", "n": 3}'
```

```bash
curl -X POST http://localhost:8000/verify/search \
  -H "Content-Type: application/json" \
  -d '{"product_text": "unilever vaseline petroleum jelly", "n": 3}'
```

---

### 4. Browse by Category

`GET /verify/category/{subcategory}`

Returns all products in a given subcategory. Valid values:

| Subcategory | Products in DB |
|-------------|---------------|
| `Cereals and Cereal Products` | Kellogg's Corn Flakes, Coco Pops, Golden Penny Pasta, Indomie Noodles |
| `Cosmetics` | Closeup, Pepsodent, Rexona, Vaseline (×2) |
| `Fats and oils, and Fat Emulsions` | Golden Terra Soya Oil, Sedoso Vegetable Oil |
| `Salts, Spices, Soups, Sauces, Salads and Seasoning` | Peppe Terra Paste, Terra Seasoning Cube |
| `Beverages` | Lipton Yellow Label Tea |
| `Sweeteners` | Dangote Sugar |

```bash
# URL-encode the subcategory name (spaces → %20)
curl "http://localhost:8000/verify/category/Cosmetics"

curl "http://localhost:8000/verify/category/Cereals%20and%20Cereal%20Products"

curl "http://localhost:8000/verify/category/Beverages"
```

---

### 5. Health Check

`GET /verify/health`

Returns system status and the number of indexed products.

```bash
curl http://localhost:8000/verify/health
```

**Response:**
```json
{
  "status": "healthy",
  "collection": "nafdac_food_products",
  "documents_indexed": 15,
  "message": "RAG system operational with 15 product(s) indexed."
}
```

---

## Running the Tests

The test suite covers all modules without requiring ChromaDB to be running
or the API server to be started.

### Install pytest (if not already installed):

```bash
pip install pytest
```

### Run all tests:

```bash
pytest tests/ -v
```

### Run individual test files:

```bash
# NAFDAC number normalisation (no external dependencies)
pytest tests/test_nafdac_normalizer.py -v

# Excel loader against the real database file
pytest tests/test_excel_loader.py -v

# Chunk construction logic
pytest tests/test_chunk_builder.py -v

# Category mismatch detection
pytest tests/test_subcategory_alignment.py -v

# Regulatory scoring (all 4 layers)
pytest tests/test_regulatory_scorer.py -v

# Embedding model (requires sentence-transformers installed)
pytest tests/test_embedder.py -v

# ChromaDB client (uses temp directories — no persistent state)
pytest tests/test_chroma_client.py -v
```

### Expected result:

```
tests/test_nafdac_normalizer.py      28 passed
tests/test_excel_loader.py           30 passed
tests/test_chunk_builder.py          25 passed
tests/test_subcategory_alignment.py  30 passed
tests/test_regulatory_scorer.py      20 passed
tests/test_embedder.py               14 passed
tests/test_chroma_client.py          20 passed
```

> `test_embedder.py` and `test_chroma_client.py` are automatically skipped
> if `sentence-transformers` or `chromadb` are not installed respectively.

---

## Environment Variables

All settings have sensible defaults and work out of the box.
Override any of them by setting environment variables before running:

```bash
export DATABASE_PATH=./data/raw/nafdac_database.xlsx
export CHROMA_PERSIST_DIR=./chroma_db
export CHROMA_COLLECTION_NAME=nafdac_food_products
export EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
export SIMILARITY_THRESHOLD=0.68
export REFERENCE_DATE=2026-03-03
export API_HOST=0.0.0.0
export API_PORT=8000
```

Or create a `.env` file in the project root:

```env
DATABASE_PATH=./data/raw/nafdac_database.xlsx
CHROMA_PERSIST_DIR=./chroma_db
API_PORT=8000
REFERENCE_DATE=2026-03-03
```

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_PATH` | `./data/raw/nafdac_database.xlsx` | Path to the Excel database |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | Directory where ChromaDB stores vectors on disk |
| `CHROMA_COLLECTION_NAME` | `nafdac_food_products` | ChromaDB collection name |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | HuggingFace model for embeddings |
| `SIMILARITY_THRESHOLD` | `0.68` | Minimum cosine similarity for semantic search results |
| `REFERENCE_DATE` | `2026-03-03` | Date used when evaluating product expiry |
| `API_HOST` | `0.0.0.0` | Server host |
| `API_PORT` | `8000` | Server port |

---

## Demo Scenarios

These are the key scenarios to demonstrate during a product demo:

### Scenario 1 — Authentic Product 
A Kellogg's Corn Flakes box with a correct, valid NAFDAC label.
```bash
curl -X POST http://localhost:8000/verify/product \
  -H "Content-Type: application/json" \
  -d '{"nafdac_no": "A8-4114", "scanned_subcategory": "corn flakes"}'
# Expected: score=1.0, VERIFIED
```

### Scenario 2 — Counterfeit (Category Mismatch) 
A fake cosmetic product reusing Kellogg's NAFDAC number.
```bash
curl -X POST http://localhost:8000/verify/product \
  -H "Content-Type: application/json" \
  -d '{"nafdac_no": "A8-4114", "scanned_subcategory": "cosmetics"}'
# Expected: score=0.2, SUBCATEGORY_MISMATCH, severity=CRITICAL
```

### Scenario 3 — Fake NAFDAC Number 
A product with a completely made-up NAFDAC number.
```bash
curl -X POST http://localhost:8000/verify/product \
  -H "Content-Type: application/json" \
  -d '{"nafdac_no": "FAKE-999", "scanned_subcategory": "cereal"}'
# Expected: score=0.0, NOT_FOUND, severity=CRITICAL
```

### Scenario 4 — Near-Expiry Warning 
Lipton Yellow Label Tea (expires 2026-03-28, just 25 days away).
```bash
curl -X POST http://localhost:8000/verify/product \
  -H "Content-Type: application/json" \
  -d '{"nafdac_no": "01-0132", "scanned_subcategory": "tea"}'
# Expected: score=0.85, VERIFIED_NEAR_EXPIRY, severity=WARNING
```

### Scenario 5 — Readable NAFDAC but Unreadable Product Name
When OCR can't read the NAFDAC number, fall back to semantic search.
```bash
curl -X POST http://localhost:8000/verify/search \
  -H "Content-Type: application/json" \
  -d '{"product_text": "indomie chicken flavour noodles dufil nigeria", "n": 3}'
# Expected: INDOMIE INSTANT NOODLES as top result
```

---

