"""Response utilities"""
from datetime import datetime
from typing import Any, Dict, Optional, List


def success_response(data: Any, message: str = "Success", status_code: int = 200) -> Dict:
    """Standard success response"""
    return {
        "success": True,
        "data": data,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
    }


def error_response(code: str, message: str, details: Optional[Dict] = None, status_code: int = 400) -> Dict:
    """Standard error response"""
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


def paginated_response(
    data: List,
    page: int = 1,
    limit: int = 20,
    total: int = 0,
    message: str = "Success",
) -> Dict:
    """Paginated response"""
    pages = (total + limit - 1) // limit if limit > 0 else 1
    return {
        "success": True,
        "data": data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": pages,
        },
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
    }
