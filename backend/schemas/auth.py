"""Authentication request and response schemas"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from backend.models.user import UserRole, UserStatus


class RegisterRequest(BaseModel):
    """User registration request"""
    email: Optional[EmailStr] = None
    phone: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    role: UserRole = UserRole.CONSUMER


class LoginRequest(BaseModel):
    """User login request"""
    phone: str = Field(..., min_length=10, max_length=20)
    password: str = Field(...)


class VerifyOTPRequest(BaseModel):
    """Verify OTP request"""
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    otp_code: str = Field(..., min_length=6, max_length=6)
    purpose: str  # registration, login, password_reset, phone_verification


class ResendOTPRequest(BaseModel):
    """Resend OTP request"""
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    purpose: str


class ForgotPasswordRequest(BaseModel):
    """Forgot password request"""
    phone: str = Field(..., min_length=10, max_length=20)


class ResetPasswordRequest(BaseModel):
    """Reset password request"""
    phone: str = Field(..., min_length=10, max_length=20)
    otp_code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8)


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserResponse(BaseModel):
    """User response"""
    id: str
    email: Optional[str] = None
    phone: str
    first_name: str
    last_name: str
    role: UserRole
    status: UserStatus
    email_verified: bool
    phone_verified: bool
    profile_image_url: Optional[str] = None
    preferred_language: str = "en"
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Auth response with user + tokens"""
    user: UserResponse
    tokens: TokenResponse


class ProfileUpdateRequest(BaseModel):
    """Profile update request"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    preferred_language: Optional[str] = None


class AvatarUploadResponse(BaseModel):
    """Avatar upload response"""
    profile_image_url: str
    message: str = "Avatar updated successfully"


class SessionResponse(BaseModel):
    """Session response"""
    id: str
    user_id: str
    device_info: Optional[dict] = None
    ip_address: Optional[str] = None
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class LogoutRequest(BaseModel):
    """Logout request"""
    all_devices: bool = False  # If true, logout from all devices
