"""Company service"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, case
from sqlalchemy.exc import IntegrityError

from backend.models.company import Company, CompanyAPIKey
from backend.models.product import Product, ProductCategory
from backend.models.user import User, UserRole, UserStatus
from backend.core.security import hash_password


class CompanyService:
    """Company and product management"""
    
    @staticmethod
    async def create_company(db: AsyncSession, company_data: dict) -> Company:
        """Register company"""
        reg_no = company_data.get("registration_number")
        email = company_data.get("email")
        phone = company_data.get("phone")
        password = company_data.get("password")

        if not password:
            raise ValueError("Password is required for company registration")

        # Validate uniqueness with explicit messages.
        if reg_no:
            reg_stmt = select(Company).where(Company.registration_number == reg_no)
            reg_exists = (await db.execute(reg_stmt)).scalars().first()
            if reg_exists:
                raise ValueError("Registration number already exists")

        if email:
            email_stmt = select(Company).where(Company.email == email)
            email_exists = (await db.execute(email_stmt)).scalars().first()
            if email_exists:
                raise ValueError("Company email already exists")

            user_email_stmt = select(User).where(User.email == email)
            user_email_exists = (await db.execute(user_email_stmt)).scalars().first()
            if user_email_exists:
                raise ValueError("User email already exists")

        if phone:
            user_phone_stmt = select(User).where(User.phone == phone)
            user_phone_exists = (await db.execute(user_phone_stmt)).scalars().first()
            if user_phone_exists:
                raise ValueError("User phone already exists")

        company = Company(
            name=company_data.get("name"),
            registration_number=reg_no,
            email=email,
            phone=phone,
            address=company_data.get("address"),
            city=company_data.get("city"),
            state=company_data.get("state"),
            website=company_data.get("website"),
            status="pending",  # Needs NAFDAC verification
            created_at=datetime.utcnow(),
        )
        db.add(company)

        # Flush first so company.id is available for the admin user.
        await db.flush()

        admin_user = User(
            email=email,
            phone=phone,
            password_hash=hash_password(password),
            first_name=company_data.get("name"),
            last_name="Admin",
            role=UserRole.COMPANY_ADMIN,
            status=UserStatus.ACTIVE,
            email_verified=True,
            phone_verified=True,
            company_id=company.id,
        )
        db.add(admin_user)

        await db.commit()
        await db.refresh(company)
        return company
    
    
    @staticmethod
    async def get_company(db: AsyncSession, company_id: str) -> Optional[Company]:
        """Get company by ID"""
        return await db.get(Company, company_id)
    
    
    @staticmethod
    async def create_product(db: AsyncSession, company_id: str, product_data: dict) -> Product:
        """Register product in NAFDAC registry"""
        def _parse_date(value):
            if not value:
                return None
            if isinstance(value, str):
                try:
                    return datetime.strptime(value, "%Y-%m-%d").date()
                except ValueError as exc:
                    raise ValueError("Date fields must use YYYY-MM-DD format") from exc
            return value

        nafdac_number = product_data.get("nafdac_number")
        if nafdac_number:
            existing_stmt = select(Product).where(Product.nafdac_number == nafdac_number)
            existing = (await db.execute(existing_stmt)).scalars().first()
            if existing:
                raise ValueError("NAFDAC number already exists")

        product = Product(
            company_id=company_id,
            nafdac_number=nafdac_number,
            name=product_data.get("name"),
            manufacturer_name=product_data.get("manufacturer_name"),
            description=product_data.get("description"),
            category_id=product_data.get("category_id"),
            batch_number=product_data.get("batch_number"),
            manufacturing_date=_parse_date(product_data.get("manufacturing_date")),
            expiry_date=_parse_date(product_data.get("expiry_date")),
            ingredients=product_data.get("ingredients"),
            warnings=product_data.get("warnings"),
            created_at=datetime.utcnow(),
        )
        db.add(product)
        try:
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise ValueError("NAFDAC number already exists") from exc
        await db.refresh(product)
        return product
    
    
    @staticmethod
    async def get_products(db: AsyncSession, company_id: str, limit: int = 50, offset: int = 0) -> tuple[List[Product], int]:
        """Get company products"""
        stmt = select(Product).where(Product.company_id == company_id).order_by(desc(Product.created_at)).limit(limit).offset(offset)
        result = await db.execute(stmt)
        products = result.scalars().all()
        
        # Count
        count_stmt = select(func.count()).select_from(Product).where(Product.company_id == company_id)
        count_result = await db.execute(count_stmt)
        total = count_result.scalar() or 0
        
        return products, total
    
    
    @staticmethod
    async def generate_api_key(db: AsyncSession, company_id: str, key_name: str) -> CompanyAPIKey:
        """Generate API key for server-to-server integration"""
        import secrets
        
        api_key = CompanyAPIKey(
            company_id=company_id,
            key_name=key_name,
            api_key=f"key_{secrets.token_urlsafe(32)}",
            created_at=datetime.utcnow(),
        )
        db.add(api_key)
        await db.commit()
        await db.refresh(api_key)
        return api_key
    
    
    @staticmethod
    async def verify_api_key(db: AsyncSession, api_key: str) -> Optional[str]:
        """Verify API key and return company ID"""
        stmt = select(CompanyAPIKey).where(CompanyAPIKey.api_key == api_key)
        result = await db.execute(stmt)
        key_record = result.scalars().first()
        
        if key_record:
            return str(key_record.company_id)
        return None
    @staticmethod
    async def get_team_members(db: AsyncSession, company_id: str) -> List["User"]:
        """Get company team members"""
        from backend.models.user import User
        stmt = select(User).where(User.company_id == company_id)
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_dashboard_stats(db: AsyncSession, company_id: str) -> dict:
        """Get company dashboard statistics"""
        from backend.models.scan import Scan, ScanStatus
        # Aggregate scans linked to this company's products.
        stmt = select(
            func.count(Scan.id).label("total"),
            func.sum(case((Scan.status == ScanStatus.AUTHENTIC, 1), else_=0)).label("authentic"),
            func.sum(case((Scan.status == ScanStatus.CAUTION, 1), else_=0)).label("caution"),
            func.sum(case((Scan.status == ScanStatus.FAKE, 1), else_=0)).label("fake")
        ).join(
            Product, Product.id == Scan.product_id
        ).where(
            Product.company_id == company_id
        )
        
        result = await db.execute(stmt)
        row = result.fetchone()
        
        return {
            "total_scans": row.total or 0,
            "authentic_count": row.authentic or 0,
            "caution_count": row.caution or 0,
            "counterfeit_count": row.fake or 0,
            "this_week_scans": 0 # Placeholder
        }

    @staticmethod
    async def get_heatmap_data(db: AsyncSession, company_id: str) -> List[dict]:
        """Get heatmap data for company products"""
        from backend.models.analytics import Hotspot
        # Mocking: filtering hotspots that might be relevant to company
        stmt = select(Hotspot).limit(100)
        result = await db.execute(stmt)
        hotspots = result.scalars().all()
        return [{"lat": float(h.location.split(',')[0]), "lng": float(h.location.split(',')[1]), "count": h.report_count} for h in hotspots if h.location]

    @staticmethod
    async def get_product_stats(db: AsyncSession, company_id: str) -> dict:
        """Get summarized product statistics"""
        from backend.models.product import ProductStatus
        stmt = select(
            func.count(Product.id).label("total"),
            func.sum(case((Product.status == ProductStatus.ACTIVE, 1), else_=0)).label("active"),
            func.sum(case((Product.status == ProductStatus.PENDING, 1), else_=0)).label("pending")
        ).where(Product.company_id == company_id)
        
        result = await db.execute(stmt)
        row = result.fetchone()
        
        return {
            "total_products": row.total or 0,
            "active_products": row.active or 0,
            "pending_products": row.pending or 0,
            "expired_products": 0,
            "discontinued_products": 0
        }

    @staticmethod
    async def get_api_keys(db: AsyncSession, company_id: str) -> List[CompanyAPIKey]:
        """Get all API keys for a company"""
        stmt = select(CompanyAPIKey).where(CompanyAPIKey.company_id == company_id)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def delete_api_key(db: AsyncSession, company_id: str, key_id: str) -> bool:
        """Deactivate/delete an API key"""
        stmt = select(CompanyAPIKey).where((CompanyAPIKey.company_id == company_id) & (CompanyAPIKey.id == key_id))
        result = await db.execute(stmt)
        key = result.scalars().first()
        if key:
            await db.delete(key)
            await db.commit()
            return True
        return False

    @staticmethod
    async def get_dashboard_trends(db: AsyncSession, company_id: str, period: str) -> dict:
        """Get scan and report trends (mock)"""
        return {
            "scans_trend": [{"date": "2026-03-01", "count": 120}, {"date": "2026-03-02", "count": 145}],
            "reports_trend": [{"date": "2026-03-01", "count": 5}, {"date": "2026-03-02", "count": 8}],
            "period": period
        }

    @staticmethod
    async def get_state_breakdown(db: AsyncSession, company_id: str) -> List[dict]:
        """Get scan stats per state (mock)"""
        return [
            {"state": "Lagos", "scan_count": 500, "counterfeit_count": 45, "risk_level": "high"},
            {"state": "Kano", "scan_count": 300, "counterfeit_count": 12, "risk_level": "medium"}
        ]

    @staticmethod
    async def get_recent_alerts(db: AsyncSession, company_id: str, limit: int = 5) -> List[dict]:
        """Get latest alerts for company"""
        from backend.models.alert import Alert
        stmt = select(Alert).where(Alert.company_id == company_id).order_by(desc(Alert.created_at)).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_quick_stats(db: AsyncSession, company_id: str) -> dict:
        """Get summarized instant stats"""
        return {
            "active_monitors": 12,
            "reports_today": 4,
            "scans_today": 182,
            "new_alerts": 2
        }

    @staticmethod
    async def mark_alert_read(db: AsyncSession, company_id: str, alert_id: str) -> bool:
        """Mark alert as read"""
        from backend.models.alert import Alert
        stmt = select(Alert).where((Alert.company_id == company_id) & (Alert.id == alert_id))
        result = await db.execute(stmt)
        alert = result.scalars().first()
        if alert:
            alert.is_read = True
            await db.commit()
            return True
        return False

    @staticmethod
    async def mark_all_alerts_read(db: AsyncSession, company_id: str):
        """Mark all alerts for company as read"""
        from backend.models.alert import Alert
        from sqlalchemy import update
        stmt = update(Alert).where(Alert.company_id == company_id).values(is_read=True)
        await db.execute(stmt)
        await db.commit()

