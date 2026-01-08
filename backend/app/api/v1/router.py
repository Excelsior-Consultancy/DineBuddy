"""
Main API router that aggregates all endpoint routers
"""
from fastapi import APIRouter

from app.api.v1.endpoints import health, restaurant, user_restaurant, menu_category, menu_items

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(restaurant.router, tags=["restaurant"])
api_router.include_router(user_restaurant.router, tags=["user_restaurant"])
api_router.include_router(menu_category.router, tags=["menu_category"])
api_router.include_router(menu_items.router, tags=["menu_items"])


# Future routers will be added here:
# api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
# api_router.include_router(menu.router, prefix="/menu", tags=["menu"])
# api_router.include_router(orders.router, prefix="/orders", tags=["orders"])