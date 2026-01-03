# ============================================================================
# FILE: servers/transactional_server/models.py - CORRECT VERSION
# ============================================================================
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"

class CreateOrderRequest(BaseModel):
    user_id: int
    product_id: int
    quantity: int

class Order(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    status: OrderStatus
    total_amount: float
    created_at: datetime

class UpdateInventoryRequest(BaseModel):
    product_id: int
    quantity_change: int
    reason: str

class InventoryUpdate(BaseModel):
    product_id: int
    old_quantity: int
    new_quantity: int
    change: int
    reason: str
    timestamp: datetime