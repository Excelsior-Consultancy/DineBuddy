from sqlalchemy import Column, String, Integer, ForeignKey
from app.db.base import Base, IDMixin, TimestampMixin
from sqlalchemy.orm import relationship

class MenuCategory(Base, IDMixin, TimestampMixin):
    __tablename__ = 'menu_categories'
    name = Column(String, nullable=False, doc="The name of the menu category.")
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'), nullable=False, doc="The restaurant this category belongs to.")
    restaurant = relationship('Restaurant', back_populates='categories')