from fastapi import APIRouter
<<<<<<< HEAD
from app.api.v1.endpoints import health, restaurant, user_restaurant, menu_category, menu_items, menu_item_variant,user, auth
=======
from app.api.v1.endpoints import health, restaurant, user_restaurant, menu_category, menu_items, menu_item_variant
>>>>>>> Quick-availability-toggle

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(restaurant.router, tags=["restaurant"])
api_router.include_router(user_restaurant.router, tags=["user_restaurant"])
api_router.include_router(menu_category.router, tags=["menu_category"])
api_router.include_router(menu_items.router, tags=["menu_items"])
api_router.include_router(menu_item_variant.router, tags=["menu_item_variant"])
api_router.include_router(user.router, tags=["Users"])
api_router.include_router(auth.router, tags=["auth"])