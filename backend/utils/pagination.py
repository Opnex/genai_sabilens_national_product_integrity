"""Pagination utilities"""
from typing import Tuple


def parse_pagination(page: int = 1, limit: int = 20) -> Tuple[int, int]:
    """Parse and validate pagination parameters"""
    if page < 1:
        page = 1
    if limit < 1:
        limit = 20
    if limit > 100:
        limit = 100
    
    skip = (page - 1) * limit
    return skip, limit
