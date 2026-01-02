from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from uuid import UUID

from app.models import OrderStatus, UserRole


# ==================== Auth Schemas ====================

class Token(BaseModel):
    """JWT Token response."""
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class TokenData(BaseModel):
    """Token payload data."""
    user_id: Optional[UUID] = None
    username: Optional[str] = None
    role: Optional[UserRole] = None


class LoginRequest(BaseModel):
    """Login request schema."""
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)


# ==================== Organization Schemas ====================

class OrganizationCreate(BaseModel):
    """Schema for creating an organization."""
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=50, pattern=r'^[a-z0-9-]+$')
    logo_url: Optional[str] = None
    is_demo: bool = False


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization."""
    name: Optional[str] = Field(None, max_length=100)
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None


class OrganizationResponse(BaseModel):
    """Schema for organization response."""
    id: UUID
    name: str
    slug: str
    logo_url: Optional[str]
    is_active: bool
    is_demo: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrganizationWithLocations(OrganizationResponse):
    """Organization with locations list."""
    locations: List["LocationResponse"] = []


# ==================== Location Schemas ====================

class LocationCreate(BaseModel):
    """Schema for creating a location."""
    organization_id: UUID
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=50, pattern=r'^[a-z0-9-]+$')
    mall_name: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None


class LocationUpdate(BaseModel):
    """Schema for updating a location."""
    name: Optional[str] = Field(None, max_length=100)
    mall_name: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    is_active: Optional[bool] = None


class LocationResponse(BaseModel):
    """Schema for location response."""
    id: UUID
    organization_id: UUID
    name: str
    slug: str
    mall_name: Optional[str]
    city: Optional[str]
    address: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class LocationWithOrganization(LocationResponse):
    """Location with organization details."""
    organization: OrganizationResponse


class LocationPublicResponse(BaseModel):
    """Public location info for display setup (no auth required)."""
    id: UUID
    name: str
    mall_name: Optional[str]
    city: Optional[str]
    organization_name: str
    
    class Config:
        from_attributes = True


# ==================== User Schemas ====================

class UserCreate(BaseModel):
    """Schema for creating a user."""
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = Field(None, max_length=100)
    role: UserRole = UserRole.STAFF
    organization_id: Optional[UUID] = None
    location_id: Optional[UUID] = None


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    location_id: Optional[UUID] = None


class UserPasswordUpdate(BaseModel):
    """Schema for password change."""
    current_password: str
    new_password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    """Schema for user response."""
    id: UUID
    username: str
    email: Optional[str]
    full_name: Optional[str]
    role: UserRole
    organization_id: Optional[UUID]
    location_id: Optional[UUID]
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserWithDetails(UserResponse):
    """User with organization and location details."""
    organization: Optional[OrganizationResponse] = None
    location: Optional[LocationResponse] = None


# ==================== Order Schemas ====================

class OrderCreate(BaseModel):
    """Schema for creating a new order."""
    human_id: str = Field(..., min_length=1, max_length=50, description="Human-readable order ID (e.g., 'A-47')")
    device_id: str = Field(..., min_length=1, max_length=100, description="Display device ID")
    location_id: Optional[UUID] = None  # Can be inferred from auth


class OrderUpdate(BaseModel):
    """Schema for updating order status."""
    status: OrderStatus


class OrderResponse(BaseModel):
    """Schema for order response."""
    id: UUID
    location_id: Optional[UUID]
    human_id: str
    status: OrderStatus
    token: str
    device_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OrderWithLocation(OrderResponse):
    """Order with location details."""
    location: LocationResponse


class OrderPublicResponse(BaseModel):
    """Public schema for client tracking (without sensitive data)."""
    human_id: str
    status: OrderStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== WebSocket Schemas ====================

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


# Update forward references
OrganizationWithLocations.model_rebuild()
Token.model_rebuild()
