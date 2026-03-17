"""User and authentication models"""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, Boolean, DateTime, TEXT, Index, Enum as SQLEnum
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    """User roles"""
    CONSUMER = "consumer"
    COMPANY_ADMIN = "company_admin"
    NAFDAC_OFFICER = "nafdac_officer"
    NAFDAC_ADMIN = "nafdac_admin"


class UserStatus(str, enum.Enum):
    """User status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"
    DELETED = "deleted"


class User(Base):
    """Users table"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email = Column(String(255), unique=True, nullable=True)
    phone = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.CONSUMER)
    status = Column(SQLEnum(UserStatus), nullable=False, default=UserStatus.ACTIVE)
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    profile_image_url = Column(TEXT)
    preferred_language = Column(String(10), default="en")
    last_login = Column(DateTime)
    company_id = Column(String(36))  # FK to companies
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index("idx_users_email", "email", postgresql_where=deleted_at.is_(None)),
        Index("idx_users_phone", "phone", postgresql_where=deleted_at.is_(None)),
        Index("idx_users_role", "role"),
    )


class Session(Base):
    """Sessions table"""
    __tablename__ = "sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), nullable=False)  # FK to users
    refresh_token = Column(TEXT, nullable=False)
    device_info = Column(String)  # JSONB
    ip_address = Column(String(50))
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index("idx_sessions_user_id", "user_id"),
        Index("idx_sessions_refresh_token", "refresh_token"),
    )


class OTPVerification(Base):
    """OTP verifications table"""
    __tablename__ = "otp_verifications"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36))  # FK to users
    phone = Column(String(20))
    email = Column(String(255))
    otp_code = Column(String(6), nullable=False)
    purpose = Column(String(50))  # registration, login, password_reset, phone_verification
    expires_at = Column(DateTime, nullable=False)
    verified_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index("idx_otp_phone", "phone"),
        Index("idx_otp_email", "email"),
    )
