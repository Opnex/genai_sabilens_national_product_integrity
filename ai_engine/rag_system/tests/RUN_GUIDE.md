# SabiLens — Full System Run Guide

From zero to working FastAPI server with every test passing.

---

## Prerequisites

```bash
cd sabilens/          # ALWAYS work from here
export PYTHONPATH=$(pwd)
```

Install once:
```bash
pip install -r sabilens_rag/requirements.txt   # fastapi, chromadb, sentence-transformers, pandas, uvicorn
pip install -r ai_engine/requirements.txt      # llama-index-core
```

---

## Step 1 — Ingest the NAFDAC database

Run from inside `sabilens_rag/` because `main.py` uses relative paths for the data files:

```bash
cd sabilens_rag/
python main.py --mode ingest
```

Expected output:
```
======================================================================
  SabiLens — NAFDAC Food Product RAG Ingestion Pipeline
  Started: 2026-03-11 10:00:00
======================================================================

[Step 1/5] Loading NAFDAC database Excel file…
[Step 2/5] Building product chunks…
[Step 3/5] Saving audit JSON…
[Step 4/5] Generating embedding vectors…
[Embedder] Generated 45 vector(s)  (dimension: 384)
[Step 5/5] Upserting into ChromaDB…

======================================================================
  ✅  INGESTION COMPLETE
  Products loaded   : 15
  Chunks built      : 45
  Duplicates skipped: 0
  DB total          : 45 document(s)
  Warnings          : 0
======================================================================
```

Files written after ingestion:
```
sabilens_rag/chroma_db/              ← vector store (survives restarts)
sabilens_rag/data/processed/nafdac_chunks.json
sabilens_rag/data/processed/ingestion_report.json
```

Only re-run ingestion when `nafdac_database.xlsx` changes. It is safe to re-run — upsert never duplicates.

---

## Step 2 — Start the API server

```bash
cd sabilens_rag/
python main.py --mode serve
```

Expected output:
```
======================================================================
  SabiLens — NAFDAC Verification API
  URL:  http://0.0.0.0:8000
  Docs: http://localhost:8000/docs
======================================================================

INFO:     Application startup complete.
```

The server is ready when you see "Application startup complete".
Open `http://localhost:8000/docs` in your browser for the interactive Swagger UI.

---

## Step 3 — Verify it is working (manual smoke tests)

Run each of these from a second terminal. Keep the server running.

**Health check:**
```bash
curl http://localhost:8000/verify/health
```
Expected:
```json
{"status": "healthy", "documents_indexed": 45, "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"}
```

**Authentic product scan (Kellogg's Corn Flakes):**
```bash
curl -X POST http://localhost:8000/verify/product \
  -H "Content-Type: application/json" \
  -d '{"nafdac_no": "A8-4114", "scanned_subcategory": "corn flakes"}'
```
Expected:
```json
{
  "verified": true,
  "verification_score": 1.0,
  "status_code": "VERIFIED",
  "severity": "NONE",
  "summary": "'KELLOGG'S CORN FLAKES' is a valid, registered NAFDAC product.",
  ...
}
```

**Fake product (number not in database):**
```bash
curl -X POST http://localhost:8000/verify/product \
  -H "Content-Type: application/json" \
  -d '{"nafdac_no": "FAKE-9999", "scanned_subcategory": "cereal"}'
```
Expected: `"status_code": "NOT_FOUND"`, `"verification_score": 0.0`

**Counterfeit (valid number, wrong product type):**
```bash
curl -X POST http://localhost:8000/verify/product \
  -H "Content-Type: application/json" \
  -d '{"nafdac_no": "A8-4114", "scanned_subcategory": "cosmetics"}'
```
Expected: `"status_code": "SUBCATEGORY_MISMATCH"`, `"verification_score": 0.2`

**Near-expiry product (Lipton Tea — expires 2026-03-28):**
```bash
curl -X POST http://localhost:8000/verify/product \
  -H "Content-Type: application/json" \
  -d '{"nafdac_no": "01-0132", "scanned_subcategory": "tea"}'
```
Expected: `"status_code": "VERIFIED_NEAR_EXPIRY"`, `"severity": "WARNING"`

**Semantic search (when NAFDAC number unreadable):**
```bash
curl -X POST http://localhost:8000/verify/search \
  -H "Content-Type: application/json" \
  -d '{"product_text": "kelloggs corn flakes nigeria cereal", "n": 3}'
```
Expected: list of matching products with similarity scores.

---

## Step 4 — Test the orchestrator directly (Python)

With the server running, open a Python shell from `sabilens/`:

```python
import sys
sys.path.insert(0, ".")

from ai_engine.orchestrator.scan_orchestrator import ScanOrchestrator

orc = ScanOrchestrator()

# Clean product
result = orc.scan("A8-4114", "corn flakes")
print(result.final_verdict, result.final_score)   # AUTHENTIC 0.88

# Not in database
result = orc.scan("FAKE-9999", "cereal")
print(result.final_verdict, result.final_score)   # FAKE 0.0

# Counterfeit
result = orc.scan("A8-4114", "cosmetics")
print(result.final_verdict, result.final_score)   # FAKE 0.2

# Full reasoning trace
print(orc.explain("A8-4114", "corn flakes"))
```

---

## Step 5 — Run all tests

All tests are run from the `sabilens/` root. The `conftest.py` there handles `PYTHONPATH` automatically for pytest.

```bash
cd sabilens/

# All tests across the full system (runs 9 test files)
pytest -v

# Individual test files — run in this order to confirm each layer:
pytest sabilens_rag/tests/test_nafdac_normalizer.py -v    # Layer 1: data cleaning
pytest sabilens_rag/tests/test_excel_loader.py -v         # Layer 2: Excel ingestion
pytest sabilens_rag/tests/test_chunk_builder.py -v        # Layer 3: chunk building
pytest sabilens_rag/tests/test_embedder.py -v             # Layer 4: vector embedding
pytest sabilens_rag/tests/test_chroma_client.py -v        # Layer 5: vector store
pytest sabilens_rag/tests/test_subcategory_alignment.py -v # Layer 6: category matching
pytest sabilens_rag/tests/test_regulatory_scorer.py -v    # Layer 7: scoring logic
pytest sabilens_rag/tests/test_verification_agent.py -v   # Layer 8: ReAct agent
pytest ai_engine/tests/test_scan_orchestrator.py -v       # Layer 9: orchestrator
```

Expected: all tests pass, no server required (everything is mocked or uses temp stores).

---

## What each test file covers

| File | What it tests | Needs server? |
|------|--------------|---------------|
| test_nafdac_normalizer.py | NAFDAC number cleaning — strips NBSP, fixes dashes, handles suffixes | No |
| test_excel_loader.py | Excel loading, all 15 rows, field extraction, bad data handling | No (reads xlsx directly) |
| test_chunk_builder.py | Chunk building, deduplication, text format, metadata shape | No |
| test_embedder.py | Embedding model loads, vector dimension 384, L2 normalisation | No (loads model) |
| test_chroma_client.py | Upsert, query, WHERE filter, idempotency, reset | No (in-memory store) |
| test_subcategory_alignment.py | Category alias matching, mismatch detection, severity | No |
| test_regulatory_scorer.py | All 4 verdict paths: NOT_FOUND, EXPIRED, MISMATCH, VERIFIED | No |
| test_verification_agent.py | ReAct loop, all verdict paths, fallback, trace, tool sequence | No (mocked tools) |
| test_scan_orchestrator.py | Pipeline fusion, override logic, mock signals, PipelineResult shape | No (mocked agent) |

---

## All 5 NAFDAC number formats the system handles

| Format | Example | Product |
|--------|---------|---------|
| Alpha-short | A8-4114 | Kellogg's Corn Flakes |
| Alpha-long serial | A8-100798 | Dangote Sugar |
| Numeric prefix | 01-0132 | Lipton Tea |
| With letter suffix | A8-8893L | Sedoso Vegetable Oil |
| With NBSP prefix (raw OCR) | \xa001-0132 | cleaned to 01-0132 |

---

## All possible verdict shapes

| Scenario | status_code | final_verdict | score | severity |
|----------|------------|---------------|-------|----------|
| Clean product | VERIFIED | AUTHENTIC | 0.88 | NONE |
| Near-expiry (< 60 days) | VERIFIED_NEAR_EXPIRY | AUTHENTIC | 0.81 | WARNING |
| Registration expired | EXPIRED | SUSPICIOUS | 0.48 | WARNING |
| Number not in database | NOT_FOUND | FAKE | 0.0 | CRITICAL |
| Wrong product type | SUBCATEGORY_MISMATCH | FAKE | 0.2 | CRITICAL |
| Agent crashed | AGENT_ERROR | FAKE | 0.0 | CRITICAL |

---

## Common errors and fixes

**`ModuleNotFoundError: No module named 'sabilens_rag'`**
→ You are not in `sabilens/` root or `PYTHONPATH` is not set.
```bash
cd sabilens/ && export PYTHONPATH=$(pwd)
```

**`RuntimeError: ChromaDB collection is empty`** or health returns `documents_indexed: 0`
→ Ingestion was not run, or was run from the wrong directory.
```bash
cd sabilens_rag/ && python main.py --mode ingest
```

**`ConnectionError: A3 RAG service is unreachable`** (from a4_fusion)
→ The API server is not running.
```bash
cd sabilens_rag/ && python main.py --mode serve
```

**`FileNotFoundError: Database not found`**
→ The Excel file is missing or path is wrong.
→ Check that `sabilens_rag/data/raw/nafdac_database.xlsx` exists.

**Test failures in test_excel_loader.py or test_chunk_builder.py**
→ Run tests from `sabilens/` not from inside `sabilens_rag/`:
```bash
cd sabilens/ && pytest -v
```
