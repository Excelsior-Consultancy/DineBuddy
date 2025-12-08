from sqlalchemy.orm import Session, joinedload
from app.models.restaurant import Restaurant
from app.schemas.restaurant import RestaurantCreate

class RestaurantService:
    """
    Service for Restaurant model - provides instance methods for creation and retrieval of restaurants.
    """
    def create(self, db: Session, restaurant_create: RestaurantCreate) -> Restaurant:
        restaurant = Restaurant(name=restaurant_create.name)
        db.add(restaurant)
        db.commit()
        db.refresh(restaurant)
        return restaurant

    def get_by_id(self, db: Session, restaurant_id: int) -> Restaurant:
        return db.query(Restaurant)\
            .options(joinedload(Restaurant.categories).joinedload('menu_items'))\
            .filter(Restaurant.id == restaurant_id).first()

    def get_all(self, db: Session):
        return db.query(Restaurant)\
            .options(joinedload(Restaurant.categories).joinedload('menu_items'))\
            .all()
