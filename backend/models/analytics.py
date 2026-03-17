"""Geospatial and analytics models"""
from datetime import datetime, date
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, Date, Integer, Numeric, Boolean, TEXT, Index, Enum as SQLEnum
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()


class RiskLevel(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class Hotspot(Base):
    """Counterfeit hotspots"""
    __tablename__ = "hotspots"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    location = Column(String, nullable=False)  # GEOGRAPHY(POINT)
    region_name = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100), default="Nigeria")
    report_count = Column(Integer, default=0)
    severity_score = Column(Numeric(5, 2))
    risk_level = Column(SQLEnum(RiskLevel))
    last_updated = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index("idx_hotspots_risk", "risk_level"),
    )


class VendorLocation(Base):
    """Vendor locations (where counterfeits were purchased)"""
    __tablename__ = "vendor_locations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    report_id = Column(String(36))  # FK to reports
    vendor_name = Column(String(255))
    location = Column(String, nullable=False)  # GEOGRAPHY(POINT)
    address = Column(TEXT)
    city = Column(String(100))
    state = Column(String(100))
    report_count = Column(Integer, default=1)
    risk_level = Column(SQLEnum(RiskLevel), default=RiskLevel.UNKNOWN)
    is_blacklisted = Column(Boolean, default=False)
    blacklisted_at = Column(DateTime)
    blacklisted_by = Column(String(36))  # FK to users
    last_reported_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index("idx_vendors_risk", "risk_level"),
        Index("idx_vendors_blacklisted", "is_blacklisted"),
    )


class AnalyticsDaily(Base):
    """Daily analytics aggregates"""
    __tablename__ = "analytics_daily"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    date = Column(Date, nullable=False, unique=True)
    total_scans = Column(Integer, default=0)
    authentic_scans = Column(Integer, default=0)
    suspicious_scans = Column(Integer, default=0)
    counterfeit_scans = Column(Integer, default=0)
    total_reports = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)
    unique_companies = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())


class AnalyticsCategory(Base):
    """Category analytics"""
    __tablename__ = "analytics_categories"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    category_id = Column(String(36))  # FK to product_categories
    category_name = Column(String(100))
    period = Column(String(20))  # daily, weekly, monthly, quarterly
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    scan_count = Column(Integer, default=0)
    counterfeit_count = Column(Integer, default=0)
    suspicious_count = Column(Integer, default=0)
    authentic_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())


class AnalyticsRegion(Base):
    """Regional analytics"""
    __tablename__ = "analytics_regions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    state = Column(String(100), nullable=False)
    city = Column(String(100))
    period = Column(String(20))  # daily, weekly, monthly, quarterly
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    scan_count = Column(Integer, default=0)
    counterfeit_count = Column(Integer, default=0)
    risk_score = Column(Numeric(5, 2))
    created_at = Column(DateTime, default=func.now())


class NigerianState(Base):
    """Nigerian states lookup table"""
    __tablename__ = "nigerian_states"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    capital = Column(String(100))
    region = Column(String(50))


class Language(Base):
    """Languages lookup table"""
    __tablename__ = "languages"
    
    id = Column(Integer, primary_key=True)
    code = Column(String(10), nullable=False, unique=True)
    name = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)


class AuditLog(Base):
    """Audit logs (for compliance)"""
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36))  # FK to users
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50))
    entity_id = Column(String(36))
    old_data = Column(String)  # JSONB
    new_data = Column(String)  # JSONB
    ip_address = Column(String(50))
    user_agent = Column(TEXT)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index("idx_audit_user", "user_id"),
        Index("idx_audit_entity", "entity_type", "entity_id"),
        Index("idx_audit_created", "created_at"),
    )


class SystemLog(Base):
    """System logs"""
    __tablename__ = "system_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    log_level = Column(String(20))  # debug, info, warning, error, critical
    component = Column(String(100))
    message = Column(TEXT)
    metadata_json = Column("metadata", String)  # JSONB
    created_at = Column(DateTime, default=func.now())

