"""Authentication service"""
import random
import string
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import smtplib
from email.mime.text import MIMEText

from app.models.user import User, Session, OTPVerification, UserRole, UserStatus
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.config import settings


class AuthService:
    """Authentication service"""
    
    @staticmethod
    async def register_user(db: AsyncSession, req: RegisterRequest) -> Tuple[UserResponse, TokenResponse]:
        """Register new user"""
        # Check if user exists
        stmt = select(User).where((User.phone == req.phone) | (User.email == req.email))
        existing = await db.execute(stmt)
        if existing.scalars().first():
            raise ValueError("User already exists")
        
        # In local debug mode, auto-activate accounts to simplify testing.
        auto_activate = settings.AUTH_AUTO_ACTIVATE

        # Create user
        user = User(
            email=req.email,
            phone=req.phone,
            password_hash=hash_password(req.password),
            first_name=req.first_name,
            last_name=req.last_name,
            role=req.role,
            status=UserStatus.ACTIVE if auto_activate else UserStatus.PENDING,
            phone_verified=auto_activate,
            email_verified=auto_activate,
        )
        db.add(user)
        await db.flush()
        
        # Generate OTP
        otp_code = "".join(random.choices(string.digits, k=6))
        otp = OTPVerification(
            user_id=user.id,
            phone=req.phone,
            email=req.email,
            otp_code=otp_code,
            purpose="registration",
            expires_at=datetime.utcnow() + timedelta(minutes=10),
        )
        db.add(otp)
        await db.commit()
        
        # Send OTP (mock for now)
        # await send_sms(req.phone, f"Your SabiLens OTP: {otp_code}")
        
        # Create tokens
        tokens = await AuthService.create_tokens(user)
        user_resp = UserResponse.from_orm(user)
        
        return user_resp, tokens
    
    
    @staticmethod
    async def login_user(db: AsyncSession, req: LoginRequest) -> Tuple[UserResponse, TokenResponse]:
        """Login user"""
        stmt = select(User).where(User.phone == req.phone)
        result = await db.execute(stmt)
        user = result.scalars().first()
        
        if not user or not verify_password(req.password, user.password_hash):
            raise ValueError("Invalid credentials")
        
        if user.status != UserStatus.ACTIVE:
            raise ValueError("User account is not active")
        
        # Update last login
        user.last_login = datetime.utcnow()
        await db.commit()
        await db.refresh(user)
        
        # Create tokens
        tokens = await AuthService.create_tokens(user)
        user_resp = UserResponse.from_orm(user)
        
        return user_resp, tokens
    
    
    @staticmethod
    async def create_tokens(user: User) -> TokenResponse:
        """Create access and refresh tokens"""
        access_token = create_access_token({"sub": user.id, "role": user.role.value})
        refresh_token = create_refresh_token({"sub": user.id})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    
    
    @staticmethod
    async def verify_otp(db: AsyncSession, phone: str, otp_code: str, purpose: str) -> bool:
        """Verify OTP"""
        stmt = select(OTPVerification).where(
            (OTPVerification.phone == phone) &
            (OTPVerification.otp_code == otp_code) &
            (OTPVerification.purpose == purpose) &
            (OTPVerification.verified_at.is_(None)) &
            (OTPVerification.expires_at > datetime.utcnow())
        )
        result = await db.execute(stmt)
        otp = result.scalars().first()
        
        if not otp:
            raise ValueError("Invalid or expired OTP")
        
        # Mark as verified
        otp.verified_at = datetime.utcnow()
        
        # Update user if registration
        if purpose == "registration":
            user = await db.get(User, otp.user_id)
            if user:
                user.phone_verified = True
                user.status = UserStatus.ACTIVE
        
        await db.commit()
        return True
    
    
    @staticmethod
    async def send_otp(db: AsyncSession, phone: str, email: Optional[str], purpose: str) -> str:
        """Send OTP"""
        otp_code = "".join(random.choices(string.digits, k=6))
        
        # Delete previous OTPs
        stmt = select(OTPVerification).where(
            (OTPVerification.phone == phone) |
            (OTPVerification.email == email)
        )
        result = await db.execute(stmt)
        old_otps = result.scalars().all()
        for old_otp in old_otps:
            await db.delete(old_otp)
        
        # Create new OTP
        otp = OTPVerification(
            phone=phone,
            email=email,
            otp_code=otp_code,
            purpose=purpose,
            expires_at=datetime.utcnow() + timedelta(minutes=10),
        )
        db.add(otp)
        await db.commit()
        
        # Send SMS/Email (mock)
        # await send_sms(phone, f"Your SabiLens OTP: {otp_code}")
        
        return otp_code
    
    
    @staticmethod
    async def refresh_access_token(db: AsyncSession, refresh_token: str) -> TokenResponse:
        """Refresh access token"""
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")
        
        user_id = payload.get("sub")
        user = await db.get(User, user_id)
        
        if not user or user.status != UserStatus.ACTIVE:
            raise ValueError("User not found or inactive")
        
        tokens = await AuthService.create_tokens(user)
        return tokens
    
    
    @staticmethod
    async def reset_password(db: AsyncSession, phone: str, otp_code: str, new_password: str) -> bool:
        """Reset password"""
        stmt = select(OTPVerification).where(
            (OTPVerification.phone == phone) &
            (OTPVerification.otp_code == otp_code) &
            (OTPVerification.purpose == "password_reset") &
            (OTPVerification.expires_at > datetime.utcnow())
        )
        result = await db.execute(stmt)
        otp = result.scalars().first()
        
        if not otp:
            raise ValueError("Invalid or expired OTP")
        
        # Update password
        stmt = select(User).where(User.phone == phone)
        result = await db.execute(stmt)
        user = result.scalars().first()
        
        if not user:
            raise ValueError("User not found")
        
        user.password_hash = hash_password(new_password)
        otp.verified_at = datetime.utcnow()
        await db.commit()
        
        return True
    
    
    @staticmethod
    async def logout(db: AsyncSession, user_id: str, all_devices: bool = False) -> bool:
        """Logout user"""
        if all_devices:
            # Delete all sessions
            stmt = select(Session).where(Session.user_id == user_id)
            result = await db.execute(stmt)
            sessions = result.scalars().all()
            for session in sessions:
                await db.delete(session)
        await db.commit()
        return True
