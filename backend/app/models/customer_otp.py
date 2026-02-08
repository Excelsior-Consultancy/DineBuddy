from sqlalchemy import Column, String, DateTime, Integer, Boolean
from datetime import datetime, timezone

from app.db.base import Base, IDMixin


class CustomerOTP(Base, IDMixin):
    __tablename__ = "customer_otps"
    phone = Column(String(20), index=True, nullable=False)
    otp_code = Column(String(6), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    attempts = Column(Integer, default=0)  # max 3
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    @property
    def is_expired(self):
        return datetime.now(timezone.utc) > self.expires_at
