from sqlalchemy import Column, String
from app.db.base import Base, IDMixin, TimestampMixin

class Restaurant(Base, IDMixin, TimestampMixin):
    __tablename__ = 'restaurants'
    name = Column(String, nullable=False, unique=True, doc="The unique name of the restaurant.")

    # TODO: Add relationship when MenuCategory model is created
    # categories = relationship('MenuCategory', back_populates='restaurant', cascade='all, delete-orphan', doc="Categories for this restaurant.")
