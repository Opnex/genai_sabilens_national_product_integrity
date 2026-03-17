"""Scan and report models"""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, TEXT, Numeric, Date, Index, Enum as SQLEnum, Integer
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class ScanStatus(str, enum.Enum):
    AUTHENTIC = "authentic"
    CAUTION = "caution"
    FAKE = "fake"
    PENDING = "pending"

class Scan(Base):
    """Scans table"""
    __tablename__ = "scans"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), nullable=False)  # FK to users
    product_id = Column(String(36))  # FK to products
    product_name = Column(String(255))
    category = Column(String(100))
    manufacturer = Column(String(255))
    nafdac_number = Column(String(100))
    batch_number = Column(String(100))
    expiry_date = Column(Date)
    status = Column(SQLEnum(ScanStatus))
    similarity_score = Column(Numeric(5, 2))
    confidence_score = Column(Numeric(5, 2))
    scan_image_urls = Column(String)  # Array
    scan_location = Column(String)  # GEOGRAPHY(POINT)
    location_name = Column(String(255))
    scan_metadata = Column(String)  # JSONB
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index("idx_scans_user", "user_id"),
        Index("idx_scans_product", "product_id"),
        Index("idx_scans_status", "status"),
        Index("idx_scans_created", "created_at"),
    )

class ScanAnalysis(Base):
    """Scan analysis results (detailed AI output)"""
    __tablename__ = "scan_analyses"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    scan_id = Column(String(36), nullable=False)  # FK to scans
    ai_model_version = Column(String(50))
    features_detected = Column(String)  # JSONB
    anomalies = Column(String)  # JSONB
    ocr_text = Column(TEXT)
    visual_fingerprint = Column(String)  # JSONB
    analysis_time_ms = Column(Integer)  # Integer
    created_at = Column(DateTime, default=func.now())

# Note: Report, ReportStatus, PurchaseChannel, and ReportEvidence have been moved to backend/models/report.py
