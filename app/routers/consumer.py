"""Consumer routes"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.utils.response import success_response, paginated_response
from app.dependencies import get_current_user
from app.schemas.consumer import (
    ScanCreateRequest, ScanResponse, ScanAnalysisResponse, ScanConfirmRequest,
    ScanStatsResponse, ReportCreateRequest, ReportResponse, ReportHistoryResponse,
    NotificationResponse, NotificationsListResponse, MarkNotificationsReadRequest,
    NotificationSettingsResponse, NotificationSettingsUpdateRequest,
    SettingsResponse, SettingsUpdateRequest, UserStatsResponse
)
from app.schemas.auth import ProfileUpdateRequest, UserResponse
from app.services.scan_service import ScanService
from app.services.consumer_service import ConsumerService
from app.services.report_service import ReportService

router = APIRouter()

# --- Profile Management ---

@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user = Depends(get_current_user)):
    """Get consumer profile"""
    return success_response(UserResponse.from_orm(current_user))

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    req: ProfileUpdateRequest, 
    current_user = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """Update consumer profile"""
    user = await ConsumerService.update_profile(db, current_user.id, req)
    return success_response(UserResponse.from_orm(user))

@router.patch("/profile/avatar")
async def update_avatar(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload/update profile picture"""
    # In a real app, upload to S3/Cloudinary first
    avatar_url = f"https://storage.sabilens.com/avatars/{current_user.id}.png"
    user = await ConsumerService.update_avatar(db, current_user.id, avatar_url)
    return success_response({"profile_image_url": user.profile_image_url})

@router.delete("/profile")
async def delete_profile(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Delete consumer account"""
    await ConsumerService.delete_account(db, current_user.id)
    return success_response({"message": "Account deactivated successfully"})

@router.get("/stats", response_model=UserStatsResponse)
async def get_consumer_stats(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get consumer stats (reports, scans)"""
    stats = await ConsumerService.get_stats(db, current_user.id)
    return success_response(stats)

# --- Scan History ---

@router.get("/scans")
async def get_scans(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all scan history (paginated)"""
    scans, total = await ScanService.get_user_scans(db, current_user.id, limit, (page - 1) * limit)
    items = [ScanResponse.from_orm(s) for s in scans]
    return paginated_response(items, total, page, limit)

@router.get("/scans/recent")
async def get_recent_scans(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get recent scans (for home page)"""
    scans = await ScanService.get_recent_scans(db, current_user.id)
    return success_response([ScanResponse.from_orm(s) for s in scans])

@router.get("/scans/filter")
async def filter_scans(
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Filter scans (by status/date)"""
    scans, total = await ScanService.filter_scans(db, current_user.id, status, start_date, end_date, limit, (page-1)*limit)
    items = [ScanResponse.from_orm(s) for s in scans]
    return paginated_response(items, total, page, limit)

@router.get("/scans/stats", response_model=ScanStatsResponse)
async def get_user_scan_stats(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get scan statistics"""
    stats = await ScanService.get_scan_stats(db, current_user.id)
    return success_response(stats)

@router.get("/scans/{scanId}", response_model=ScanResponse)
async def get_scan_detail(scanId: str, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get specific scan details"""
    scan = await ScanService.get_scan(db, scanId)
    if not scan or scan.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Scan not found")
    return success_response(ScanResponse.from_orm(scan))

@router.delete("/scans/clear")
async def clear_scans(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Clear all scan history"""
    await ScanService.clear_history(db, current_user.id)
    return success_response({"message": "Scan history cleared"})

@router.delete("/scans/{scanId}")
async def delete_specific_scan(scanId: str, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Delete specific scan"""
    scan = await ScanService.get_scan(db, scanId)
    if not scan or scan.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Scan not found")
    await db.delete(scan)
    await db.commit()
    return success_response({"message": "Scan deleted"})

# --- Product Scanning ---

@router.post("/scan", status_code=201)
async def submit_scan(req: ScanCreateRequest, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Submit new product scan"""
    scan = await ScanService.create_scan(db, current_user.id, req)
    return success_response(ScanResponse.from_orm(scan), status_code=201)

@router.post("/scan/upload")
async def upload_scan_images(
    files: List[UploadFile] = File(...),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload product images"""
    urls = [f"https://storage.sabilens.com/scans/{current_user.id}/{f.filename}" for f in files]
    return success_response({"image_urls": urls})

@router.post("/scan/analyze/{scanId}")
async def analyze_product_scan(scanId: str, db: AsyncSession = Depends(get_db)):
    """AI analysis of scanned product"""
    # Mock analysis logic
    analysis = await ScanService.record_analysis(db, scanId, {
        "confidence_score": 0.85,
        "risk_level": "low",
        "recommendation": "Product appears authentic."
    })
    return success_response({"analysis_id": str(analysis.id), "status": "completed"})

@router.get("/scan/result/{scanId}")
async def get_scan_result(scanId: str, db: AsyncSession = Depends(get_db)):
    """Get scan result"""
    scan = await ScanService.get_scan(db, scanId)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return success_response({"scan_id": scan.id, "status": scan.status})

@router.post("/scan/confirm")
async def confirm_scan_accuracy(req: ScanConfirmRequest, db: AsyncSession = Depends(get_db)):
    """Confirm scan result accuracy"""
    return success_response({"message": "Feedback received"})

# --- Reporting ---

@router.post("/reports", status_code=201)
async def submit_report(req: ReportCreateRequest, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Submit counterfeit report"""
    report = await ReportService.create_report(db, current_user.id, req.scan_id, req.additional_comments)
    return success_response(ReportResponse.from_orm(report), status_code=201)

@router.post("/reports/upload")
async def upload_report_evidence(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """Upload receipt/evidence"""
    url = f"https://storage.sabilens.com/evidence/{file.filename}"
    return success_response({"file_url": url})

@router.get("/reports/history")
async def get_reports_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's report history"""
    reports, total = await ReportService.get_user_reports(db, current_user.id, limit, (page-1)*limit)
    items = [ReportResponse.from_orm(r) for r in reports]
    return paginated_response(items, total, page, limit)

@router.get("/reports/{reportId}", response_model=ReportResponse)
async def get_report_status(reportId: str, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get report status"""
    report = await ReportService.get_report(db, reportId)
    if not report or report.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Report not found")
    return success_response(ReportResponse.from_orm(report))

@router.put("/reports/{reportId}")
async def update_report(reportId: str, db: AsyncSession = Depends(get_db)):
    """Update report"""
    return success_response({"message": "Report updated"})

@router.delete("/reports/{reportId}")
async def withdraw_report(reportId: str, db: AsyncSession = Depends(get_db)):
    """Withdraw report"""
    return success_response({"message": "Report withdrawn"})

# --- Notifications & Settings ---

@router.get("/notifications")
async def get_notifications(db: AsyncSession = Depends(get_db)):
    """Get all notifications"""
    return success_response({"notifications": []})

@router.patch("/notifications/read")
async def mark_notifications_read(req: MarkNotificationsReadRequest, db: AsyncSession = Depends(get_db)):
    """Mark notifications as read"""
    return success_response({"message": "Marked as read"})

@router.delete("/notifications/{id}")
async def delete_notification(id: str, db: AsyncSession = Depends(get_db)):
    """Delete notification"""
    return success_response({"message": "Deleted"})

@router.get("/notifications/settings")
async def get_notification_settings(db: AsyncSession = Depends(get_db)):
    """Get notification preferences"""
    return success_response({})

@router.put("/notifications/settings")
async def update_notification_settings(req: NotificationSettingsUpdateRequest, db: AsyncSession = Depends(get_db)):
    """Update notification preferences"""
    return success_response({"message": "Settings updated"})

@router.get("/settings", response_model=SettingsResponse)
async def get_all_settings(current_user = Depends(get_current_user)):
    """Get all settings"""
    return success_response(SettingsResponse(language=current_user.preferred_language))

@router.put("/settings/language")
async def update_language(lang: str, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Update preferred language"""
    current_user.preferred_language = lang
    await db.commit()
    return success_response({"message": "Language updated"})

@router.put("/settings/location")
async def update_location_prefs(db: AsyncSession = Depends(get_db)):
    """Update location preferences"""
    return success_response({"message": "Location preferences updated"})

@router.get("/settings/data")
async def request_data_export(db: AsyncSession = Depends(get_db)):
    """Request data export"""
    return success_response({"message": "Data export requested"})

@router.delete("/settings/data")
async def delete_user_data(db: AsyncSession = Depends(get_db)):
    """Delete user data"""
    return success_response({"message": "Data deletion scheduled"})

