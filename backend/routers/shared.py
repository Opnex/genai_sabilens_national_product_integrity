"""Shared verification routes"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.utils.response import success_response

router = APIRouter()


# NAFDAC Verification
@router.get("/nafdac/{nafdac_number}")
async def verify_nafdac_number(nafdac_number: str, db: AsyncSession = Depends(get_db)):
    return success_response({})


@router.get("/batch/{batch_number}")
async def verify_batch_number(batch_number: str, db: AsyncSession = Depends(get_db)):
    return success_response({})


@router.post("/image")
async def verify_product_image(db: AsyncSession = Depends(get_db)):
    return success_response({})


@router.get("/product/{product_id}")
async def verify_product(product_id: str, db: AsyncSession = Depends(get_db)):
    return success_response({})


# Location Services
@router.get("/states")
async def get_nigerian_states(db: AsyncSession = Depends(get_db)):
    return success_response({})


@router.get("/cities/{state}")
async def get_state_cities(state: str, db: AsyncSession = Depends(get_db)):
    return success_response({})


@router.post("/reverse-geocode")
async def reverse_geocode(db: AsyncSession = Depends(get_db)):
    return success_response({})
