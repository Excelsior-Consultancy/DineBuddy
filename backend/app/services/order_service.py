from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from decimal import Decimal

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.menu_items import MenuItem
from app.models.menu_item_variant import MenuItemVariant


def create_order(
    db: Session,
    restaurant_id: int,
    payload,
    current_user,
):
    """
    Create order + order items atomically
    """

    # ----------------------------
    # Validate items
    # ----------------------------
    if not payload.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must contain at least one item",
        )

    total_amount = Decimal("0.00")
    tax_amount = Decimal("0.00")

    try:
        # ----------------------------
        # Start transaction
        # ----------------------------
        with db.begin_nested():

            # ----------------------------
            # Create Order (initial)
            # ----------------------------
            order = Order(
                restaurant_id=restaurant_id,
                customer_id=current_user.id,
                table_number=payload.table_number,
                status=OrderStatus.PENDING,   # ✅ Correct enum
                total_amount=Decimal("0.00"),
                tax_amount=Decimal("0.00"),
                created_by_user_id=current_user.id,
            )

            db.add(order)
            db.flush()  # ✅ Generate order.id

            order_items = []

            # ----------------------------
            # Process Items
            # ----------------------------
            for item in payload.items:

                # ----------------------------
                # Get Menu Item
                # ----------------------------
                menu_item = (
                    db.query(MenuItem)
                    .filter(
                        MenuItem.id == item.menu_item_id,
                        MenuItem.restaurant_id == restaurant_id,
                        MenuItem.is_available == True,
                    )
                    .first()
                )

                if not menu_item:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Menu item {item.menu_item_id} not available",
                    )

                # Base price
                unit_price = Decimal(menu_item.price)

                # ----------------------------
                # Variant Handling
                # ----------------------------
                if item.variant_id:

                    variant = (
                        db.query(MenuItemVariant)
                        .filter(
                            MenuItemVariant.id == item.variant_id,
                            MenuItemVariant.item_id == menu_item.id,  # ✅ FIXED
                        )
                        .first()
                    )

                    if not variant:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Variant {item.variant_id} not available",
                        )

                    # Add price adjustment
                    unit_price += Decimal(variant.price_adjustment)

                # ----------------------------
                # Calculate Line Total
                # ----------------------------
                line_total = unit_price * item.quantity
                total_amount += line_total

                # ----------------------------
                # Create Order Item
                # ----------------------------
                order_item = OrderItem(
                    order_id=order.id,
                    menu_item_id=menu_item.id,
                    variant_id=item.variant_id,
                    quantity=item.quantity,
                    unit_price=unit_price,
                    special_instructions=item.special_instructions,
                )

                order_items.append(order_item)

            # ----------------------------
            # Calculate Tax (5%)
            # ----------------------------
            tax_amount = total_amount * Decimal("0.05")

            # ----------------------------
            # Update Order Totals
            # ----------------------------
            order.tax_amount = tax_amount
            order.total_amount = total_amount + tax_amount

            # ----------------------------
            # Save Items
            # ----------------------------
            db.add_all(order_items)

        # ----------------------------
        # Commit
        # ----------------------------
        db.refresh(order)
        return order

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to create order",
        ) from e