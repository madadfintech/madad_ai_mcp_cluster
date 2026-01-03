from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class User(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

class UserResponse(BaseModel):
    users: List[User]
    total: int

class ProductQuery(BaseModel):
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None

class Product(BaseModel):
    id: int
    name: str
    category: str
    price: float
    in_stock: bool