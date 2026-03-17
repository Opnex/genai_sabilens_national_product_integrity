import re
from datetime import datetime


NAFDAC_PATTERN = r"\b\d{2}-\d{4}\b"
BATCH_PATTERN = r"(?:BN[:=]?\s*)([A-Za-z0-9]+)"
DATE_6_DIGIT_PATTERN = r"\b\d{6}\b"
DATE_SLASH_PATTERN = r"\b\d{2}/\d{2}/\d{2}\b"
VOLUME_PATTERN = r"\b\d+\s?(ml|g|kg|litre|l)\b"


# -----------------------
# Normalizers
# -----------------------

def normalize_nafdac(raw: str):
    match = re.search(NAFDAC_PATTERN, raw)
    if match:
        return f"NAFDAC-{match.group()}"
    return None


def normalize_batch(raw: str):
    match = re.search(BATCH_PATTERN, raw, re.IGNORECASE)
    if match:
        return match.group(1).strip().upper()
    return None


def normalize_date(raw: str):
    # Look specifically for EXP or MFD prefixes
    exp_pattern = r"EXP[:=]?\s*(\d{6})"
    mfd_pattern = r"MFD[:=]?\s*(\d{6})"

    # Try EXP first
    exp_match = re.search(exp_pattern, raw, re.IGNORECASE)
    if exp_match:
        try:
            dt = datetime.strptime(exp_match.group(1), "%d%m%y")
            return dt.strftime("%Y-%m-%d")
        except:
            pass

    # Fallback: generic 6 digit
    match_6 = re.search(r"\b\d{6}\b", raw)
    if match_6:
        try:
            dt = datetime.strptime(match_6.group(), "%d%m%y")
            return dt.strftime("%Y-%m-%d")
        except:
            pass

    return None

# -----------------------
# Manufacturer Extraction
# -----------------------

def extract_manufacturer(text: str):

    pattern = r"(Unilever.*?(Plc|Ltd|Limited|Inc|Incorporated))"

    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return match.group(1).strip()

    return None

# -----------------------
# Net Weight / Volume
# -----------------------

def extract_volume(text: str):
    match = re.search(VOLUME_PATTERN, text, re.IGNORECASE)
    if match:
        return match.group().strip()
    return None

def extract_product_name(raw_text: str, brand: str):

    if not raw_text or not brand:
        return None

    lines = raw_text.split()

    # Filter candidates
    candidates = []

    for line in raw_text.split("."):
        clean = line.strip()

        if not clean:
            continue

        if "www" in clean.lower():
            continue

        if "nafdac" in clean.lower():
            continue

        if any(unit in clean.lower() for unit in ["ml", "g", "kg", "litre"]):
            continue

        if brand.lower() in clean.lower():
            candidates.append(clean)

    # Prefer shorter descriptive line
    if candidates:
        candidates.sort(key=lambda x: len(x))
        return candidates[0].strip()

    return None

# -----------------------
# Main Extraction Function
# -----------------------

def extract_structured_metadata(full_text: str, brand_detected: str = None):

    nafdac = normalize_nafdac(full_text)
    batch = normalize_batch(full_text)
    expiry = normalize_date(full_text)
    manufacturer = extract_manufacturer(full_text)
    volume = extract_volume(full_text)
    product_name = extract_product_name(full_text, brand_detected)
    valid_format = all([nafdac, batch])

    return {
        "nafdac_number": nafdac,
        "batch_number": batch,
        "expiry_date": expiry,
        "manufacturer_name": manufacturer,
        "net_weight_or_volume": volume,
        "product_name": product_name,
        "valid_format": valid_format
    }