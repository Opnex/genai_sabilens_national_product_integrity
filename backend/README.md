# SabiLens Backend

```
sabilens-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app entry
│   ├── config.py                    # Settings from .env
│   ├── database.py                  # Async SQLAlchemy setup
│   ├── dependencies.py              # Auth guards, DB injection
│   ├── models/                      # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py                  # User, Session, OTP
│   │   ├── company.py               # Company, Settings, APIKey, SubscriptionPlan
│   │   ├── product.py               # Product, Category, Barcode, Embedding
│   │   ├── scan.py                  # Scan, ScanAnalysis, Report, Evidence
│   │   ├── alert.py                 # Alert, Notification, Preferences
│   │   ├── nafdac.py                # Case, EnforcementAction
│   │   └── analytics.py             # Hotspot, Vendor, Analytics, AuditLog
│   ├── schemas/                     # Pydantic request/response models
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── consumer.py
│   │   ├── company.py
│   │   ├── nafdac.py
│   │   └── shared.py
│   ├── routers/                     # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py                  # POST /register, /login, /logout, etc.
│   │   ├── consumer.py              # GET /scans, POST /scan, GET /notifications
│   │   ├── company.py               # GET /dashboard, POST /products, GET /alerts
│   │   ├── nafdac.py                # GET /companies, POST /cases, GET /analytics
│   │   └── shared.py                # GET /verify/nafdac, GET /location/states
│   ├── services/                    # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── scan_service.py
│   │   ├── ai_service.py            # Celery tasks for AI pipeline
│   │   ├── report_service.py
│   │   ├── notification_service.py
│   │   └── geo_service.py           # PostGIS queries for heatmap
│   ├── core/                        # Core utilities
│   │   ├── __init__.py
│   │   ├── security.py              # JWT, bcrypt
│   │   ├── websocket.py             # WebSocket connection manager
│   │   └── celery_app.py            # Celery config
│   └── utils/                       # Helpers
│       ├── __init__.py
│       ├── response.py              # standard response format
│       └── pagination.py            # pagination helpers
├── alembic/                         # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/                    # Migration files
├── tests/                           # Unit & integration tests
├── .env.example                     # Environment template
├── requirements.txt                 # Python dependencies
├── docker-compose.yml               # PostgreSQL + Redis + API
├── Dockerfile                       # API container
└── README.md                        # Documentation
```

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env

# 3. Start PostgreSQL + Redis
docker-compose up -d

# 4. Run migrations
alembic upgrade head

# 5. Start API
uvicorn backend.main:app --reload

# 6. Start Celery worker (separate terminal)
celery -A app.core.celery_app worker --loglevel=info

# 7. Access Swagger docs
http://localhost:8000/api/docs
```

## PostgreSQL Extensions

```sql
CREATE EXTENSION "uuid-ossp";
CREATE EXTENSION "postgis";
CREATE EXTENSION "pgcrypto";
```

## Models Overview

- **User**: Consumer, Company Admin, NAFDAC Officer/Admin
- **Company**: Product manufacturers (verified by NAFDAC)
- **Product**: NAFDAC-registered products with embeddings (6-view AI fingerprints)
- **Scan**: User scans product images → AI analysis → authenticity verdict
- **Report**: Consumer reports counterfeit → generates Alert
- **Alert**: Sent to Company & NAFDAC dashboards
- **Case**: NAFDAC investigation case (linked to Report)
- **EnforcementAction**: Raid, Seizure, Notice, Prosecution
- **Hotspot**: Geographic clusters of counterfeits (PostGIS)
- **Vendor**: Blacklisted sellers & risk tracking

## API Response Format

All endpoints return:

```json
{
  "success": true,
  "data": {},
  "message": "Success",
  "timestamp": "2026-03-01T12:00:00"
}
```

Error:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": {}
  },
  "timestamp": "2026-03-01T12:00:00"
}
```

Paginated:

```json
{
  "success": true,
  "data": [],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5
  },
  "message": "Success"
}
```

## Team Branches

- **tunjipaul** (Foundation): `main/dev` - Core DB, Auth, AI Bridge, WebSocket, Docker
- **Mr Openx** (Company): `feature/company` - Products, Reports, Evidence, Heatmap
- **Barrister Femi** (NAFDAC): `feature/nafdac` - Officers, Cases, Analytics, Enforcement

Merge order: tunjipaul → Mr Openx → Barrister Femi
