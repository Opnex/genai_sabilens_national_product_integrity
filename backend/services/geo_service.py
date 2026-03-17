"""Geospatial analytics service"""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from backend.models.scan import Scan, ScanStatus
from backend.models.product import Product
from backend.models.analytics import Hotspot, VendorLocation, RiskLevel

class GeoService:
    """Geospatial logic for heatmap and vendor risk"""

    @staticmethod
    async def get_heatmap_clusters(db: AsyncSession, company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get scan clusters for heatmap visualization"""
        # In production, this would use PostGIS ST_ClusterKMeans or similar
        # For now, we return raw points with status weighting
        stmt = select(Scan).where(Scan.scan_location.is_not(None))
        if company_id:
            stmt = stmt.join(Product, Product.id == Scan.product_id).where(Product.company_id == company_id)
        
        result = await db.execute(stmt)
        scans = result.scalars().all()
        
        clusters = []
        for s in scans:
            # Assuming scan_location is "LAT,LNG" string for simple mock
            try:
                lat, lng = map(float, s.scan_location.split(','))
                clusters.append({
                    "lat": lat,
                    "lng": lng,
                    "weight": 1.0 if s.status == ScanStatus.FAKE else 0.5,
                    "status": s.status
                })
            except:
                continue
        return clusters

    @staticmethod
    async def get_high_risk_vendors(db: AsyncSession, limit: int = 10) -> List[VendorLocation]:
        """Get vendors with critical or high risk levels"""
        stmt = select(VendorLocation).where(
            VendorLocation.risk_level.in_([RiskLevel.CRITICAL, RiskLevel.HIGH])
        ).order_by(desc(VendorLocation.report_count)).limit(limit)
        
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def update_hotspots(db: AsyncSession):
        """Update hotspot aggregates based on new reports"""
        # Mock logic to populate hotspots from reports
        # This would typically be a background task (Celery)
        pass

    @staticmethod
    async def get_region_risk(db: AsyncSession, company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get risk level breakdown by region"""
        return [
            {"region": "South West", "risk_score": 7.5, "status": "high"},
            {"region": "North West", "risk_score": 4.2, "status": "medium"}
        ]

    @staticmethod
    async def get_raw_coordinates(db: AsyncSession, company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all scan coordinates for a company"""
        stmt = select(Scan).where(Scan.scan_location.is_not(None))
        if company_id:
            stmt = stmt.join(Product, Product.id == Scan.product_id).where(Product.company_id == company_id)
        
        result = await db.execute(stmt)
        scans = result.scalars().all()
        
        coords = []
        for s in scans:
            try:
                lat, lng = map(float, s.scan_location.split(','))
                coords.append({"id": str(s.id), "lat": lat, "lng": lng, "timestamp": s.created_at})
            except:
                continue
        return coords

