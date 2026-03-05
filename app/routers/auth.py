"""Auth routes (PUBLIC)"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.utils.response import success_response, error_response
from app.schemas.auth import (
    RegisterRequest, LoginRequest, VerifyOTPRequest, ResendOTPRequest,
    ForgotPasswordRequest, ResetPasswordRequest, RefreshTokenRequest,
    AuthResponse
)
from app.services.auth_service import AuthService
from app.dependencies import get_current_user

router = APIRouter()


@router.post("/register", status_code=201)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register new user"""
    try:
        user, tokens = await AuthService.register_user(db, req)
        return success_response({
            "user": user.dict(),
            "tokens": tokens.dict()
        }, status_code=201)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable. Check DATABASE_URL credentials and database status.",
        )
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed. Verify Postgres is running and DATABASE_URL credentials are correct.",
        )


@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """User login"""
    try:
        user, tokens = await AuthService.login_user(db, req)
        return success_response({
            "user": user.dict(),
            "tokens": tokens.dict()
        })
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable. Check DATABASE_URL credentials and database status.",
        )
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed. Verify Postgres is running and DATABASE_URL credentials are correct.",
        )


@router.post("/logout")
async def logout(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """User logout"""
    try:
        await AuthService.logout(db, current_user.id)
        return success_response({"message": "Logged out successfully"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refresh-token")
async def refresh_token(req: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Refresh access token"""
    try:
        tokens = await AuthService.refresh_access_token(db, req.refresh_token)
        return success_response({"tokens": tokens.dict()})
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Request password reset OTP"""
    try:
        otp_code = await AuthService.send_otp(db, req.phone, None, "password_reset")
        return success_response({"message": "OTP sent to phone"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Reset password with OTP"""
    try:
        await AuthService.reset_password(db, req.phone, req.otp_code, req.new_password)
        return success_response({"message": "Password reset successfully"})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify-phone")
async def verify_phone(req: VerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    """Verify phone with OTP"""
    try:
        await AuthService.verify_otp(db, req.phone, req.otp_code, "registration")
        return success_response({"message": "Phone verified successfully"})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify-email")
async def verify_email(req: VerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    """Verify email with OTP"""
    try:
        await AuthService.verify_otp(db, req.email, req.otp_code, "email_verification")
        return success_response({"message": "Email verified successfully"})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/resend-otp")
async def resend_otp(req: ResendOTPRequest, db: AsyncSession = Depends(get_db)):
    """Resend OTP"""
    try:
        otp_code = await AuthService.send_otp(db, req.phone, req.email, req.purpose)
        return success_response({"message": "OTP sent successfully"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

