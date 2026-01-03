from fastapi import APIRouter, HTTPException
from typing import List, Dict
from .models import (CreateOrderRequest, Order, OrderStatus, UpdateInventoryRequest, InventoryUpdate)
from datetime import datetime
from shared.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)

# Mock data storage
ORDERS: List[Order] = []
INVENTORY: Dict[int, int] = {1: 100, 2: 50, 3: 25, 4: 75, 5: 200, 6: 150}
ORDER_COUNTER = 1

@router.post("/orders", response_model=Order)
async def create_order(request: CreateOrderRequest):
    """Create a new order"""
    global ORDER_COUNTER
    
    logger.info("Creating order", user_id=request.user_id, 
               product_id=request.product_id, quantity=request.quantity)
    
    # Check inventory
    if INVENTORY.get(request.product_id, 0) < request.quantity:
        logger.warning("Insufficient inventory", 
                      product_id=request.product_id,
                      requested=request.quantity,
                      available=INVENTORY.get(request.product_id, 0))
        raise HTTPException(400, "Insufficient inventory")
    
    # Decrease inventory
    INVENTORY[request.product_id] -= request.quantity
    
    # Create order
    order = Order(
        id=ORDER_COUNTER,
        user_id=request.user_id,
        product_id=request.product_id,
        quantity=request.quantity,
        status=OrderStatus.PENDING,
        total_amount=request.quantity * 99.99,  # Mock price
        created_at=datetime.now()
    )
    
    ORDERS.append(order)
    ORDER_COUNTER += 1
    
    logger.info("Order created successfully", order_id=order.id)
    return order

@router.put("/orders/{order_id}/status", response_model=Order)
async def update_order_status(order_id: int, status: OrderStatus):
    """Update order status"""
    logger.info("Updating order status", order_id=order_id, new_status=status)
    
    order = next((o for o in ORDERS if o.id == order_id), None)
    if not order:
        logger.warning("Order not found", order_id=order_id)
        raise HTTPException(404, "Order not found")
    
    order.status = status
    logger.info("Order status updated", order_id=order_id, status=status)
    return order

@router.post("/inventory/update", response_model=InventoryUpdate)
async def update_inventory(request: UpdateInventoryRequest):
    """Update product inventory"""
    logger.info("Updating inventory", 
               product_id=request.product_id,
               change=request.quantity_change,
               reason=request.reason)
    
    old_quantity = INVENTORY.get(request.product_id, 0)
    new_quantity = old_quantity + request.quantity_change
    
    if new_quantity < 0:
        logger.warning("Cannot have negative inventory",
                      product_id=request.product_id,
                      would_be=new_quantity)
        raise HTTPException(400, "Cannot have negative inventory")
    
    INVENTORY[request.product_id] = new_quantity
    
    logger.info("Inventory updated successfully",
               product_id=request.product_id,
               old=old_quantity,
               new=new_quantity)
    
    return InventoryUpdate(
        product_id=request.product_id,
        old_quantity=old_quantity,
        new_quantity=new_quantity,
        change=request.quantity_change,
        reason=request.reason,
        timestamp=datetime.now()
    )

@router.delete("/orders/{order_id}")
async def cancel_order(order_id: int):
    """Cancel an order and restore inventory"""
    logger.info("Cancelling order", order_id=order_id)
    
    order = next((o for o in ORDERS if o.id == order_id), None)
    if not order:
        logger.warning("Order not found", order_id=order_id)
        raise HTTPException(404, "Order not found")
    
    if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
        logger.warning("Cannot cancel order in current status",
                      order_id=order_id,
                      status=order.status)
        raise HTTPException(400, "Cannot cancel shipped or delivered order")
    
    # Restore inventory
    INVENTORY[order.product_id] += order.quantity
    
    # Remove order
    ORDERS.remove(order)
    
    logger.info("Order cancelled successfully", order_id=order_id)
    return {"message": "Order cancelled successfully"}