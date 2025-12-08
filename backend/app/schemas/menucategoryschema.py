from pydantic import BaseModel

class MenuCategoryCreate(BaseModel):
    name: str
    restaurant_id: int

class MenuCategoryRead(BaseModel):
    id: int
    name: str
    restaurant_id: int

    class Config:
        orm_mode = True