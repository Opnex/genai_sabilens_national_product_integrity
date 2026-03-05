"""NAFDAC enforcement service"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from app.models.nafdac import Case, EnforcementAction
from app.models.alert import Alert


class NAFDACService:
    """NAFDAC case and enforcement management"""
    
    @staticmethod
    async def create_case(db: AsyncSession, report_id: str, case_data: dict) -> Case:
        """Create investigation case"""
        case = Case(
            report_id=report_id,
            case_number=case_data.get("case_number"),
            status="open",
            severity=case_data.get("severity", "medium"),
            description=case_data.get("description"),
            assigned_officer_id=case_data.get("assigned_officer_id"),
            created_at=datetime.utcnow(),
        )
        db.add(case)
        await db.commit()
        await db.refresh(case)
        return case
    
    
    @staticmethod
    async def record_enforcement(db: AsyncSession, case_id: str, action_data: dict) -> EnforcementAction:
        """Record enforcement action (raid, seizure, notice)"""
        action = EnforcementAction(
            case_id=case_id,
            action_type=action_data.get("type"),  # raid, seizure, warning_notice, fine
            location=action_data.get("location"),
            quantity_seized=action_data.get("quantity_seized"),
            value_seized=action_data.get("value_seized"),
            description=action_data.get("description"),
            officer_id=action_data.get("officer_id"),
            created_at=datetime.utcnow(),
        )
        db.add(action)
        await db.commit()
        await db.refresh(action)
        return action
    
    
    @staticmethod
    async def get_case(db: AsyncSession, case_id: str) -> Optional[Case]:
        """Get case by ID"""
        return await db.get(Case, case_id)
    
    
    @staticmethod
    async def get_cases(db: AsyncSession, status: Optional[str] = None, limit: int = 50, offset: int = 0) -> tuple[List[Case], int]:
        """Get cases with optional filter"""
        stmt = select(Case).order_by(desc(Case.created_at))
        
        if status:
            stmt = stmt.where(Case.status == status)
        
        stmt = stmt.limit(limit).offset(offset)
        result = await db.execute(stmt)
        cases = result.scalars().all()
        
        # Count total
        count_stmt = select(func.count()).select_from(Case)
        if status:
            count_stmt = count_stmt.where(Case.status == status)
        count_result = await db.execute(count_stmt)
        total = count_result.scalar() or 0
        
        return cases, total
    
    
    @staticmethod
    async def close_case(db: AsyncSession, case_id: str, resolution: str) -> Case:
        """Close case with resolution"""
        case = await db.get(Case, case_id)
        if not case:
            raise ValueError("Case not found")
        
        case.status = "closed"
        case.resolution = resolution
        case.closed_at = datetime.utcnow()
        await db.commit()
        await db.refresh(case)
        return case
    
    
    @staticmethod
    async def get_hotspot_cases(db: AsyncSession, latitude: float, longitude: float, radius_km: float = 5) -> List[Case]:
        """Get cases near location (for hotspot analysis)"""
        # Mock: In production, use PostGIS for proximity search
        stmt = select(Case).where(Case.status != "closed").order_by(desc(Case.created_at)).limit(100)
        result = await db.execute(stmt)
        return result.scalars().all()
    @staticmethod
    async def get_officers(db: AsyncSession) -> List[dict]:
        """Get NAFDAC officers (mock implementation)"""
        # In a real app, query a dedicated 'officers' table or filter by role
        from app.models.user import User, UserRole
        stmt = select(User).where(User.role == UserRole.NAFDAC)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def verify_company(db: AsyncSession, company_id: str, status: str, officer_id: str) -> bool:
        """Verify or reject a company registration"""
        from app.models.company import Company, CompanyStatus
        company = await db.get(Company, company_id)
        if not company:
            return False
        company.status = status
        company.verified_by = officer_id
        company.verified_at = datetime.utcnow()
        await db.commit()
        return True

    @staticmethod
    async def get_national_stats(db: AsyncSession) -> dict:
        """Get high-level national statistics"""
        from app.models.scan import Scan, ScanStatus
        from app.models.company import Company
        
        total_companies = (await db.execute(select(func.count(Company.id)))).scalar() or 0
        total_scans = (await db.execute(select(func.count(Scan.id)))).scalar() or 0
        counterfeits = (await db.execute(select(func.count(Scan.id)).where(Scan.status == ScanStatus.FAKE))).scalar() or 0
        
        return {
            "total_companies": total_companies,
            "total_scans": total_scans,
            "seizures_value": 150000000, # Placeholder
            "active_investigations": 42, # Placeholder
            "counterfeit_rate": (counterfeits / total_scans * 100) if total_scans > 0 else 0
        }

    @staticmethod
    async def get_blacklisted_vendors(db: AsyncSession) -> List[dict]:
        """Get vendors with high risk or blacklisted status"""
        from app.models.analytics import VendorLocation
        stmt = select(VendorLocation).where(VendorLocation.is_blacklisted == True)
        result = await db.execute(stmt)
        return result.scalars().all()
