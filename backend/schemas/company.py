"""Company request and response schemas"""
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date


class CompanyRegistrationRequest(BaseModel):
    """Company registration request"""
    name: str
    registration_number: str
    email: EmailStr
    phone: str
    address: str
    city: str
    state: str
    website: Optional[str] = None
    password: str = Field(..., min_length=8)


class CompanyLoginRequest(BaseModel):
    """Company login request"""
    email: EmailStr
    password: str


class CompanyProfileResponse(BaseModel):
    """Company profile response"""
    id: str
    name: str
    registration_number: str
    email: str
    phone: str
    address: str
    city: str
    state: str
    country: str
    logo_url: Optional[str] = None
    website: Optional[str] = None
    status: str
    subscription_tier: str
    verified_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProductCreateRequest(BaseModel):
    """Create product request"""
    name: str
    description: Optional[str] = None
    category_id: Optional[str] = None
    nafdac_number: str
    batch_number: Optional[str] = None
    manufacturer_name: str
    manufacturing_date: Optional[date] = None
    expiry_date: Optional[date] = None
    ingredients: Optional[str] = None
    warnings: Optional[str] = None


class ProductResponse(BaseModel):
    """Product response"""
    id: str
    company_id: str
    name: str
    description: Optional[str] = None
    category_id: Optional[str] = None
    nafdac_number: str
    batch_number: Optional[str] = None
    manufacturer_name: str
    manufacturing_date: Optional[date] = None
    expiry_date: Optional[date] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Products list response"""
    products: List[ProductResponse]
    total: int
    page: int
    limit: int


class ProductStatsResponse(BaseModel):
    """Product statistics"""
    total_products: int
    active_products: int
    pending_products: int
    expired_products: int
    discontinued_products: int


class ReportResponse(BaseModel):
    """Company report response"""
    id: str
    scan_id: str
    user_id: str
    product_id: Optional[str] = None
    report_status: str
    severity: Optional[str] = None
    purchase_channel: str
    price_paid: Optional[float] = None
    location_name: Optional[str] = None
    reported_at: datetime
    resolved_at: Optional[datetime] = None


class ReportListResponse(BaseModel):
    """Reports list response"""
    reports: List[ReportResponse]
    total: int
    page: int
    limit: int


class ReportStatsResponse(BaseModel):
    """Report statistics"""
    total_reports: int
    pending_reports: int
    verified_reports: int
    investigating_reports: int
    resolved_reports: int
    critical_severity: int
    high_severity: int


class AlertResponse(BaseModel):
    """Alert response"""
    id: str
    report_id: Optional[str] = None
    alert_type: str
    severity: str
    title: str
    message: str
    is_read: bool
    is_acknowledged: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    """Alerts list response"""
    alerts: List[AlertResponse]
    total: int
    unread_count: int


class DashboardTrendsResponse(BaseModel):
    """Dashboard trends data"""
    scans_trend: List[dict]
    reports_trend: List[dict]
    period: str

class StateStatsResponse(BaseModel):
    """Stats per state"""
    state: str
    scan_count: int
    counterfeit_count: int
    risk_level: str

class DashboardStatesResponse(BaseModel):
    """Dashboard states breakdown"""
    states: List[StateStatsResponse]

class DashboardKPIResponse(BaseModel):
    """Dashboard KPI cards"""
    total_scans_month: int
    authentic_count: int
    suspicious_count: int
    counterfeit_count: int
    alert_count: int
    revenue_month: float
    top_threat_state: str
    recent_alerts: List[AlertResponse]

class EvidenceFileResponse(BaseModel):
    """Evidence file detail"""
    id: str
    file_url: str
    file_type: str
    file_size: int
    uploaded_at: datetime

class EvidenceCaseResponse(BaseModel):
    """Evidence for a specific case"""
    case_id: str
    files: List[EvidenceFileResponse]
    zip_url: Optional[str] = None

class EvidenceVaultResponse(BaseModel):
    """Evidence vault overview"""
    files: List[EvidenceFileResponse]
    total: int
    stats: dict


class HeatmapCoordinateResponse(BaseModel):
    """Heatmap coordinate"""
    id: str
    latitude: float
    longitude: float
    city: str
    state: str
    report_count: int
    risk_level: str


class HeatmapResponse(BaseModel):
    """Heatmap response"""
    coordinates: List[HeatmapCoordinateResponse]
    total_points: int
    center_latitude: float
    center_longitude: float


class TeamMemberResponse(BaseModel):
    """Team member response"""
    id: str
    email: str
    phone: str
    first_name: str
    last_name: str
    role: str
    status: str
    joined_at: datetime

    class Config:
        from_attributes = True


class TeamListResponse(BaseModel):
    """Team list response"""
    members: List[TeamMemberResponse]
    total: int


class APIKeyResponse(BaseModel):
    """API key response"""
    id: str
    name: str
    api_key: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool
    last_used_at: Optional[datetime] = None


class APIKeyListResponse(BaseModel):
    """API keys list response"""
    keys: List[APIKeyResponse]
    total: int


class SubscriptionResponse(BaseModel):
    """Subscription response"""
    id: str
    tier: str
    status: str
    current_plan_name: str
    max_scans_monthly: int
    scans_used_month: int
    expires_at: Optional[datetime] = None
    features: List[str]
