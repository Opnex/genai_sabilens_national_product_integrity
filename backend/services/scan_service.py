"""Scan service"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from backend.models.scan import Scan, ScanAnalysis
from backend.models.user import User
from backend.models.product import Product


class ScanService:
    """Scan management service"""
    
    @staticmethod
    async def create_scan(db: AsyncSession, user_id: str, req: any) -> Scan:
        """Create new scan"""
        scan = Scan(
            user_id=user_id,
            product_id=req.product_id,
            image_url=req.image_url,
            barcode=req.barcode,
            latitude=req.latitude,
            longitude=req.longitude,
            location_text=req.location_text,
            status="pending",
            created_at=datetime.utcnow(),
        )
        db.add(scan)
        await db.commit()
        await db.refresh(scan)
        return scan
    
    
    @staticmethod
    async def get_scan(db: AsyncSession, scan_id: str) -> Optional[Scan]:
        """Get scan by ID"""
        return await db.get(Scan, scan_id)
    
    
    @staticmethod
    @staticmethod
    async def get_user_scans(db: AsyncSession, user_id: str, limit: int = 20, offset: int = 0) -> tuple[List[Scan], int]:
        """Get user's scan history"""
        stmt = select(Scan).where(Scan.user_id == user_id).order_by(desc(Scan.created_at)).limit(limit).offset(offset)
        result = await db.execute(stmt)
        scans = result.scalars().all()
        
        # Count total
        count_stmt = select(func.count()).select_from(Scan).where(Scan.user_id == user_id)
        count_result = await db.execute(count_stmt)
        total = count_result.scalar() or 0
        
        return scans, total
    
    
    @staticmethod
    async def update_scan_status(db: AsyncSession, scan_id: str, status: str) -> Scan:
        """Update scan status (pending -> analyzing -> authentic/caution/fake)"""
        scan = await db.get(Scan, scan_id)
        if not scan:
            raise ValueError("Scan not found")
        
        scan.status = status
        scan.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(scan)
        return scan
    
    
    @staticmethod
    async def record_analysis(db: AsyncSession, scan_id: str, analysis_data: dict) -> ScanAnalysis:
        """Record AI analysis results"""
        analysis = ScanAnalysis(
            scan_id=scan_id,
            confidence_score=analysis_data.get("confidence_score", 0.0),
            visual_analysis=analysis_data.get("visual_analysis"),
            ocr_analysis=analysis_data.get("ocr_analysis"),
            regulatory_check=analysis_data.get("regulatory_check"),
            fusion_result=analysis_data.get("fusion_result"),
            risk_level=analysis_data.get("risk_level"),
            recommendation=analysis_data.get("recommendation"),
            created_at=datetime.utcnow(),
        )
        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)
        return analysis
    @staticmethod
    async def get_recent_scans(db: AsyncSession, user_id: str, limit: int = 5) -> List[Scan]:
        """Get recent scans for home page"""
        stmt = select(Scan).where(Scan.user_id == user_id).order_by(desc(Scan.created_at)).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def clear_history(db: AsyncSession, user_id: str) -> bool:
        """Clear all scan history for a user"""
        stmt = delete(Scan).where(Scan.user_id == user_id)
        await db.execute(stmt)
        await db.commit()
        return True

    @staticmethod
    async def filter_scans(db: AsyncSession, user_id: str, status: Optional[str] = None, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, limit: int = 20, offset: int = 0) -> tuple[List[Scan], int]:
        """Filter scans by status and date"""
        stmt = select(Scan).where(Scan.user_id == user_id)
        if status:
            stmt = stmt.where(Scan.status == status)
        if start_date:
            stmt = stmt.where(Scan.created_at >= start_date)
        if end_date:
            stmt = stmt.where(Scan.created_at <= end_date)
        
        stmt = stmt.order_by(desc(Scan.created_at)).limit(limit).offset(offset)
        result = await db.execute(stmt)
        scans = result.scalars().all()

        # Count total
        count_stmt = select(func.count()).select_from(Scan).where(Scan.user_id == user_id)
        if status:
            count_stmt = count_stmt.where(Scan.status == status)
        if start_date:
            count_stmt = count_stmt.where(Scan.created_at >= start_date)
        if end_date:
            count_stmt = count_stmt.where(Scan.created_at <= end_date)
        
        count_result = await db.execute(count_stmt)
        total = count_result.scalar() or 0
        
        return scans, total

    @staticmethod
    async def get_scan_stats(db: AsyncSession, user_id: str) -> dict:
        """Get scan statistics for a user"""
        stmt = select(
            func.count(Scan.id).label("total"),
            func.sum(func.case((Scan.status == ScanStatus.AUTHENTIC, 1), else_=0)).label("authentic"),
            func.sum(func.case((Scan.status == ScanStatus.CAUTION, 1), else_=0)).label("caution"),
            func.sum(func.case((Scan.status == ScanStatus.FAKE, 1), else_=0)).label("fake"),
            func.sum(func.case((Scan.status == ScanStatus.PENDING, 1), else_=0)).label("pending")
        ).where(Scan.user_id == user_id)
        
        result = await db.execute(stmt)
        row = result.fetchone()
        
        return {
            "total_scans": row.total or 0,
            "authentic_count": row.authentic or 0,
            "suspicious_count": row.caution or 0,
            "fake_count": row.fake or 0,
            "pending_count": row.pending or 0
        }
