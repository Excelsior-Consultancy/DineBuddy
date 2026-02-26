from sqlalchemy import Column, Integer, ForeignKey, String, Numeric
from sqlalchemy.orm import relationship

from app.db.base import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)

    # Link to order
    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False
    )

    # Menu item reference
    menu_item_id = Column(
        Integer,
        ForeignKey("menu_items.id"),
        nullable=False
    )

    # Optional variant (size, addon, etc.)
    variant_id = Column(
        Integer,
        ForeignKey("menu_item_variants.id"),
        nullable=True
    )

    quantity = Column(Integer, nullable=False)

    # Snapshot price (VERY IMPORTANT)
    unit_price = Column(Numeric(7, 2), nullable=False)

    special_instructions = Column(String(500), nullable=True)

    # Relationships
    order = relationship("Order", back_populates="items")

    menu_item = relationship("MenuItem")

    variant = relationship("MenuItemVariant")
