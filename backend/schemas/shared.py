"""Shared verification and location schemas"""
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class NAFDACVerificationResponse(BaseModel):
    """NAFDAC number verification response"""
    nafdac_number: str
    is_valid: bool
    product_name: Optional[str] = None
    manufacturer: Optional[str] = None
    status: Optional[str] = None
    expires_at: Optional[datetime] = None
    company_id: Optional[str] = None
    message: str


class BatchVerificationResponse(BaseModel):
    """Batch number verification response"""
    batch_number: str
    is_valid: bool
    product_name: Optional[str] = None
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None
    message: str


class ImageVerificationRequest(BaseModel):
    """Image verification request"""
    image_url: str
    product_nafdac_number: Optional[str] = None


class ImageVerificationResponse(BaseModel):
    """Image verification response"""
    is_authentic: bool
    confidence_score: float
    detected_anomalies: Optional[List[str]] = None
    message: str


class ProductVerificationResponse(BaseModel):
    """Product verification response"""
    product_id: str
    nafdac_number: str
    name: str
    manufacturer: str
    status: str
    is_registered: bool
    company_id: Optional[str] = None
    embeddings_count: int
    message: str


class StateResponse(BaseModel):
    """Nigerian state response"""
    id: int
    name: str
    capital: Optional[str] = None
    region: str


class StatesListResponse(BaseModel):
    """States list response"""
    states: List[StateResponse]
    total: int


class CityResponse(BaseModel):
    """City response"""
    city: str
    state: str


class CitiesListResponse(BaseModel):
    """Cities list response"""
    cities: List[CityResponse]
    state: str
    total: int


class ReverseGeocodeRequest(BaseModel):
    """Reverse geocode request"""
    latitude: float
    longitude: float


class ReverseGeocodeResponse(BaseModel):
    """Reverse geocode response"""
    address: str
    city: str
    state: str
    country: str
    latitude: float
    longitude: float
