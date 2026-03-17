# SabiLens Backend - Developer Quick Reference

## 🔧 Adding New Endpoints

### 1. Create Route Handler
```python
# backend/routers/new_module.py
from fastapi import APIRouter, Depends, HTTPException
from backend.utils.dependencies import get_current_user
from backend.databases import get_db

router = APIRouter()

@router.get("/items/{item_id}")
async def get_item(item_id: str, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        item = await ItemService.get_item(db, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Not found")
        return success_response(item.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### 2. Register in main.py
```python
from backend.routers import new_module

app.include_router(new_module.router, prefix="/api/v1/new", tags=["new"])
```

---

## 📦 Using Services

### Example: Scan Service
```python
from backend.services.scan_service import ScanService
from backend.schemas.consumer import ScanCreateRequest

# Create a scan
scan = await ScanService.create_scan(db, user_id, ScanCreateRequest(...))

# Get user scans
scans, total = await ScanService.get_user_scans(db, user_id, limit=20, offset=0)

# Update status
await ScanService.update_scan_status(db, scan_id, "analyzing")

# Record analysis
analysis = await ScanService.record_analysis(db, scan_id, {
    "confidence_score": 0.92,
    "visual_analysis": {...},
    "risk_level": "low"
})
```

---

## 🤖 Triggering Celery Tasks

### From Route Handler
```python
from backend.services.ai_service import process_visual_analysis

# Trigger async task
task = process_visual_analysis.delay(scan_id, image_url)

# Get task status later
task_result = AsyncResult(task.id, app=celery_app)
print(task_result.state)  # PENDING, STARTED, SUCCESS, FAILURE
print(task_result.result)  # Return value
```

### Monitoring Tasks
```bash
# See active tasks
celery -A app.core.celery_app inspect active

# See task stats
celery -A app.core.celery_app inspect stats

# Check specific task
celery -A app.core.celery_app inspect active_queues
```

---

## 🛡️ Role-Based Access Control

### Protect Route by Role
```python
from backend.utils.dependencies import require_role

@router.post("/admin-only")
async def admin_action(current_user = Depends(require_role("nafdac_admin")), db: AsyncSession = Depends(get_db)):
    # Only nafdac_admin role can access
    return success_response({"message": "Admin action"})
```

### Available Roles
- `consumer` - End users reporting counterfeits
- `company_admin` - Company staff managing products
- `nafdac_officer` - NAFDAC field officers
- `nafdac_admin` - NAFDAC headquarters admin

---

## 📝 Creating New Service

### Template
```python
# backend/services/my_service.py
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

class MyService:
    @staticmethod
    async def create_item(db: AsyncSession, data: dict):
        item = MyModel(
            field=data.get("field"),
            created_at=datetime.utcnow()
        )
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item
    
    @staticmethod
    async def get_items(db: AsyncSession, limit: int, offset: int):
        stmt = select(MyModel).limit(limit).offset(offset)
        result = await db.execute(stmt)
        items = result.scalars().all()
        return items
```

### Register Service
```python
# backend/services/__init__.py
from backend.services.my_service import MyService

__all__ = [..., "MyService"]
```

---

## 🗄️ Database Queries

### Create
```python
user = User(email="test@example.com", phone="+2348012345678")
db.add(user)
await db.commit()
await db.refresh(user)
```

### Read
```python
from sqlalchemy import select

stmt = select(User).where(User.email == "test@example.com")
result = await db.execute(stmt)
user = result.scalars().first()
```

### Update
```python
user.status = "active"
await db.commit()
await db.refresh(user)
```

### Delete
```python
await db.delete(user)
await db.commit()
```

### Pagination
```python
limit = 20
offset = (page - 1) * limit
stmt = select(User).limit(limit).offset(offset)
users = await db.execute(stmt)
```

---

## ✅ Request/Response Examples

### Register Request
```json
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "phone": "+2348012345678",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe",
  "role": "consumer"
}
```

### Register Response
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "phone": "+2348012345678",
      "role": "consumer",
      "status": "pending"
    },
    "tokens": {
      "access_token": "eyJ0eXAi...",
      "refresh_token": "eyJ0eXAi...",
      "expires_in": 900
    }
  }
}
```

### Scan Request
```json
POST /api/v1/consumer/scan
{
  "image_url": "https://cloudinary.com/image.jpg",
  "barcode": "5901234123457",
  "latitude": 6.5244,
  "longitude": 3.3792,
  "location_text": "Lekki, Lagos"
}
```

### Scan Response
```json
{
  "success": true,
  "data": {
    "id": "scan-uuid",
    "user_id": "user-uuid",
    "status": "pending",
    "created_at": "2026-03-01T10:30:00Z"
  }
}
```

---

## 🧪 Testing Pattern

### Test File Template
```python
# tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_register_user():
    response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "phone": "+2348012345678",
        "password": "test123",
        "first_name": "Test",
        "last_name": "User",
        "role": "consumer"
    })
    assert response.status_code == 201
    assert response.json()["success"] == True
```

### Run Specific Test
```bash
pytest tests/test_auth.py::test_register_user -v
```

---

## 🐍 Async/Await Patterns

### Always use async for I/O
```python
# ✅ CORRECT
async def get_user(db: AsyncSession, user_id: str):
    result = await db.execute(...)  # Database query
    return result.scalars().first()

# ❌ INCORRECT
def get_user(db: AsyncSession, user_id: str):
    result = db.execute(...)  # Not awaited!
```

### Celery task
```python
@celery_app.task
def sync_task(data):
    # Can be sync (blocking CPU work)
    return heavy_computation(data)

@celery_app.task  
async def async_task(data):
    # Can be async (I/O operations)
    result = await some_api_call(data)
    return result
```

---

## 🔐 Environment Secrets

### Never hardcode credentials
```python
# ✅ CORRECT
from backend.config import settings
api_key = settings.EXTERNAL_API_KEY

# ❌ INCORRECT
api_key = "sk_live_abc123xyz"  # Exposed!
```

### Add to .env
```env
EXTERNAL_API_KEY=sk_live_abc123xyz
```

### Access in code
```python
from backend.config import settings
key = settings.EXTERNAL_API_KEY
```

---

## 📊 Debugging Tips

### Enable Debug Logs
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Inspect Request
```python
@app.middleware("http")
async def log_request(request: Request, call_next):
    print(f"Method: {request.method}")
    print(f"URL: {request.url}")
    print(f"Headers: {request.headers}")
    response = await call_next(request)
    return response
```

### Check Database State
```python
# In route handler
stmt = select(User)
users = await db.execute(stmt)
print(f"Total users: {len(users.scalars().all())}")
```

---

## 📚 Common Imports

```python
# FastAPI & Starlette
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from fastapi.responses import JSONResponse

# SQLAlchemy
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

# Utilities
from datetime import datetime, timedelta
from uuid import uuid4
from typing import Optional, List

# Project modules
from backend.database import get_db
from backend.models import User, Scan
from backend.schemas import UserResponse
from backend.services import AuthService
from backend.utils.response import success_response
from backend.utils.dependencies import get_current_user
from backend.config import settings
```

---

## 🚀 Deployment Checklist

- [ ] Set production SECRET_KEY (min 32 chars)
- [ ] Configure DATABASE_URL with prod credentials
- [ ] Set REDIS_URL to prod instance
- [ ] Disable CORS wildcard, whitelist specific origins
- [ ] Enable HTTPS/TLS
- [ ] Setup Celery worker with supervisor/systemd
- [ ] Configure logging to file/Sentry
- [ ] Set up database backups
- [ ] Document all environment variables
- [ ] Test with load testing (locust)
- [ ] Setup monitoring (Datadog/NewRelic)

---

**Last Updated**: March 1, 2026
**Maintainer**: tunjipaul (Foundation & Auth Lead)
