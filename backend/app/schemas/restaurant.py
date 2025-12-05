from pydantic import BaseModel

class RestaurantCreate(BaseModel):
    name: str

class RestaurantRead(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
