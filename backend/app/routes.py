from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
import logging

from app.database import get_db
from app.models import OrderStatus
from app.schemas import (
    OrderCreate,
    OrderResponse,
    OrderPublicResponse,
    OrderUpdate,
    QRDisplayMessage,
    StatusUpdateMessage
)
from app import crud
from app.websocket import manager
from app.utils import generate_tracking_url

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/orders", response_model=OrderResponse, status_code=201)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new order and notify the display device to show QR code.
    """
    try:
        # Create order in database
        order = await crud.create_order(db, order_data)
        
        # Generate tracking URL
        tracking_url = generate_tracking_url(order.token)
        
        # Send QR display command to specific display
        qr_message = QRDisplayMessage(
            url=tracking_url,
            human_id=order.human_id,
            timeout=30
        )
        await manager.send_to_display(order.device_id, qr_message.dict())
        
        # Broadcast new order to all staff
        await manager.broadcast_to_staff({
            "type": "NEW_ORDER",
            "order": OrderResponse.model_validate(order).model_dump(mode='json')
        })
        
        logger.info(f"Created order {order.human_id} with token {order.token}")
        
        return order
    
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders", response_model=List[OrderResponse])
async def get_orders(
    status: OrderStatus = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of orders with optional status filter.
    """
    orders = await crud.get_orders(db, status=status)
    return orders


@router.get("/orders/active", response_model=List[OrderResponse])
async def get_active_orders(
    device_id: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all active orders (pending, scanned, preparing, ready).
    Optional device_id filter.
    """
    orders = await crud.get_active_orders(db, device_id=device_id)
    return orders


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get order by ID.
    """
    order = await crud.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/track/{token}", response_model=OrderPublicResponse)
async def track_order(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get order status by client token (public endpoint).
    """
    order = await crud.get_order_by_token(db, token)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return OrderPublicResponse(
        human_id=order.human_id,
        status=order.status,
        created_at=order.created_at
    )


@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: UUID,
    status_update: OrderUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update order status and notify connected clients.
    """
    # Get current order to check status change
    current_order = await crud.get_order_by_id(db, order_id)
    if not current_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    old_status = current_order.status
    
    order = await crud.update_order_status(db, order_id, status_update.status)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # If status changed from pending to scanned - clear QR on display
    if old_status == OrderStatus.PENDING and status_update.status == OrderStatus.SCANNED:
        await manager.send_to_display(order.device_id, {
            "type": "CLEAR_QR"
        })
    
    # Notify client via WebSocket
    status_message = StatusUpdateMessage(
        status=order.status,
        human_id=order.human_id
    )
    await manager.send_to_client(order.token, status_message.dict())
    
    # Notify all staff
    await manager.broadcast_to_staff({
        "type": "STATUS_UPDATE",
        "order": OrderResponse.model_validate(order).model_dump(mode='json')
    })
    
    logger.info(f"Updated order {order.human_id} to status {order.status}")
    
    return order


@router.websocket("/ws/staff")
async def websocket_staff(websocket: WebSocket):
    """
    WebSocket endpoint for staff dashboard.
    Receives updates about all orders.
    """
    await manager.connect_staff(websocket)
    try:
        while True:
            # Keep connection alive, listen for pings
            data = await websocket.receive_text()
            # Echo back for ping/pong
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect_staff(websocket)
        logger.info("Staff disconnected")


@router.websocket("/ws/display/{device_id}")
async def websocket_display(websocket: WebSocket, device_id: str):
    """
    WebSocket endpoint for display devices.
    Receives commands to show QR codes.
    """
    await manager.connect_display(device_id, websocket)
    try:
        while True:
            # Keep connection alive, listen for acknowledgments
            data = await websocket.receive_text()
            logger.debug(f"Display {device_id} sent: {data}")
    except WebSocketDisconnect:
        manager.disconnect_display(device_id)
        logger.info(f"Display {device_id} disconnected")


@router.websocket("/ws/client/{token}")
async def websocket_client(websocket: WebSocket, token: str):
    """
    WebSocket endpoint for client tracking.
    Receives status updates for their specific order.
    """
    await manager.connect_client(token, websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect_client(token)
        logger.info(f"Client {token} disconnected")
