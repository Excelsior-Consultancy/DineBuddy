from sqlalchemy.orm import Session
from app.models.restaurant import Restaurant

class RestaurantService:
    """
    Service for Restaurant model - provides instance methods for creation and retrieval of restaurants.
    """
    def create(self, db: Session, name: str) -> Restaurant:
        restaurant = Restaurant(name=name)
        db.add(restaurant)
        db.commit()
        db.refresh(restaurant)
        return restaurant

    def get_by_id(self, db: Session, restaurant_id: int) -> Restaurant:
        return db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()

    def get_all(self, db: Session):
        return db.query(Restaurant).all()
