from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID

from app.models import OrderStatus


class OrderCreate(BaseModel):
    """Schema for creating a new order."""
    human_id: str = Field(..., min_length=1, max_length=50, description="Human-readable order ID (e.g., 'A-47')")
    device_id: str = Field(..., min_length=1, max_length=100, description="Display device ID")


class OrderUpdate(BaseModel):
    """Schema for updating order status."""
    status: OrderStatus


class OrderResponse(BaseModel):
    """Schema for order response."""
    id: UUID
    human_id: str
    status: OrderStatus
    token: str
    device_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OrderPublicResponse(BaseModel):
    """Public schema for client tracking (without sensitive data)."""
    human_id: str
    status: OrderStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


class WebSocketMessage(BaseModel):
    """Base WebSocket message schema."""
    type: str
    data: dict


class QRDisplayMessage(BaseModel):
    """Message to display QR code."""
    type: str = "SHOW_QR"
    url: str
    human_id: str
    timeout: int = 30


class StatusUpdateMessage(BaseModel):
    """Message for status update."""
    type: str = "STATUS_UPDATE"
    status: OrderStatus
    human_id: str
