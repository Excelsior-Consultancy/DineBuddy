from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.otp_schema import OTPRequest, OTPVerify
from app.services.otp_service import request_otp, verify_otp


router = APIRouter(prefix="/auth/customer", tags=["Customer Auth"])


@router.post("/request-otp")
def send_otp(payload: OTPRequest, db: Session = Depends(get_db)):

    return request_otp(db, payload.phone)


@router.post("/verify-otp")
def verify(payload: OTPVerify, db: Session = Depends(get_db)):

    return verify_otp(db, payload.phone, payload.otp)
