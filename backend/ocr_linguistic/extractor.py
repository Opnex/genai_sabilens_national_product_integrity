"""
OCR Extractor
==============================
Handles:
  - Running PaddleOCR on the product image
  - Parsing raw text blocks into structured metadata JSON
"""

from paddleocr import PaddleOCR
from .config import (
    NAFDAC_IN_TEXT_PATTERN,
    NAFDAC_PATTERN,
    BATCH_IN_TEXT_PATTERN,
    EXPIRY_PATTERN,
    MANUFACTURER_IN_TEXT_PATTERN,
)

# Initialize PaddleOCR once at module level (avoids reloading model repeatedly)
# use_angle_cls=True handles rotated or tilted text on packaging
_ocr_engine = None

def get_ocr_engine():
    global _ocr_engine
    if _ocr_engine is None:
        _ocr_engine = PaddleOCR(use_angle_cls=True, lang="en")
    return _ocr_engine




# ==============================================================
# OCR EXTRACTION
# ==============================================================

def extract_text_blocks(image_path: str) -> list[dict]:
    """
    Run PaddleOCR on the product image.

    Args:
        image_path: File path to the product image (JPG, PNG, etc.)

    Returns:
        List of dicts, each with:
          - 'text': the detected string
          - 'confidence': float 0.0–1.0 (how sure PaddleOCR is)
    """
    ocr_engine = get_ocr_engine()
    results = ocr_engine.ocr(image_path)
    print("OCR Results:", results)
    blocks = []

    if not results or not results[0]:
        return blocks

    for line in results[0]:
        text = line[1][0].strip()
        confidence = round(line[1][1], 4)
        if text:
            blocks.append({"text": text, "confidence": confidence})

    return blocks


def build_raw_text(blocks: list[dict]) -> str:
    """
    Join all text blocks into a single string.
    Used for regex-based pattern matching across the full label.
    """
    return " ".join(b["text"] for b in blocks)


# ==============================================================
# INDIVIDUAL FIELD EXTRACTORS
# ==============================================================

def extract_nafdac_number(raw_text: str) -> str | None:
    """
    Find the NAFDAC registration number in the label text.
    Tries keyword-based match first, falls back to format match.
    """
    # Primary: look for NAFDAC/REG keyword followed by the number
    match = NAFDAC_IN_TEXT_PATTERN.search(raw_text)
    if match:
        return match.group(1).upper()

    # Fallback: scan each token for NAFDAC number format
    for token in raw_text.split():
        cleaned = token.strip(".,;:")
        if NAFDAC_PATTERN.match(cleaned.upper()):
            return cleaned.upper()

    return None


def extract_batch_number(raw_text: str) -> str | None:
    """
    Find the batch/lot number in the label text.
    """
    match = BATCH_IN_TEXT_PATTERN.search(raw_text)
    return match.group(1).upper() if match else None


def extract_expiry_date(raw_text: str) -> str | None:
    """
    Find the expiry date using common date formats.
    Handles: 12/2026, 12-2026, DEC 2026, DEC. 2026
    """
    match = EXPIRY_PATTERN.search(raw_text)
    return match.group(0).strip() if match else None


def extract_product_name(blocks: list[dict]) -> str | None:
    """
    Identify the product name from OCR blocks.
    Strategy: highest-confidence block that is not purely numeric
    and has more than 2 characters (filters out noise like dates).
    """
    candidates = [
        b for b in blocks
        if not b["text"].isdigit() and len(b["text"]) > 2
    ]
    if not candidates:
        return None

    candidates.sort(key=lambda x: x["confidence"], reverse=True)
    return candidates[0]["text"]


def extract_manufacturer_name(raw_text: str) -> str | None:
    """
    Find the manufacturer/distributor name using common label keywords.
    """
    match = MANUFACTURER_IN_TEXT_PATTERN.search(raw_text)
    return match.group(1).strip() if match else None


# ==============================================================
# METADATA BUILDER
# ==============================================================

def build_metadata(blocks: list[dict]) -> dict:
    """
    Combine all field extractors into one structured metadata dict.

    Args:
        blocks: List of OCR text blocks from extract_text_blocks()

    Returns:
        Structured metadata dict ready for linguistic validation.
    """
    raw_text = build_raw_text(blocks)

    avg_confidence = (
        round(sum(b["confidence"] for b in blocks) / len(blocks), 4)
        if blocks else 0.0
    )

    return {
        "product_name": extract_product_name(blocks),
        "nafdac_number": extract_nafdac_number(raw_text),
        "batch_number": extract_batch_number(raw_text),
        "expiry_date": extract_expiry_date(raw_text),
        "manufacturer_name": extract_manufacturer_name(raw_text),
        "raw_ocr_text": raw_text,
        "avg_ocr_confidence": avg_confidence,
    }