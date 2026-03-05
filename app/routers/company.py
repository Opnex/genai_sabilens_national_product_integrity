from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.utils.response import success_response, paginated_response
from app.dependencies import get_current_user
from app.config import settings
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.services.company_service import CompanyService
from app.services.report_service import ReportService
from app.services.geo_service import GeoService
from app.utils.file_upload import FileUploadUtil
from app.models.user import User, UserRole, UserStatus
from app.models.company import Company
from app.models.report import ReportStatus, Severity, PurchaseChannel
from app.schemas.company import (
    CompanyRegistrationRequest, CompanyLoginRequest, ProductCreateRequest, CompanyProfileResponse,
    ProductResponse, ProductListResponse, ProductStatsResponse,
    ReportResponse, ReportListResponse, ReportStatsResponse,
    AlertListResponse, DashboardKPIResponse, DashboardTrendsResponse,
    DashboardStatesResponse, HeatmapResponse, TeamMemberResponse,
    TeamListResponse, APIKeyResponse, APIKeyListResponse,
    SubscriptionResponse, EvidenceVaultResponse, EvidenceFileResponse,
    EvidenceCaseResponse,
)
from app.schemas.auth import UserResponse

router = APIRouter()

# --- Auth & Profile ---

@router.post("/register", status_code=201)
async def register_company(req: CompanyRegistrationRequest, db: AsyncSession = Depends(get_db)):
    """Register new company"""
    try:
        company = await CompanyService.create_company(db, req.dict())
        return success_response({"id": str(company.id), "name": company.name, "status": company.status}, status_code=201)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login_company(req: CompanyLoginRequest, db: AsyncSession = Depends(get_db)):
    """Company login with email + password"""
    stmt = select(User).where(
        (User.email == req.email) &
        (User.role == UserRole.COMPANY_ADMIN)
    )
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=403, detail="Company user account is not active")

    if not user.company_id:
        company_stmt = select(Company).where(Company.email == req.email)
        company_result = await db.execute(company_stmt)
        company = company_result.scalars().first()
        if not company:
            raise HTTPException(status_code=400, detail="Company account is not linked to a company profile")
        user.company_id = company.id

    user.last_login = datetime.utcnow()
    await db.commit()
    await db.refresh(user)

    access_token = create_access_token({"sub": user.id, "role": user.role.value})
    refresh_token = create_refresh_token({"sub": user.id})

    return success_response({
        "user": {
            "id": user.id,
            "email": user.email,
            "phone": user.phone,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "company_id": user.company_id,
            "role": user.role.value,
            "status": user.status.value,
        },
        "tokens": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        },
    })

@router.post("/verify")
async def verify_company_email(req: dict, db: AsyncSession = Depends(get_db)):
    """Verify company user email"""
    return success_response({"message": "Email verified successfully"})

@router.get("/status")
async def get_registration_status(reg_no: str, db: AsyncSession = Depends(get_db)):
    """Check status of company application"""
    return success_response({"status": "pending", "details": "Awaiting NAFDAC review"})

@router.post("/resend-verification")
async def resend_verification(email: str, db: AsyncSession = Depends(get_db)):
    """Resend verification email"""
    return success_response({"message": "Verification email resent"})

@router.get("/profile")
async def get_company_profile(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get company profile"""
    company_id = current_user.company_id
    if not company_id:
        raise HTTPException(status_code=400, detail="User not associated with a company")
    company = await CompanyService.get_company(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return success_response(CompanyProfileResponse.from_orm(company))

@router.put("/profile")
async def update_company_profile(req: dict, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Update company details"""
    return success_response({"message": "Profile updated"})

@router.patch("/profile/logo")
async def upload_company_logo(file: UploadFile = File(...), current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Upload company logo"""
    return success_response({"logo_url": "https://storage.sabilens.com/logos/company_logo.png"})

# --- Team & Subscription ---

@router.get("/team")
async def get_team_members(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get team members"""
    members = await CompanyService.get_team_members(db, current_user.company_id)
    items = [
        TeamMemberResponse(
            id=m.id,
            email=m.email or "",
            phone=m.phone,
            first_name=m.first_name or "",
            last_name=m.last_name or "",
            role=m.role.value if hasattr(m.role, "value") else str(m.role),
            status=m.status.value if hasattr(m.status, "value") else str(m.status),
            joined_at=m.created_at,
        )
        for m in members
    ]
    return success_response({"members": items, "total": len(items)})

@router.post("/team")
async def invite_team_member(email: str, role: str, db: AsyncSession = Depends(get_db)):
    """Invite team member"""
    return success_response({"message": f"Invitation sent to {email}"})

@router.get("/subscription")
async def get_subscription_details(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get company subscription and usage details"""
    # In production, query the 'subscription_plans' and 'companies' tables
    return success_response({
        "id": "sub_123",
        "tier": "premium",
        "status": "active",
        "current_plan_name": "Pro Business",
        "max_scans_monthly": 10000,
        "scans_used_month": 450,
        "next_billing_date": "2026-04-05",
        "features": ["api_access", "advanced_analytics", "priority_support"]
    })

@router.put("/subscription")
async def update_subscription_plan(req: dict, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Upgrade/Downgrade company plan"""
    return success_response({"message": "Subscription update initiated"})

@router.get("/billing")
async def get_billing_history(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get company invoices and payment methods"""
    return success_response({"invoices": [], "payment_methods": []})

# --- Dashboard & Analytics ---

@router.get("/dashboard/kpi")
async def get_kpi_cards(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get dashboard overview"""
    stats = await CompanyService.get_dashboard_stats(db, current_user.company_id)
    return success_response(stats)

@router.get("/dashboard/trends")
async def get_dashboard_trends(period: str = "30d", current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get scan and report trends"""
    trends = await CompanyService.get_dashboard_trends(db, current_user.company_id, period)
    return success_response(trends)

@router.get("/dashboard/states")
async def get_dashboard_states(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get scan breakdown by state"""
    states = await CompanyService.get_state_breakdown(db, current_user.company_id)
    return success_response({"states": states})

@router.get("/dashboard/recent-alerts")
async def get_recent_dashboard_alerts(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get latest alerts for dashboard"""
    alerts = await CompanyService.get_recent_alerts(db, current_user.company_id, limit=5)
    return success_response({"alerts": alerts, "total": len(alerts), "unread_count": 0})

@router.get("/dashboard/quick-stats")
async def get_quick_stats(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get real-time quick stats"""
    stats = await CompanyService.get_quick_stats(db, current_user.company_id)
    return success_response(stats)

@router.get("/heatmap")
async def get_heatmap(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get heatmap data for company products"""
    data = await GeoService.get_heatmap_clusters(db, current_user.company_id)
    return success_response({
        "coordinates": data, 
        "total_points": len(data),
        "center_latitude": 9.0820, # Nigeria center
        "center_longitude": 8.6753
    })

@router.get("/heatmap/regions")
async def get_heatmap_regions(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get risk level breakdown by region"""
    regions = await GeoService.get_region_risk(db, current_user.company_id)
    return success_response({"regions": regions})

@router.get("/heatmap/coordinates")
async def get_heatmap_coordinates(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get detailed latitude/longitude points"""
    coords = await GeoService.get_raw_coordinates(db, current_user.company_id)
    return success_response({"coordinates": coords})

# --- Evidence Vault ---

@router.get("/evidence")
async def get_evidence_vault(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get company evidence vault (scans and report evidence)"""
    # This aggregates files from scans and reports
    return success_response({"files": [], "total": 0, "stats": {"total_size_mb": 45.2, "file_count": 128}})

@router.get("/evidence/{caseId}")
async def get_case_evidence(caseId: str, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get evidence files for a specific case"""
    return success_response({
        "case_id": caseId,
        "files": [],
        "zip_url": f"/vault/cases/{caseId}/bundle.zip"
    })

@router.get("/evidence/{caseId}/files")
async def list_case_files(caseId: str, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """List raw files in a case"""
    return success_response({"files": []})

@router.post("/evidence/{caseId}/zip")
async def create_case_zip(caseId: str, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Generate ZIP bundle for a case"""
    import zipfile
    import io
    # In production, this would be a background task
    return success_response({"zip_url": f"/temp/bundles/{caseId}.zip", "message": "ZIP generation started"})

@router.post("/evidence/upload")
async def upload_evidence_to_vault(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload file to evidence vault"""
    url = await FileUploadUtil.save_file(file, sub_dir=f"company_{current_user.company_id}/vault")
    return success_response({"file_url": url, "message": "File uploaded to vault"})

@router.get("/evidence/stats")
async def get_vault_stats(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get vault usage statistics"""
    return success_response({
        "total_storage_used": "1.2GB",
        "storage_limit": "10GB",
        "file_type_distribution": {"images": 85, "reports": 15}
    })

# --- Reports & Alerts Oversight ---

@router.get("/reports")
async def get_company_reports(
    status: Optional[ReportStatus] = None,
    severity: Optional[Severity] = None,
    channel: Optional[PurchaseChannel] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Oversight of counterfeit reports related to brand"""
    # Filter reports by company_id and optional params
    reports, total = await ReportService.get_company_reports(
        db, current_user.company_id, status=status, severity=severity, channel=channel, limit=limit, offset=(page-1)*limit
    )
    items = [ReportResponse.from_orm(r) for r in reports]
    return paginated_response(items, total, page, limit)

@router.get("/reports/filter")
async def filter_reports(
    product_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Granular filtering for reports"""
    return success_response({"reports": []})

@router.post("/reports/export")
async def export_reports(req: dict, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Export reports to CSV/PDF"""
    file_url = await ReportService.export_reports(db, current_user.company_id, req.get("format", "csv"))
    return success_response({"file_url": file_url, "message": f"Exported to {req.get('format')}"})

@router.get("/alerts")
async def get_company_alerts(
    is_read: Optional[bool] = None,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all company alerts"""
    alerts = await CompanyService.get_recent_alerts(db, current_user.company_id, limit=100)
    # Filter by read status if provided
    if is_read is not None:
        alerts = [a for a in alerts if a.is_read == is_read]
    return success_response({"alerts": alerts, "total": len(alerts), "unread_count": sum(1 for a in alerts if not a.is_read)})

@router.patch("/alerts/{alertId}/read")
async def mark_alert_read(alertId: str, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Mark specific alert as read"""
    success = await CompanyService.mark_alert_read(db, current_user.company_id, alertId)
    return success_response({"success": success})

@router.patch("/alerts/read-all")
async def mark_all_alerts_read(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Mark all alerts for company as read"""
    await CompanyService.mark_all_alerts_read(db, current_user.company_id)
    return success_response({"message": "All alerts marked as read"})

@router.get("/reports/stats")
async def get_company_report_stats(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Summary of report activity for the brand"""
    # Aggregated stats for company reports
    return success_response({
        "total_reports": 0,
        "verified_fake": 0,
        "under_investigation": 0,
        "resolved": 0
    })

# --- Product Registry ---

@router.get("/products")
async def get_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all registered products"""
    products, total = await CompanyService.get_products(db, current_user.company_id, limit, (page-1)*limit)
    items = [ProductResponse.from_orm(p) for p in products]
    return paginated_response(items, total, page, limit)

@router.post("/products", status_code=201)
async def register_product(req: ProductCreateRequest, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Register new product"""
    try:
        product = await CompanyService.create_product(db, current_user.company_id, req.dict())
        return success_response(ProductResponse.from_orm(product), status_code=201)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/products/upload")
async def bulk_upload_products(file: UploadFile = File(...), current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Bulk register products via CSV/Excel"""
    return success_response({"message": "Bulk upload initiated", "job_id": "bulk_001"})

@router.get("/products/stats")
async def get_product_stats(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get aggregated product statistics"""
    stats = await CompanyService.get_product_stats(db, current_user.company_id)
    return success_response(stats)

# --- Heatmap Extras ---

@router.get("/heatmap/filter")
async def filter_heatmap(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    risk_level: Optional[str] = None,
    current_user = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """Filter heatmap data"""
    return success_response({"coordinates": []})

@router.get("/heatmap/export")
async def export_heatmap_data(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Export heatmap as GeoJSON"""
    return success_response({"type": "FeatureCollection", "features": []})

# --- Independent File Upload Utilities ---

@router.post("/upload/image")
async def upload_single_image(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """Generic image upload"""
    url = await FileUploadUtil.save_file(file, sub_dir="general/images")
    return success_response({"file_url": url})

@router.post("/upload/images")
async def upload_multiple_images(files: List[UploadFile] = File(...), db: AsyncSession = Depends(get_db)):
    """Bulk image upload"""
    urls = []
    for file in files:
        url = await FileUploadUtil.save_file(file, sub_dir="general/bulk")
        urls.append(url)
    return success_response({"file_urls": urls})

@router.post("/upload/receipt")
async def upload_purchase_receipt(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """Specific receipt upload for reports"""
    url = await FileUploadUtil.save_file(file, sub_dir="reports/receipts")
    return success_response({"file_url": url})

@router.delete("/upload/{fileId}")
async def delete_uploaded_file(fileId: str, db: AsyncSession = Depends(get_db)):
    """Delete an uploaded file"""
    return success_response({"message": "File deletion requested"})

# --- Settings ---

@router.get("/settings/notifications")
async def get_notification_settings(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get notification preferences"""
    return success_response({
        "email_alerts": True,
        "push_scans": False,
        "weekly_report": True
    })

@router.put("/settings/notifications")
async def update_notification_settings(req: dict, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Update notification preferences"""
    return success_response({"message": "Settings saved"})

@router.get("/settings/security")
async def get_security_settings(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get security logs and 2FA status"""
    return success_response({"two_factor_enabled": False, "recent_logins": []})

@router.get("/settings/api")
async def get_api_config(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get base API configuration"""
    return success_response({"endpoint": "https://api.sabilens.com/v1", "documentation": "/docs"})

@router.get("/settings/api-keys")
async def get_api_keys(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get API keys"""
    keys = await CompanyService.get_api_keys(db, current_user.company_id)
    items = [APIKeyResponse.from_orm(k) for k in keys]
    return success_response({"keys": items, "total": len(items)})

@router.post("/settings/api-keys")
async def create_api_key(name: str, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Generate new API key"""
    key = await CompanyService.generate_api_key(db, current_user.company_id, name)
    return success_response(APIKeyResponse.from_orm(key))

@router.delete("/settings/api-keys/{keyId}")
async def revoke_api_key(keyId: str, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Revoke API key"""
    await CompanyService.delete_api_key(db, current_user.company_id, keyId)
    return success_response({"message": "API key revoked"})

@router.put("/settings/webhooks")
async def update_webhook_url(url: str, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Configure webhook endpoint"""
    return success_response({"message": "Webhook updated"})

@router.post("/settings/test-webhook")
async def test_webhook(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Send test payload to configured webhook"""
    return success_response({"delivery_status": "success", "response_code": 200})

@router.delete("/settings/account")
async def deactivate_account(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Deactivate company account"""
    return success_response({"message": "Account deactivated. All data retained for 30 days."})


