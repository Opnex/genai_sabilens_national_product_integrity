CATEGORY_RULES = {
    "pharma": {
        "required_fields": [
            "brand_detected",
            "nafdac_number",
            "batch_number",
            "expiry_date",
            "manufacturer_name"
        ],
        "expiry_regex": r"^\d{4}-\d{2}-\d{2}$",
        "batch_regex": r"^[A-Za-z0-9]{5,12}$"
    },

    "cosmetics": {
        "required_fields": [
            "brand_detected",
            "nafdac_number",
            "batch_number",
            "manufacturer_name",
            "net_weight_or_volume"
        ],
        "expiry_regex": r"^\d{4}-\d{2}-\d{2}$",     
            "batch_regex": r"^[A-Za-z0-9]{5,12}$"
        },

    "food": {
        "required_fields": [
            "brand_detected",
            "nafdac_number",
            "batch_number",
            "expiry_date",
            "net_weight_or_volume"
        ],
        "expiry_regex": r"^\d{4}-\d{2}-\d{2}$",
        "batch_regex": r"^[A-Za-z0-9]{5,12}$"
    }
}