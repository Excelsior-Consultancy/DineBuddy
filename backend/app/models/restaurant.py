from sqlalchemy import Column, String, Boolean
from app.db.base import Base, IDMixin, TimestampMixin
from sqlalchemy.orm import relationship


class Restaurant(Base, IDMixin, TimestampMixin):
    __tablename__ = "restaurants"

    name = Column(
        String,
        nullable=False,
        unique=True,
        doc="The unique name of the restaurant."
    )

    slug = Column(
        String,
        nullable=False,
        unique=True,
        index=True,
        doc="URL-safe unique slug"
    )

    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)

    is_active = Column(Boolean, default=True)
    timezone = Column(String, nullable=True)
    currency = Column(String, nullable=True)

    # categories = relationship(...)
