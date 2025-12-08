from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, Text
from app.db.base import Base, IDMixin, TimestampMixin
from sqlalchemy.orm import relationship

class MenuItem(Base, IDMixin, TimestampMixin):
    __tablename__ = 'menu_items'
    
    name = Column(String, nullable=False, doc="The name of the menu item.")
    description = Column(Text, nullable=True, doc="Description of the menu item.")
    price = Column(Numeric(10, 2), nullable=False, doc="Price of the menu item.")
    menu_category_id = Column(Integer, ForeignKey('menu_categories.id'), nullable=False, doc="The menu category this item belongs to.")
    
    # Relationship to MenuCategory
    menu_category = relationship('MenuCategory', back_populates='menu_items')

