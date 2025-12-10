"""
Customer model - OTP-based authentication for food ordering
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer
from datetime import datetime

from app.db.base import Base, IDMixin, TimestampMixin


class Customer(Base, IDMixin, TimestampMixin):
    """
    Customer model for end-users who place orders
    
    Customers authenticate using OTP (One-Time Password) sent to their phone.
    No password required - just phone number verification.
    
    Flow:
    1. Customer scans QR code at restaurant
    2. Enters phone number
    3. Receives OTP via SMS
    4. Verifies OTP to place order
    """
    __tablename__ = "customers"
    
    # Contact Info (Primary identifier)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    
    # Optional Profile Info
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    
    # OTP Authentication
    otp_code = Column(String(6), nullable=True)  # 6-digit OTP
    otp_expires_at = Column(DateTime, nullable=True)
    otp_verified_at = Column(DateTime, nullable=True)  # Last successful verification
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_phone_verified = Column(Boolean, default=False, nullable=False)
    
    # Tracking
    last_order_at = Column(DateTime, nullable=True)
    total_orders = Column(Integer, default=0, nullable=False)
    
    def __repr__(self):
        return f"<Customer {self.phone} ({self.name or 'Anonymous'})>"
    
    @property
    def is_otp_valid(self) -> bool:
        """Check if current OTP is still valid"""
        if not self.otp_code or not self.otp_expires_at:
            return False
        return datetime.utcnow() < self.otp_expires_at
    
    @property
    def masked_phone(self) -> str:
        """Return masked phone number for display (e.g., +91****5678)"""
        if not self.phone or len(self.phone) < 4:
            return "****"
        return f"{self.phone[:-4]}****{self.phone[-4:]}"

