from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Order, OrderStatus, Organization, Location, User, UserRole
from app.schemas import (
    OrderCreate, OrderUpdate, 
    OrganizationCreate, OrganizationUpdate,
    LocationCreate, LocationUpdate,
    UserCreate, UserUpdate
)
from app.utils import generate_token
from app.auth import get_password_hash


# ==================== Order CRUD ====================

async def check_duplicate_active_order(
    db: AsyncSession, 
    human_id: str, 
    location_id: UUID
) -> Optional[Order]:
    """Check if there's an active order with same human_id at this location."""
    result = await db.execute(
        select(Order).where(
            and_(
                Order.human_id == human_id,
                Order.location_id == location_id,
                Order.status.in_([
                    OrderStatus.PENDING,
                    OrderStatus.SCANNED,
                    OrderStatus.PREPARING,
                    OrderStatus.READY
                ])
            )
        )
    )
    return result.scalar_one_or_none()


async def create_order(db: AsyncSession, order_data: OrderCreate, location_id: UUID) -> Order:
    """Create a new order. Raises ValueError if duplicate active order exists."""
    # Check for duplicate
    existing = await check_duplicate_active_order(db, order_data.human_id, location_id)
    if existing:
        raise ValueError(f"Заказ {order_data.human_id} уже существует и ещё активен")
    
    token = generate_token()
    
    order = Order(
        human_id=order_data.human_id,
        device_id=order_data.device_id,
        location_id=location_id,
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
    location_id: Optional[UUID] = None,
    organization_id: Optional[UUID] = None,
    limit: int = 100
) -> List[Order]:
    """Get list of orders with optional filters."""
    query = select(Order).order_by(Order.created_at.desc()).limit(limit)
    
    if status:
        query = query.where(Order.status == status)
    
    if location_id:
        query = query.where(Order.location_id == location_id)
    
    if organization_id:
        # Join with locations to filter by organization
        query = query.join(Location).where(Location.organization_id == organization_id)
    
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


async def get_active_orders(
    db: AsyncSession, 
    device_id: Optional[str] = None,
    location_id: Optional[UUID] = None,
    organization_id: Optional[UUID] = None
) -> List[Order]:
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
    
    if location_id:
        query = query.where(Order.location_id == location_id)
    
    if organization_id:
        query = query.join(Location).where(Location.organization_id == organization_id)
    
    result = await db.execute(query.order_by(Order.created_at.desc()))
    return list(result.scalars().all())


# ==================== Organization CRUD ====================

async def create_organization(db: AsyncSession, org_data: OrganizationCreate) -> Organization:
    """Create a new organization."""
    org = Organization(
        name=org_data.name,
        slug=org_data.slug,
        logo_url=org_data.logo_url,
        is_demo=org_data.is_demo
    )
    
    db.add(org)
    await db.commit()
    await db.refresh(org)
    
    return org


async def get_organization_by_id(db: AsyncSession, org_id: UUID) -> Optional[Organization]:
    """Get organization by ID."""
    result = await db.execute(
        select(Organization)
        .options(selectinload(Organization.locations))
        .where(Organization.id == org_id)
    )
    return result.scalar_one_or_none()


async def get_organization_by_slug(db: AsyncSession, slug: str) -> Optional[Organization]:
    """Get organization by slug."""
    result = await db.execute(select(Organization).where(Organization.slug == slug))
    return result.scalar_one_or_none()


async def get_organizations(db: AsyncSession, include_inactive: bool = False) -> List[Organization]:
    """Get all organizations."""
    query = select(Organization).options(selectinload(Organization.locations))
    
    if not include_inactive:
        query = query.where(Organization.is_active == True)
    
    result = await db.execute(query.order_by(Organization.name))
    return list(result.scalars().all())


async def update_organization(
    db: AsyncSession, 
    org_id: UUID, 
    org_data: OrganizationUpdate
) -> Optional[Organization]:
    """Update organization."""
    org = await get_organization_by_id(db, org_id)
    
    if not org:
        return None
    
    update_data = org_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(org, field, value)
    
    await db.commit()
    await db.refresh(org)
    
    return org


# ==================== Location CRUD ====================

async def create_location(db: AsyncSession, loc_data: LocationCreate) -> Location:
    """Create a new location."""
    location = Location(
        organization_id=loc_data.organization_id,
        name=loc_data.name,
        slug=loc_data.slug,
        mall_name=loc_data.mall_name,
        city=loc_data.city,
        address=loc_data.address
    )
    
    db.add(location)
    await db.commit()
    await db.refresh(location)
    
    return location


async def get_location_by_id(db: AsyncSession, loc_id: UUID) -> Optional[Location]:
    """Get location by ID."""
    result = await db.execute(
        select(Location)
        .options(selectinload(Location.organization))
        .where(Location.id == loc_id)
    )
    return result.scalar_one_or_none()


async def get_locations_by_organization(
    db: AsyncSession, 
    org_id: UUID,
    include_inactive: bool = False
) -> List[Location]:
    """Get all locations for an organization."""
    query = select(Location).where(Location.organization_id == org_id)
    
    if not include_inactive:
        query = query.where(Location.is_active == True)
    
    result = await db.execute(query.order_by(Location.name))
    return list(result.scalars().all())


async def get_all_active_locations_with_org(db: AsyncSession) -> List[dict]:
    """Get all active locations with organization names for public display setup."""
    query = (
        select(Location, Organization.name.label('org_name'))
        .join(Organization, Location.organization_id == Organization.id)
        .where(Location.is_active == True)
        .where(Organization.is_active == True)
        .order_by(Organization.name, Location.name)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    return [
        {
            "id": row.Location.id,
            "name": row.Location.name,
            "mall_name": row.Location.mall_name,
            "city": row.Location.city,
            "organization_name": row.org_name
        }
        for row in rows
    ]


async def update_location(
    db: AsyncSession, 
    loc_id: UUID, 
    loc_data: LocationUpdate
) -> Optional[Location]:
    """Update location."""
    location = await get_location_by_id(db, loc_id)
    
    if not location:
        return None
    
    update_data = loc_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(location, field, value)
    
    await db.commit()
    await db.refresh(location)
    
    return location


# ==================== User CRUD ====================

async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    """Create a new user."""
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role,
        organization_id=user_data.organization_id,
        location_id=user_data.location_id
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """Get user by ID with relationships."""
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.organization),
            selectinload(User.location)
        )
        .where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Get user by username."""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_users_by_organization(
    db: AsyncSession, 
    org_id: UUID,
    include_inactive: bool = False
) -> List[User]:
    """Get all users for an organization."""
    query = select(User).where(User.organization_id == org_id)
    
    if not include_inactive:
        query = query.where(User.is_active == True)
    
    result = await db.execute(query.order_by(User.username))
    return list(result.scalars().all())


async def get_users_by_location(
    db: AsyncSession, 
    loc_id: UUID,
    include_inactive: bool = False
) -> List[User]:
    """Get all users for a location."""
    query = select(User).where(User.location_id == loc_id)
    
    if not include_inactive:
        query = query.where(User.is_active == True)
    
    result = await db.execute(query.order_by(User.username))
    return list(result.scalars().all())


async def update_user(
    db: AsyncSession, 
    user_id: UUID, 
    user_data: UserUpdate
) -> Optional[User]:
    """Update user."""
    user = await get_user_by_id(db, user_id)
    
    if not user:
        return None
    
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    
    return user


async def update_user_password(db: AsyncSession, user_id: UUID, new_password: str) -> bool:
    """Update user password."""
    user = await get_user_by_id(db, user_id)
    
    if not user:
        return False
    
    user.hashed_password = get_password_hash(new_password)
    await db.commit()
    
    return True


async def update_user_last_login(db: AsyncSession, user_id: UUID) -> None:
    """Update user's last login timestamp."""
    from datetime import datetime
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(last_login=datetime.utcnow())
    )
    await db.commit()
