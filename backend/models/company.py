"""Company models"""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, Boolean, Numeric, TEXT, Index, Integer, Enum as SQLEnum
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()


class CompanyStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REJECTED = "rejected"


class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class Company(Base):
    """Companies table"""
    __tablename__ = "companies"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False)
    registration_number = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(TEXT)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100), default="Nigeria")
    logo_url = Column(TEXT)
    website = Column(String(255))
    status = Column(SQLEnum(CompanyStatus), default=CompanyStatus.PENDING)
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE)
    subscription_expires_at = Column(DateTime)
    verified_at = Column(DateTime)
    verified_by = Column(String(36))  # FK to users
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index("idx_companies_status", "status"),
        Index("idx_companies_registration", "registration_number"),
    )


class CompanySettings(Base):
    """Company settings table"""
    __tablename__ = "company_settings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    company_id = Column(String(36), nullable=False, unique=True)  # FK to companies
    notification_email = Column(Boolean, default=True)
    notification_alerts = Column(Boolean, default=True)
    notification_reports = Column(Boolean, default=True)
    auto_export_enabled = Column(Boolean, default=False)
    api_access_enabled = Column(Boolean, default=False)
    webhook_url = Column(TEXT)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class CompanyAPIKey(Base):
    """Company API keys table"""
    __tablename__ = "company_api_keys"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    company_id = Column(String(36), nullable=False)  # FK to companies
    api_key = Column(String(255), unique=True, nullable=False)
    api_secret = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    permissions = Column(String)  # JSONB
    last_used_at = Column(DateTime)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index("idx_api_keys_company", "company_id"),
    )


class SubscriptionPlan(Base):
    """Subscription plans table"""
    __tablename__ = "subscription_plans"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(100), nullable=False)
    tier = Column(SQLEnum(SubscriptionTier), unique=True, nullable=False)
    description = Column(TEXT)
    price_monthly = Column(Numeric(10, 2))
    price_annual = Column(Numeric(10, 2))
    features = Column(String)  # JSONB
    max_scans_monthly = Column(Integer)
    max_products = Column(Integer)
    max_team_members = Column(Integer)
    api_access = Column(Boolean, default=False)
    webhook_support = Column(Boolean, default=False)
    priority_support = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index("idx_subscription_plans_tier", "tier"),
    )


class WebhookLog(Base):
    """Webhook logs table"""
    __tablename__ = "webhook_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    company_id = Column(String(36), nullable=False)  # FK to companies
    webhook_url = Column(TEXT, nullable=False)
    event_type = Column(String(100))
    payload = Column(String)  # JSONB
    response_status = Column(Integer)
    response_body = Column(TEXT)
    retry_count = Column(Integer, default=0)
    last_retry_at = Column(DateTime)
    success = Column(Boolean, default=False)
    error_message = Column(TEXT)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index("idx_webhook_logs_company", "company_id"),
        Index("idx_webhook_logs_created", "created_at"),
    )
