from sqlalchemy.orm import Session
from datetime import datetime

from app.models.customer_otp import CustomerOTP
from app.models.customer import Customer
from app.utils.otp import generate_otp, get_expiry
from app.services.sms import send_sms
from app.core.jwt import create_access_token
from fastapi import HTTPException


# --------------------------------
# REQUEST OTP
# --------------------------------
def request_otp(db: Session, phone: str):

    # Remove old OTPs
    db.query(CustomerOTP).filter(
        CustomerOTP.phone == phone,
        CustomerOTP.is_used == False
    ).delete()

    otp = generate_otp()

    otp_obj = CustomerOTP(
        phone=phone,
        otp_code=otp,
        expires_at=get_expiry()
    )

    db.add(otp_obj)
    db.commit()

    send_sms(phone, otp)

    return {"message": "OTP sent successfully"}


# --------------------------------
# VERIFY OTP
# --------------------------------
def verify_otp(db: Session, phone: str, otp: str):

    otp_obj = db.query(CustomerOTP).filter(
        CustomerOTP.phone == phone,
        CustomerOTP.is_used == False
    ).order_by(CustomerOTP.created_at.desc()).first()

    if not otp_obj:
        raise HTTPException(status_code=400, detail="OTP not found")

    if otp_obj.is_expired:
        raise HTTPException(status_code=400, detail="OTP expired")

    # Rate limiting
    if otp_obj.attempts >= 3:
        raise HTTPException(
            status_code=429,
            detail="Too many attempts. Request new OTP"
        )

    if otp_obj.otp_code != otp:

        otp_obj.attempts += 1
        db.commit()

        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Success
    otp_obj.is_used = True

    # Create or fetch customer
    customer = db.query(Customer).filter(
        Customer.phone == phone
    ).first()

    if not customer:
        customer = Customer(phone=phone)
        db.add(customer)

    db.commit()

    token = create_access_token({
        "sub": str(customer.id),
        "type": "customer"
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }
