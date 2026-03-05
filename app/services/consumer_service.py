"""Consumer logic service"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, desc

from app.models.user import User, UserStatus
from app.models.scan import Scan, ScanStatus
from app.models.report import Report
from app.schemas.auth import ProfileUpdateRequest
from app.schemas.consumer import UserStatsResponse

class ConsumerService:
    """Consumer management service"""

    @staticmethod
    async def update_profile(db: AsyncSession, user_id: str, req: ProfileUpdateRequest) -> User:
        """Update user profile"""
        stmt = update(User).where(User.id == user_id).values(
            **req.dict(exclude_unset=True),
            updated_at=datetime.utcnow()
        ).returning(User)
        result = await db.execute(stmt)
        user = result.scalars().first()
        await db.commit()
        return user

    @staticmethod
    async def update_avatar(db: AsyncSession, user_id: str, avatar_url: str) -> User:
        """Update user avatar"""
        user = await db.get(User, user_id)
        if not user:
            raise ValueError("User not found")
        user.profile_image_url = avatar_url
        user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def delete_account(db: AsyncSession, user_id: str) -> bool:
        """Soft delete user account"""
        user = await db.get(User, user_id)
        if not user:
            raise ValueError("User not found")
        user.status = UserStatus.DELETED
        user.deleted_at = datetime.utcnow()
        await db.commit()
        return True

    @staticmethod
    async def get_stats(db: AsyncSession, user_id: str) -> Dict[str, Any]:
        """Get consumer statistics"""
        # Count scans
        scan_stmt = select(func.count(Scan.id)).where(Scan.user_id == user_id)
        scan_result = await db.execute(scan_stmt)
        total_scans = scan_result.scalar() or 0

        # Count reports
        report_stmt = select(func.count(Report.id)).where(Report.user_id == user_id)
        report_result = await db.execute(report_stmt)
        total_reports = report_result.scalar() or 0

        # Authentic vs Fake scans
        authentic_stmt = select(func.count(Scan.id)).where((Scan.user_id == user_id) & (Scan.status == ScanStatus.AUTHENTIC))
        fake_stmt = select(func.count(Scan.id)).where((Scan.user_id == user_id) & (Scan.status == ScanStatus.FAKE))
        suspicious_stmt = select(func.count(Scan.id)).where((Scan.user_id == user_id) & (Scan.status == ScanStatus.CAUTION))

        authentic_count = (await db.execute(authentic_stmt)).scalar() or 0
        fake_count = (await db.execute(fake_stmt)).scalar() or 0
        suspicious_count = (await db.execute(suspicious_stmt)).scalar() or 0

        return {
            "total_scans": total_scans,
            "total_reports": total_reports,
            "reports_verified": 0, # Placeholder
            "scans_authentic": authentic_count,
            "scans_suspicious": suspicious_count,
            "scans_fake": fake_count
        }
