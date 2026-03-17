
SabiLens
FastAPI Backend - Developer README

1-Day Sprint  |  3-Person Team
tunjipaul
Foundation & Auth LeadMr Openx
Company & Evidence LeadBarrister Femi
NAFDAC & Analytics Lead

1. Project Overview
SabiLens is a multimodal AI platform for detecting counterfeit products in Nigeria. The FastAPI backend connects the mobile app, AI pipeline, PostgreSQL database, and regulatory dashboards. It must be demo-ready in one day.

LayerTechnologyFrameworkFastAPI (Python 3.11+)ORMSQLAlchemy 2.0 (async)DatabasePostgreSQL 15 + PostGIS + pgcryptoMigrationsAlembicAuthJWT (python-jose) + bcrypt password hashingAsync TasksCelery + Redis (for non-blocking AI pipeline calls)File StorageCloudinary or AWS S3Real-TimeFastAPI WebSockets (native)ValidationPydantic v2ContainerizationDocker + docker-compose

2. Project Structure
All three team members work inside the same repository. Every module is isolated to avoid merge conflicts.

sabilens-backend/
+-- app/
¦   +-- main.py                   # App entry point (tunjipaul)
¦   +-- config.py                 # Env variables (tunjipaul)
¦   +-- database.py               # Async DB session (tunjipaul)
¦   +-- dependencies.py           # Auth guards, DB injection (tunjipaul)
¦   +-- models/                   # SQLAlchemy ORM models
¦   ¦   +-- user.py               # (tunjipaul)
¦   ¦   +-- company.py            # (Mr Openx)
¦   ¦   +-- product.py            # (Mr Openx)
¦   ¦   +-- scan.py               # (tunjipaul)
¦   ¦   +-- report.py             # (Mr Openx)
¦   ¦   +-- alert.py              # (Barrister Femi)
¦   ¦   +-- analytics.py          # (Barrister Femi)
¦   +-- schemas/                  # Pydantic request/response models
¦   ¦   +-- auth.py               # (tunjipaul)
¦   ¦   +-- consumer.py           # (tunjipaul)
¦   ¦   +-- company.py            # (Mr Openx)
¦   ¦   +-- nafdac.py             # (Barrister Femi)
¦   ¦   +-- shared.py             # (tunjipaul)
¦   +-- routers/                  # Route handlers
¦   ¦   +-- auth.py               # (tunjipaul)
¦   ¦   +-- consumer.py           # (tunjipaul)
¦   ¦   +-- company.py            # (Mr Openx)
¦   ¦   +-- nafdac.py             # (Barrister Femi)
¦   ¦   +-- shared.py             # (Barrister Femi)
¦   +-- services/                 # Business logic
¦   ¦   +-- auth_service.py       # (tunjipaul)
¦   ¦   +-- scan_service.py       # (tunjipaul)
¦   ¦   +-- ai_service.py         # AI bridge (tunjipaul)
¦   ¦   +-- report_service.py     # (Mr Openx)
¦   ¦   +-- notification_service.py # (Barrister Femi)
¦   ¦   +-- geo_service.py        # (Mr Openx)
¦   +-- core/
¦   ¦   +-- security.py           # JWT utils (tunjipaul)
¦   ¦   +-- websocket.py          # WS manager (tunjipaul)
¦   ¦   +-- celery_app.py         # Task queue (tunjipaul)
¦   +-- utils/
¦       +-- response.py           # Standard response wrapper (tunjipaul)
¦       +-- pagination.py         # (tunjipaul)
¦       +-- file_upload.py        # (Mr Openx)
+-- alembic/                      # DB migrations (tunjipaul)
+-- tests/                        # (all three)
+-- Dockerfile                    # (tunjipaul)
+-- docker-compose.yml            # (tunjipaul)
+-- requirements.txt              # (tunjipaul)


3. Team Assignments

tunjipaul
Foundation & Auth Lead - Backend Core
tunjipaul owns the entire project foundation. Nothing else can start until your work on Session 1 (below) is complete and pushed. You are also responsible for Docker, deployment, and the AI pipeline bridge.

tunjipaul - Endpoint Responsibilities
Endpoint GroupRoutesAuth (Public)POST /register, /login, /logout, /refresh-token, /forgot-password, /reset-password, /verify-email, /verify-phone, /resend-otpConsumer - ProfileGET/PUT /consumer/profile, PATCH avatar, DELETE account, GET statsConsumer - ScanningPOST /scan, /scan/upload, /scan/analyze, GET /scan/result/:id, POST /scan/confirmConsumer - Scan HistoryGET /scans, /scans/recent, /scans/:id, DELETE /scans/clear, /scans/:id, GET /scans/filter, /scans/statsConsumer - NotificationsGET /notifications, PATCH /read, DELETE /:id, GET/PUT /notifications/settingsConsumer - SettingsGET /settings, PUT /language, /location, /privacy, GET/DELETE /settings/dataWebSocketWS /ws/notifications, WS /ws/company/:id, WS /ws/nafdac
tunjipaul - Hour-by-Hour Timeline
TimeTaskDeliverable / Notes08:00Repo setupInit GitHub repo. Add all teammates as collaborators. Push base folder structure, .env.example, requirements.txt, docker-compose.yml (Postgres + PostGIS + Redis). EVERYONE PULLS THIS FIRST.08:30DB + base modelsWrite database.py (async SQLAlchemy). Write ALL models (user, session, otp, company stub, product stub, scan, report stub, alert stub, analytics stub). Run Alembic init + first migration. This unblocks Mr Openx and Barrister Femi.09:30Core utilitiesWrite utils/response.py (success_response, error_response, paginated_response). Write core/security.py (JWT encode/decode, bcrypt). Write dependencies.py (get_current_user, require_role). Write utils/pagination.py. PUSH - this unblocks all route work.10:15Auth routesBuild routers/auth.py: register, login, logout, refresh-token, forgot-password, reset-password, verify-email, verify-phone, resend-otp. Test all endpoints with Swagger.11:30Consumer routesBuild routers/consumer.py: profile CRUD, scan submission (POST /scan creates pending record and fires Celery task), scan history, scan result polling, notifications, settings.13:00Lunch break30 minutes. Sync with team in group chat - share what's done, flag any blockers.13:30AI pipeline bridgeBuild services/ai_service.py: Celery task that calls A1 (visual), A2 (OCR), A3 (regulatory), A4 (fusion) over HTTP. On completion, update scan.status and trigger alert generation. Connect WebSocket manager to push result to user.15:00WebSocket managerBuild core/websocket.py - ConnectionManager class for WS /ws/notifications, /ws/company/:id, /ws/nafdac. Wire into main.py.16:00Docker + deployFinalize Dockerfile. Ensure docker-compose up runs all services cleanly. Test full scan flow end-to-end. Fix any integration bugs.17:30Demo dry runRun demo scenario: scan authentic product ? result, scan counterfeit ? result, confirm alert appears on WS. Confirm Mr Openx and Barrister Femi routes are all live.


Mr Openx
Company & Evidence Lead - Business Layer
Mr Openx owns all company-facing features including the product registry, reports, evidence vault, and heat map data layer. Wait for tunjipaul to push the base models and utils before starting (approx. 09:30). You will be ready to push your first routes by 11:00.

Mr Openx - Endpoint Responsibilities
Endpoint GroupRoutesCompany - Auth & ProfilePOST /company/register, /login, /verify, GET /status, POST /resend-verification, GET/PUT /profile, PATCH /logoCompany - Team & BillingGET/POST /team, PUT/DELETE /team/:userId, GET/PUT /billing, GET/PUT /subscriptionCompany - DashboardGET /dashboard, /dashboard/kpi, /dashboard/trends, /dashboard/states, /dashboard/recent-alerts, /dashboard/quick-statsCompany - ProductsGET/POST /products, GET/PUT/DELETE /products/:id, POST /products/upload, GET /products/categories, /products/statsCompany - Reports & AlertsGET /reports, /reports/:id, /reports/filter, /reports/stats, PATCH /reports/:id/status, POST /reports/export, GET /alerts, PATCH /alerts/:id/read, /alerts/read-allCompany - Evidence VaultGET /evidence, /evidence/:caseId, /evidence/:caseId/files, POST /evidence/:caseId/download, /evidence/:caseId/zip, GET /evidence/statsCompany - HeatmapGET /heatmap, /heatmap/regions, /heatmap/coordinates, /heatmap/filter, /heatmap/exportCompany - Settings & API KeysGET/PUT /settings/notifications, /settings/security, /settings/api, GET/POST /settings/api-keys, DELETE /settings/api-keys/:id, PUT /settings/webhooks, POST /settings/test-webhook, DELETE /settings/accountFile Upload UtilitiesPOST /upload/image, /upload/images, /upload/receipt, DELETE /upload/:fileId
Mr Openx - Hour-by-Hour Timeline
TimeTaskDeliverable / Notes08:00Pull repoClone tunjipaul's repo. Read the schema PDFs carefully. Set up your local Python venv. Do NOT push any code yet - wait for tunjipaul's base models.09:00Prep workWrite your Pydantic schemas in schemas/company.py while you wait for the base models. Cover: CompanyCreate, CompanyProfile, ProductCreate, ProductUpdate, ReportFilter, EvidenceResponse.09:30Pull models, start routestunjipaul pushes models + utils. Pull immediately. Begin routers/company.py: company registration, login, profile, team management. Use require_role('company_admin') from dependencies.py.10:30Products & file uploadBuild the full product registry CRUD. Build utils/file_upload.py (handles image upload to Cloudinary/S3, returns URL). Connect to POST /products/upload.11:30Reports & alertsBuild report viewing, filtering, status update, and CSV/PDF export. Build alert reading endpoints. Build services/report_service.py business logic.13:00Lunch break30 minutes. Check group chat. Confirm with tunjipaul that alert generation from scans is wiring up to your alert table correctly.13:30Evidence vaultBuild evidence case endpoints. Implement ZIP bundle creation using Python's zipfile module. Build the case file download endpoint.14:30Heatmap & geo dataBuild services/geo_service.py using PostGIS spatial queries to return coordinate clusters, region breakdowns, and risk levels for the dashboard map. Wire into /heatmap routes.15:30Dashboard + API keysBuild the 6 dashboard KPI endpoints (aggregate DB queries). Build API key generation (use secrets.token_hex(32)). Build webhook settings.16:30Test + polishTest all company routes in Swagger. Fix any 422 validation errors. Confirm heatmap returns valid GeoJSON coordinates. Push final code.


Barrister Femi
NAFDAC & Analytics Lead - Regulatory Layer
Barrister Femi owns everything regulatory - NAFDAC officer management, national dashboard, case and vendor tracking, analytics, enforcement actions, and all shared verification endpoints. Also waits for tunjipaul's push at 09:30.

Barrister Femi - Endpoint Responsibilities
Endpoint GroupRoutesNAFDAC - Auth & OfficersPOST /nafdac/login, POST/GET /nafdac/officers, PUT/DELETE /officers/:id, GET/PUT /nafdac/permissionsNAFDAC - Company MgmtGET /companies, /companies/pending, /companies/:id, POST /companies/:id/verify, /reject, PUT /suspend, /activate, DELETE /:id, GET /companies/statsNAFDAC - National DashboardGET /nafdac/dashboard, /dashboard/stats, /dashboard/heatmap, /dashboard/live-alerts, /dashboard/regions, /dashboard/trendsNAFDAC - AlertsGET /nafdac/alerts, /alerts/critical, /alerts/:id, PATCH /alerts/:id/acknowledge, /resolve, POST /bulk-acknowledge, GET /alerts/stats, /alerts/exportNAFDAC - Cases & EvidenceGET /cases, /cases/:id, /cases/:id/evidence, POST /cases/:id/assign, /update-status, /export, GET /cases/stats, /cases/searchNAFDAC - Vendor TrackingGET /vendors, /vendors/high-risk, /vendors/recurring, /vendors/:id, POST /vendors/:id/blacklist, /investigate, GET /vendors/export, /vendors/statsNAFDAC - AnalyticsGET /analytics/categories, /trends, /regions, /timeline, POST /analytics/export, GET /analytics/predictions, /hotspotsNAFDAC - Export SystemGET /export, POST /export/reports, /cases, /vendors, /analytics, GET /export/history, /export/download/:exportIdNAFDAC - EnforcementPOST/GET /enforcement/raids, PUT /raids/:id, POST /enforcement/notices, GET /enforcement/history, POST /enforcement/seizuresNAFDAC - NotificationsGET /nafdac/notifications, POST /notifications/broadcast, /notifications/company/:id, GET/PUT /notifications/settingsNAFDAC - Settings & ConfigGET/PUT /nafdac/settings, GET/PUT /settings/risk-levels, GET/POST/PUT/DELETE /settings/categories, GET /settings/audit-logsShared - VerificationGET /verify/nafdac/:number, /verify/batch/:number, POST /verify/image, GET /verify/product/:idShared - LocationGET /location/states, /location/cities/:state, POST /location/reverse-geocode
Barrister Femi - Hour-by-Hour Timeline
TimeTaskDeliverable / Notes08:00Pull repo + studyClone repo. Study the NAFDAC PDF endpoints and schema tables: alerts, hotspots, vendor_locations, analytics_daily, analytics_categories, analytics_regions, audit_logs.09:00Write schemasWrite schemas/nafdac.py: OfficerCreate, CaseResponse, AlertAcknowledge, VendorBlacklist, EnforcementRaid, AnalyticsFilter, ExportRequest. Also write the Nigerian states lookup seeder.09:30Pull + start routesPull tunjipaul's push. Start routers/nafdac.py. Build NAFDAC auth (login), officer CRUD, company management endpoints (verify, reject, suspend, activate). Use require_role('nafdac_admin', 'nafdac_officer').10:30National dashboardBuild the 6 dashboard endpoints. These are DB aggregate queries: COUNT scans by status, GROUP BY state, latest alerts feed, trend data over date ranges. Optimise with analytics_daily table.11:30Alerts & casesBuild NAFDAC alert management (acknowledge, resolve, bulk-acknowledge, export). Build cases & evidence endpoints, case assignment to officers, case status updates.13:00Lunch break30 minutes. Check with Mr Openx - confirm the alert records he writes are visible in your NAFDAC alerts feed.13:30Vendor trackingBuild vendor_locations CRUD. Implement blacklist (sets is_blacklisted=True), high-risk query (risk_level IN critical, high), recurring query (report_count >= threshold). Build services/notification_service.py.14:30Analytics endpointsBuild all 7 analytics routes. Pull from analytics_daily, analytics_categories, analytics_regions. The /hotspots route uses PostGIS ST_ClusterWithin on the hotspots table. /predictions can return mocked trend data for demo.15:30Export + enforcementBuild the export system: queue exports as background tasks, save to file, return download URL. Build enforcement endpoints (raids, seizures, notices) - these are simple POST-to-DB operations.16:30Shared routes + auditBuild routers/shared.py: NAFDAC number verification (query products table), batch number check, product image verify (calls AI service stub), location services (query nigerian_states table). Build audit log viewer endpoint.

4. Shared Contracts (Everyone Must Follow)
These rules prevent merge conflicts and ensure the mobile team can integrate cleanly.

Standard Response Format - utils/response.py
Every route in every router must return one of these three formats. No exceptions.

# Success
{ "success": true, "data": {}, "message": "Operation successful", "timestamp": "..." }

# Error
{ "success": false, "error": { "code": "ERROR_CODE", "message": "...", "details": {} }, "timestamp": "..." }

# Paginated
{ "success": true, "data": [], "pagination": { "page": 1, "limit": 20, "total": 100, "pages": 5 } }

Git Workflow
• tunjipaul works on main/dev branch. Mr Openx works on branch: feature/company. Barrister Femi works on branch: feature/nafdac
• Every push must include a short commit message: e.g. feat(company): add product registry CRUD
• No one merges to main without running python -m pytest tests/ first
• Merge order: tunjipaul merges first, then Mr Openx, then Barrister Femi

Environment Variables - .env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/sabilens
REDIS_URL=redis://localhost:6379
SECRET_KEY=your_jwt_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30
CLOUDINARY_URL=cloudinary://...
AI_VISUAL_ENDPOINT=http://ai-service:8001/visual
AI_OCR_ENDPOINT=http://ai-service:8002/ocr
AI_REGULATORY_ENDPOINT=http://ai-service:8003/regulatory
AI_FUSION_ENDPOINT=http://ai-service:8004/fusion


5. Day-End Demo Checklist
Every item below must work before the demo. Run through these in order at 17:30.

#Demo StepEndpointOwner1Consumer scans product - backend returns scan_id instantlyPOST /api/consumer/scantunjipaul2Celery AI task completes - scan result updated to authentic/fakeGET /api/consumer/scan/result/:idtunjipaul3WebSocket pushes result to consumer app in real-timeWS /ws/notificationstunjipaul4Company dashboard shows new alert for counterfeit reportGET /api/company/alertsMr Openx5Heatmap returns GPS coordinates of fake product locationGET /api/company/heatmap/coordinatesMr Openx6NAFDAC live-alerts feed shows counterfeit flagged in real-timeGET /api/nafdac/dashboard/live-alertsBarrister Femi7NAFDAC acknowledges and resolves the alertPATCH /api/nafdac/alerts/:id/resolveBarrister Femi8NAFDAC number verification returns correct product or mismatchGET /api/verify/nafdac/:numberBarrister Femi

6. Quick Setup Commands

# Clone and setup
git clone https://github.com/YOUR_REPO/sabilens-backend.git
cd sabilens-backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Start infrastructure
docker-compose up -d   # starts Postgres + PostGIS + Redis

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start Celery worker (separate terminal)
celery -A app.core.celery_app worker --loglevel=info

# View Swagger docs
http://localhost:8000/docs

Build it. Ship it. Win it.
tunjipaul  •  Mr Openx  •  Barrister Femi
SabiLens Backend - Developer READMEv1.0 - 1-Day Sprint
SabiLens | Confidential - Team Use Only	Page 

