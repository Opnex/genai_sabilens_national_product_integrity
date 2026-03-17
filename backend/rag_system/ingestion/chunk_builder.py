"""
ingestion/chunk_builder.py
--------------------------
Converts each NAFDACEntry into a ProductChunk ready for embedding and
storage in ChromaDB.

CHUNKING STRATEGY: ONE ENTRY = ONE CHUNK
  This is a structured registry — not a prose document.  Each row is an
  atomic, self-contained regulatory record.  Sliding-window or paragraph
  splitting would be semantically wrong: every field belongs together.

EMBEDDING TEXT DESIGN
  The 'text' field of each chunk is a carefully ordered natural-language
  sentence that the embedding model will read.

  Why natural language over raw JSON key-value pairs?
    • Transformer-based sentence encoders were trained on natural text.
      Sentences outperform bare key-value strings for semantic similarity.
    • Field ordering matters: the most discriminative fields (product name,
      NAFDAC number, subcategory) appear first because early tokens carry
      more weight when sequence length is truncated.
    • Including the manufacturer and applicant name enables semantic
      brand-based retrieval: "Unilever deodorant" → Rexona Xtra Cool.

  Text template (filled per entry):
    "Product: {name}. NAFDAC No: {nafdac_no}. Category: {subcategory}.
     Applicant: {applicant}. Manufacturer: {manufacturer}.
     Presentation: {presentation}. Country: {country}.
     Expiry Date: {expiry_iso}."

  Fields omitted when empty: presentation (some entries may be sparse).

CHUNK ID DESIGN
  chunk_id = MD5( nafdac_no_clean + "|" + product_name_upper )

  Why MD5?
    • Deterministic: same product always gets the same ID across re-runs.
    • Enables ChromaDB upsert: existing records are updated, not duplicated.
    • Fast: 15 rows is trivial; this scales to millions.

  For entries with no valid NAFDAC number: MD5( "" + "|" + product_name_upper )
  so they still get a unique, stable ID and can be upserted safely.
"""

import hashlib
import json
from pathlib import Path
from typing import Tuple

from ingestion.schema import NAFDACEntry, ProductChunk


def _build_text(entry: NAFDACEntry) -> str:
    """
    Construct the natural-language embedding text for one NAFDACEntry.

    The text is intentionally verbose to maximise semantic search coverage:
    a user searching for "corn flakes kelloggs registration" or
    "unilever deodorant nafdac" should retrieve the correct record.

    Args:
        entry: Fully cleaned NAFDACEntry from the loader.

    Returns:
        Natural-language string suitable for encoding by a sentence transformer.

    Examples:
        "Product: KELLOGG'S CORN FLAKES. NAFDAC No: A8-4114.
         Category: Cereals and Cereal Products. Applicant: KELLOGG TOLARAM
         NIGERIA LIMTED. Manufacturer: KT LFTZ ENTERPRISE.
         Presentation: 300G HARDBOARD PACK. Country: Nigeria.
         Expiry Date: 2029-07-30."

        "Product: Vaseline blueseal pure petroleum jelly original.
         NAFDAC No: 02-0385. Category: Cosmetics. Applicant: UNILEVER NIGERIA PLC.
         Manufacturer: UNILEVER NIGERIA PLC.
         Presentation: Light yellow gel with a blue cover and transparent body PET 225ml.
         Country: Nigeria. Expiry Date: 2028-12-20."
    """
    parts = [
        f"Product: {entry.product_name}",
        f"NAFDAC No: {entry.nafdac_no_clean or entry.nafdac_no or 'Not available'}",
        f"Category: {entry.subcategory}",
        f"Applicant: {entry.applicant_name}",
        f"Manufacturer: {entry.manufacturer}",
    ]

    # Presentation can be long (119 chars for Golden Penny Pasta) — include fully
    # so that packaging-based searches ("hardboard pack", "PET bottle") work.
    if entry.presentation.strip():
        parts.append(f"Presentation: {entry.presentation}")

    parts.append(f"Country: {entry.country}")

    if entry.expiry_date_iso:
        parts.append(f"Expiry Date: {entry.expiry_date_iso}")

    return ". ".join(parts) + "."


def _build_chunk_id(nafdac_no_clean: str, product_name_upper: str) -> str:
    """
    Compute a deterministic MD5 chunk identifier.

    The ID is stable across re-runs: re-ingesting the same spreadsheet
    after a NAFDAC update will upsert (not duplicate) existing records.

    Args:
        nafdac_no_clean:    Canonical NAFDAC number (may be '' for null rows).
        product_name_upper: Upper-cased product name for case-insensitive uniqueness.

    Returns:
        32-character lowercase hexadecimal MD5 digest.
    """
    raw = f"{nafdac_no_clean}|{product_name_upper.strip()}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def build_chunks(entries: list) -> Tuple[list, dict]:
    """
    Convert a list of NAFDACEntry objects into a list of ProductChunks.

    Deduplicates by chunk_id: if two entries hash to the same ID (identical
    NAFDAC number AND identical product name), only the first occurrence is kept.
    This guards against accidental duplicate rows being added to the spreadsheet.

    Args:
        entries: List of NAFDACEntry objects from ingestion/excel_loader.py.

    Returns:
        Tuple of:
          chunks (list[ProductChunk]): Unique chunks ready for embedding.
          stats  (dict):
            total_entries_processed  — input list length
            chunks_built             — unique chunks produced
            duplicates_skipped       — entries whose chunk_id already existed
            subcategory_breakdown    — {subcategory: count} among built chunks
            null_nafdac_chunks       — chunks with no clean NAFDAC number

    Example:
        >>> entries, _ = load_database()
        >>> chunks, stats = build_chunks(entries)
        >>> print(stats['chunks_built'])
        15
    """
    chunks: list[ProductChunk] = []
    seen_ids: set[str] = set()
    duplicates_skipped = 0
    subcategory_counts: dict[str, int] = {}

    for entry in entries:
        chunk_id = _build_chunk_id(entry.nafdac_no_clean, entry.product_name_upper)

        # Skip true duplicates (same NAFDAC number AND same product name)
        if chunk_id in seen_ids:
            duplicates_skipped += 1
            continue
        seen_ids.add(chunk_id)

        text = _build_text(entry)

        # ── Metadata dict: all values MUST be strings for ChromaDB ───────────
        # ChromaDB's WHERE-clause filtering requires string, int, or float values.
        # We store everything as strings to avoid type-conversion surprises.
        metadata: dict[str, str] = {
            "nafdac_no"        : entry.nafdac_no,
            "nafdac_no_clean"  : entry.nafdac_no_clean,
            "product_name"     : entry.product_name,
            "product_name_upper": entry.product_name_upper,
            "subcategory"      : entry.subcategory,
            "presentation"     : entry.presentation,
            "applicant_name"   : entry.applicant_name,
            "country"          : entry.country,
            "manufacturer"     : entry.manufacturer,
            "expiry_date_raw"  : entry.expiry_date_raw,
            "expiry_date_iso"  : entry.expiry_date_iso,
        }

        # Track subcategory distribution
        subcategory_counts[entry.subcategory] = (
            subcategory_counts.get(entry.subcategory, 0) + 1
        )

        chunks.append(ProductChunk(
            chunk_id        = chunk_id,
            text            = text,
            metadata        = metadata,
            subcategory     = entry.subcategory,
            nafdac_no_clean = entry.nafdac_no_clean,
            expiry_date_iso = entry.expiry_date_iso,
        ))

    stats = {
        "total_entries_processed" : len(entries),
        "chunks_built"            : len(chunks),
        "duplicates_skipped"      : duplicates_skipped,
        "subcategory_breakdown"   : subcategory_counts,
        "null_nafdac_chunks"      : sum(1 for c in chunks if not c.nafdac_no_clean),
    }

    print(f"[ChunkBuilder] ✅  Built {len(chunks)} unique chunks "
          f"(skipped {duplicates_skipped} duplicate(s)).")
    print(f"[ChunkBuilder] Subcategory distribution: {subcategory_counts}")

    return chunks, stats


def save_chunks(chunks: list, output_path: str) -> None:
    """
    Serialise all ProductChunks to a JSON file for human audit and debugging.

    This file is NOT used by the pipeline — ChromaDB is the source of truth.
    The JSON is useful for:
      • Inspecting chunk text quality before committing to a re-embedding.
      • Counting, filtering, and spot-checking chunks without starting ChromaDB.
      • Tracking changes between Greenbook versions in version control.

    Args:
        chunks:      List of ProductChunk objects to serialise.
        output_path: Destination file path (parent directories created if absent).
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    serialisable = [c.model_dump() for c in chunks]

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(serialisable, f, indent=2, ensure_ascii=False)

    print(f"[ChunkBuilder] 💾  Saved {len(chunks)} chunks to {output_path}")