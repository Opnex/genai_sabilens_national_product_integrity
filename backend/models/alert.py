"""Alert and notification models"""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, Boolean, TEXT, Index, Enum as SQLEnum
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()


class AlertType(str, enum.Enum):
    COUNTERFEIT = "counterfeit"
    SUSPICIOUS = "suspicious"
    BULK = "bulk"
    RECURRING = "recurring"


class Severity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class NotificationType(str, enum.Enum):
    SCAN_RESULT = "scan_result"
    REPORT_UPDATE = "report_update"
    ALERT = "alert"
    SYSTEM = "system"
    ACHIEVEMENT = "achievement"


class NotificationChannel(str, enum.Enum):
    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"


class Alert(Base):
    """Alerts table (for companies and NAFDAC)"""
    __tablename__ = "alerts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    report_id = Column(String(36))  # FK to reports
    company_id = Column(String(36))  # FK to companies
    alert_type = Column(SQLEnum(AlertType))
    severity = Column(SQLEnum(Severity))
    title = Column(String(255), nullable=False)
    message = Column(TEXT, nullable=False)
    alert_data = Column(String)  # JSONB - renamed from metadata
    is_read = Column(Boolean, default=False)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(36))  # FK to users
    acknowledged_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index("idx_alerts_company", "company_id"),
        Index("idx_alerts_type", "alert_type"),
        Index("idx_alerts_severity", "severity"),
        Index("idx_alerts_created", "created_at"),
    )


class Notification(Base):
    """Notifications table (for users)"""
    __tablename__ = "notifications"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), nullable=False)  # FK to users
    notification_type = Column(SQLEnum(NotificationType))
    title = Column(String(255), nullable=False)
    message = Column(TEXT, nullable=False)
    data = Column(String)  # JSONB
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index("idx_notifications_user", "user_id"),
        Index("idx_notifications_read", "is_read"),
    )


class NotificationPreference(Base):
    """User notification preferences"""
    __tablename__ = "notification_preferences"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), nullable=False, unique=True)  # FK to users
    notification_type = Column(String(50), nullable=False)
    channel = Column(SQLEnum(NotificationChannel))
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
