"""Consumer request and response schemas"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.scan import ScanStatus
from app.models.report import ReportStatus, Severity, PurchaseChannel


class ScanCreateRequest(BaseModel):
    """Create scan request"""
    product_name: Optional[str] = None
    category: Optional[str] = None
    manufacturer: Optional[str] = None
    nafdac_number: Optional[str] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[date] = None


class ScanUploadResponse(BaseModel):
    """Scan upload response"""
    file_url: str
    scan_id: str


class ScanResponse(BaseModel):
    """Scan response"""
    id: str
    user_id: str
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    category: Optional[str] = None
    manufacturer: Optional[str] = None
    nafdac_number: Optional[str] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[date] = None
    status: ScanStatus
    similarity_score: Optional[float] = None
    confidence_score: Optional[float] = None
    scan_image_urls: Optional[List[str]] = None
    location_name: Optional[str] = None
    scan_metadata: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ScanAnalysisResponse(BaseModel):
    """Scan analysis result"""
    scan_id: str
    status: ScanStatus
    confidence_score: float
    similarity_score: Optional[float] = None
    features_detected: Optional[dict] = None
    anomalies: Optional[dict] = None
    ocr_text: Optional[str] = None
    visual_fingerprint: Optional[dict] = None
    analysis_time_ms: Optional[int] = None
    verdict: str  # authentic, suspicious, fake
    message: str


class ScanConfirmRequest(BaseModel):
    """Confirm scan result request"""
    scan_id: str
    is_accurate: bool
    feedback: Optional[str] = None


class ScanFilterRequest(BaseModel):
    """Filter scans request"""
    status: Optional[ScanStatus] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    category: Optional[str] = None
    page: int = 1
    limit: int = 20


class ScanStatsResponse(BaseModel):
    """Scan statistics"""
    total_scans: int
    authentic_count: int
    suspicious_count: int
    fake_count: int
    pending_count: int


class ReportCreateRequest(BaseModel):
    """Create counterfeit report"""
    scan_id: str
    product_id: Optional[str] = None
    purchase_channel: PurchaseChannel
    purchase_channel_details: Optional[str] = None
    price_paid: Optional[float] = None
    additional_comments: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ReportUploadResponse(BaseModel):
    """Report evidence upload response"""
    file_url: str
    report_id: str


class ReportResponse(BaseModel):
    """Report response"""
    id: str
    scan_id: str
    user_id: str
    product_id: Optional[str] = None
    company_id: Optional[str] = None
    report_status: ReportStatus
    severity: Optional[Severity] = None
    purchase_channel: PurchaseChannel
    purchase_channel_details: Optional[str] = None
    price_paid: Optional[float] = None
    additional_comments: Optional[str] = None
    location_name: Optional[str] = None
    reported_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None

    class Config:
        from_attributes = True


class ReportHistoryResponse(BaseModel):
    """Report history response"""
    reports: List[ReportResponse]
    total: int
    page: int
    limit: int


class NotificationResponse(BaseModel):
    """Notification response"""
    id: str
    user_id: str
    notification_type: str
    title: str
    message: str
    data: Optional[dict] = None
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationsListResponse(BaseModel):
    """Notifications list response"""
    notifications: List[NotificationResponse]
    unread_count: int
    total: int


class MarkNotificationsReadRequest(BaseModel):
    """Mark notifications as read"""
    notification_ids: Optional[List[str]] = None  # If None, mark all as read
    all: bool = False  # If true, mark all as read


class NotificationSettingsResponse(BaseModel):
    """Notification preferences"""
    id: str
    user_id: str
    scan_result_email: bool = True
    scan_result_push: bool = True
    scan_result_sms: bool = False
    report_update_email: bool = True
    report_update_push: bool = True
    alert_email: bool = True
    alert_push: bool = True
    system_email: bool = False
    system_push: bool = True

    class Config:
        from_attributes = True


class NotificationSettingsUpdateRequest(BaseModel):
    """Update notification settings"""
    scan_result_email: Optional[bool] = None
    scan_result_push: Optional[bool] = None
    scan_result_sms: Optional[bool] = None
    report_update_email: Optional[bool] = None
    report_update_push: Optional[bool] = None
    alert_email: Optional[bool] = None
    alert_push: Optional[bool] = None
    system_email: Optional[bool] = None
    system_push: Optional[bool] = None


class SettingsResponse(BaseModel):
    """User settings response"""
    language: str = "en"
    location: Optional[str] = None
    privacy_scan_history: bool = True
    privacy_report_history: bool = True
    privacy_profile_public: bool = False

    class Config:
        from_attributes = True


class SettingsUpdateRequest(BaseModel):
    """Update settings"""
    language: Optional[str] = None
    location: Optional[str] = None
    privacy_scan_history: Optional[bool] = None
    privacy_report_history: Optional[bool] = None
    privacy_profile_public: Optional[bool] = None


class UserStatsResponse(BaseModel):
    """User statistics"""
    total_scans: int
    total_reports: int
    reports_verified: int
    scans_authentic: int
    scans_suspicious: int
    scans_fake: int
