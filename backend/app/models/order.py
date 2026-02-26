import enum
from sqlalchemy import Column, Integer, ForeignKey, String, Enum, Numeric
from sqlalchemy.orm import relationship

from app.db.base import Base


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    PREPARING = "preparing"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False
    )

    # NULL = walk-in / guest / anonymous
    customer_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    table_number = Column(String(20), nullable=True)

    status = Column(
    Enum(
        OrderStatus,
        name="orderstatus",          # Must match DB enum
        native_enum=True,
        values_callable=lambda x: [e.value for e in x],  # 👈 USE VALUES
        validate_strings=True,
    ),
    default=OrderStatus.PENDING,
    nullable=False,
)

    total_amount = Column(Numeric(7, 2), nullable=False)
    tax_amount = Column(Numeric(7, 2), default=0, nullable=False)

    notes = Column(String(500), nullable=True)

    # Staff/Admin who created the order
    created_by_user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    # ==========================
    # Relationships
    # ==========================

    restaurant = relationship("Restaurant")

    customer = relationship(
        "User",
        foreign_keys=[customer_id]
    )

    created_by = relationship(
        "User",
        foreign_keys=[created_by_user_id]
    )

    # ✅ FIX: Move inside class
    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )