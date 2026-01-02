from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Order, OrderStatus
from app.schemas import OrderCreate, OrderUpdate
from app.utils import generate_token


async def create_order(db: AsyncSession, order_data: OrderCreate) -> Order:
    """Create a new order."""
    token = generate_token()
    
    order = Order(
        human_id=order_data.human_id,
        device_id=order_data.device_id,
        token=token,
        status=OrderStatus.PENDING
    )
    
    db.add(order)
    await db.commit()
    await db.refresh(order)
    
    return order


async def get_order_by_id(db: AsyncSession, order_id: UUID) -> Optional[Order]:
    """Get order by ID."""
    result = await db.execute(select(Order).where(Order.id == order_id))
    return result.scalar_one_or_none()


async def get_order_by_token(db: AsyncSession, token: str) -> Optional[Order]:
    """Get order by token."""
    result = await db.execute(select(Order).where(Order.token == token))
    return result.scalar_one_or_none()


async def get_orders(
    db: AsyncSession,
    status: Optional[OrderStatus] = None,
    limit: int = 100
) -> List[Order]:
    """Get list of orders with optional status filter."""
    query = select(Order).order_by(Order.created_at.desc()).limit(limit)
    
    if status:
        query = query.where(Order.status == status)
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def update_order_status(
    db: AsyncSession,
    order_id: UUID,
    new_status: OrderStatus
) -> Optional[Order]:
    """Update order status."""
    order = await get_order_by_id(db, order_id)
    
    if not order:
        return None
    
    order.status = new_status
    await db.commit()
    await db.refresh(order)
    
    return order


async def get_active_orders(db: AsyncSession, device_id: Optional[str] = None) -> List[Order]:
    """Get all active orders (not completed or cancelled)."""
    query = select(Order).where(
        Order.status.in_([
            OrderStatus.PENDING,
            OrderStatus.SCANNED,
            OrderStatus.PREPARING,
            OrderStatus.READY
        ])
    )
    
    if device_id:
        query = query.where(Order.device_id == device_id)
    
    result = await db.execute(query.order_by(Order.created_at.desc()))
    return list(result.scalars().all())
