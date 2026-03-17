"""Report related models"""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, TEXT, Numeric, Index, Enum as SQLEnum, Integer
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    REJECTED = "rejected"

class Severity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class PurchaseChannel(str, enum.Enum):
    MARKET_STALL = "market_stall"
    ROADSIDE_VENDOR = "roadside_vendor"
    SUPERMARKET = "supermarket"
    SUPPLIER = "supplier"
    ONLINE = "online"
    OTHER = "other"

class Report(Base):
    """Counterfeit reports table"""
    __tablename__ = "reports"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    scan_id = Column(String(36), nullable=False)  # FK to scans
    user_id = Column(String(36), nullable=False)  # FK to users
    product_id = Column(String(36))  # FK to products
    company_id = Column(String(36))  # FK to companies
    report_status = Column(SQLEnum(ReportStatus), default=ReportStatus.PENDING)
    severity = Column(SQLEnum(Severity))
    purchase_channel = Column(SQLEnum(PurchaseChannel))
    purchase_channel_details = Column(TEXT)
    price_paid = Column(Numeric(10, 2))
    receipt_image_urls = Column(String)  # Array
    additional_comments = Column(TEXT)
    gps_location = Column(String)  # GEOGRAPHY(POINT)
    location_name = Column(String(255))
    reported_at = Column(DateTime, default=func.now())
    resolved_at = Column(DateTime)
    resolved_by = Column(String(36))  # FK to users
    resolution_notes = Column(TEXT)
    
    __table_args__ = (
        Index("idx_reports_scan", "scan_id"),
        Index("idx_reports_company", "company_id"),
        Index("idx_reports_status", "report_status"),
        Index("idx_reports_severity", "severity"),
    )

class ReportEvidence(Base):
    """Report evidence table"""
    __tablename__ = "report_evidence"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    report_id = Column(String(36), nullable=False)  # FK to reports
    evidence_type = Column(String(50))  # image, video, receipt, document
    file_url = Column(TEXT, nullable=False)
    file_size = Column(Integer)  # Integer
    mime_type = Column(String(100))
    uploaded_by = Column(String(36))  # FK to users
    created_at = Column(DateTime, default=func.now())
