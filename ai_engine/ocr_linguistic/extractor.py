"""
OCR Extractor
Handles:
  - Running PaddleOCR on the product image
  - Parsing raw text blocks into structured metadata JSON

NAFDAC FALLBACK STRATEGY:
  If the primary full-image OCR pass doesn't find a NAFDAC number,
  a second pass runs on a cropped + upscaled bottom 25% of the image.
  NAFDAC numbers on Nigerian product labels almost always appear in the
  bottom section in small print. Upscaling that region 2x gives PaddleOCR
  a much better chance of reading it.
"""

import cv2
import numpy as np
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
        _ocr_engine = PaddleOCR(use_angle_cls=True, lang="en", ocr_version="PP-OCRv4")
    return _ocr_engine




# ==============================================================
# OCR EXTRACTION
# ==============================================================

def extract_text_blocks(image_path: str) -> list[dict]:
    """
    Run PaddleOCR on the product image.
    If no NAFDAC number is found in the full-image pass, runs a second
    pass on the bottom 25% of the image (cropped + upscaled 2x).

    Args:
        image_path: File path to the product image (JPG, PNG, etc.)

    Returns:
        List of dicts, each with:
          - 'text': the detected string
          - 'confidence': float 0.0-1.0
    """
    ocr_engine = get_ocr_engine()

    # Primary pass: full image 
    results = ocr_engine.ocr(image_path)
    blocks  = _parse_ocr_results(results)

    # Check if NAFDAC was found 
    full_text = " ".join(b["text"] for b in blocks)
    nafdac    = extract_nafdac_number(full_text)

    if nafdac:
        return blocks

    # Fallback pass: bottom 25% crop + 2x upscale 
    # NAFDAC numbers are printed in small text at the bottom of Nigerian labels.
    # Upscaling the crop 2x before OCR significantly improves detection rate.
    bottom_crop = _crop_bottom(image_path, fraction=0.30, upscale=2.0)

    if bottom_crop is not None:
        fallback_results = ocr_engine.ocr(bottom_crop)
        fallback_blocks  = _parse_ocr_results(fallback_results)

        # Merge fallback blocks — deduplicate by text content
        existing_texts = {b["text"] for b in blocks}
        for fb in fallback_blocks:
            if fb["text"] not in existing_texts:
                blocks.append(fb)
                existing_texts.add(fb["text"])

    return blocks

def _parse_ocr_results(results) -> list:
    """Parse raw PaddleOCR results into clean block dicts."""
    blocks = []
    if not results or not results[0]:
        return blocks
    for line in results[0]:
        text       = line[1][0].strip()
        confidence = round(line[1][1], 4)
        if text:
            blocks.append({"text": text, "confidence": confidence})
    return blocks

def _crop_bottom(image_path: str, fraction: float = 0.30, upscale: float = 2.0):
    """
    Crop the bottom `fraction` of the image and upscale it.

    Args:
        image_path: Path to the image file.
        fraction:   Fraction of image height to crop from bottom (0.30 = bottom 30%).
        upscale:    Scale factor for upscaling the crop.

    Returns:
        Upscaled numpy array ready for PaddleOCR, or None if image can't be read.
    """
    img = cv2.imread(image_path)
    if img is None:
        return None

    h, w = img.shape[:2]
    y1   = int(h * (1.0 - fraction))
    crop = img[y1:h, 0:w]

    new_h = int(crop.shape[0] * upscale)
    new_w = int(crop.shape[1] * upscale)
    upscaled = cv2.resize(crop, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

    return upscaled


def build_raw_text(blocks: list) -> str:
    """Join all text blocks into a single string for regex matching."""
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


def extract_batch_number(raw_text: str):
    """Find the batch/lot number in the label text."""
    match = BATCH_IN_TEXT_PATTERN.search(raw_text)
    return match.group(1).upper() if match else None


def extract_expiry_date(raw_text: str):
    """
    Find the expiry date using common date formats.
    Handles: 12/2026, 12-2026, DEC 2026, DEC. 2026
    """
    match = EXPIRY_PATTERN.search(raw_text)
    return match.group(0).strip() if match else None


def extract_product_name(blocks: list):
    """
    Identify the product name from OCR blocks.
    Highest-confidence block that is not purely numeric and has > 2 chars.
    """
    candidates = [
        b for b in blocks
        if not b["text"].isdigit() and len(b["text"]) > 2
    ]
    if not candidates:
        return None
    candidates.sort(key=lambda x: x["confidence"], reverse=True)
    return candidates[0]["text"]


def extract_manufacturer_name(raw_text: str):
    """Find the manufacturer/distributor name using common label keywords."""
    match = MANUFACTURER_IN_TEXT_PATTERN.search(raw_text)
    return match.group(1).strip() if match else None


# ==============================================================
# METADATA BUILDER
# ==============================================================

def build_metadata(blocks: list) -> dict:
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
        "product_name":      extract_product_name(blocks),
        "nafdac_number":     extract_nafdac_number(raw_text),
        "batch_number":      extract_batch_number(raw_text),
        "expiry_date":       extract_expiry_date(raw_text),
        "manufacturer_name": extract_manufacturer_name(raw_text),
        "raw_ocr_text":      raw_text,
        "avg_ocr_confidence": avg_confidence,
    }
