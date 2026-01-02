"""Authentication and account management routes."""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, UserRole
from app.schemas import (
    Token, LoginRequest, 
    UserCreate, UserUpdate, UserResponse, UserWithDetails, UserPasswordUpdate,
    OrganizationCreate, OrganizationUpdate, OrganizationResponse, OrganizationWithLocations,
    LocationCreate, LocationUpdate, LocationResponse, LocationWithOrganization
)
from app import crud
from app.auth import (
    authenticate_user, create_access_token, get_password_hash, verify_password,
    get_current_user_required, get_current_admin, get_current_owner_or_admin,
    get_current_manager_or_above, check_organization_access, check_location_access
)
from app.config import get_settings

settings = get_settings()

router = APIRouter()


# ==================== Auth Routes ====================

@router.post("/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login and get access token."""
    user = await authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    await crud.update_user_last_login(db, user.id)
    
    # Create token
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "username": user.username,
            "role": user.role.value
        }
    )
    
    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/auth/login/json", response_model=Token)
async def login_json(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login with JSON body and get access token."""
    user = await authenticate_user(db, login_data.username, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Update last login
    await crud.update_user_last_login(db, user.id)
    
    # Create token
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "username": user.username,
            "role": user.role.value
        }
    )
    
    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.get("/auth/me", response_model=UserWithDetails)
async def get_current_user_info(
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db)
):
    """Get current user information with details."""
    user = await crud.get_user_by_id(db, current_user.id)
    return user


@router.put("/auth/password")
async def change_password(
    password_data: UserPasswordUpdate,
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db)
):
    """Change current user's password."""
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    await crud.update_user_password(db, current_user.id, password_data.new_password)
    
    return {"message": "Password updated successfully"}


# ==================== Organization Routes ====================

@router.post("/organizations", response_model=OrganizationResponse, status_code=201)
async def create_organization(
    org_data: OrganizationCreate,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new organization (admin only)."""
    # Check if slug already exists
    existing = await crud.get_organization_by_slug(db, org_data.slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization with this slug already exists"
        )
    
    org = await crud.create_organization(db, org_data)
    return org


@router.get("/organizations", response_model=List[OrganizationWithLocations])
async def get_organizations(
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db)
):
    """Get organizations (admin sees all, others see only their own)."""
    if current_user.role == UserRole.ADMIN:
        return await crud.get_organizations(db, include_inactive=True)
    elif current_user.organization_id:
        org = await crud.get_organization_by_id(db, current_user.organization_id)
        return [org] if org else []
    return []


@router.get("/organizations/{org_id}", response_model=OrganizationWithLocations)
async def get_organization(
    org_id: UUID,
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db)
):
    """Get organization by ID."""
    if not check_organization_access(current_user, org_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    org = await crud.get_organization_by_id(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return org


@router.patch("/organizations/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: UUID,
    org_data: OrganizationUpdate,
    current_user: User = Depends(get_current_owner_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update organization (admin or owner only)."""
    if current_user.role != UserRole.ADMIN and current_user.organization_id != org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    org = await crud.update_organization(db, org_id, org_data)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return org


# ==================== Location Routes ====================

@router.post("/locations", response_model=LocationResponse, status_code=201)
async def create_location(
    loc_data: LocationCreate,
    current_user: User = Depends(get_current_owner_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new location (admin or owner only)."""
    # Check organization access
    if current_user.role != UserRole.ADMIN:
        if current_user.organization_id != loc_data.organization_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    location = await crud.create_location(db, loc_data)
    return location


@router.get("/locations", response_model=List[LocationResponse])
async def get_locations(
    organization_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db)
):
    """Get locations (filtered by access)."""
    # Admin can see all
    if current_user.role == UserRole.ADMIN:
        if organization_id:
            return await crud.get_locations_by_organization(db, organization_id, include_inactive=True)
        # Return all locations for all organizations
        orgs = await crud.get_organizations(db, include_inactive=True)
        locations = []
        for org in orgs:
            locs = await crud.get_locations_by_organization(db, org.id, include_inactive=True)
            locations.extend(locs)
        return locations
    
    # Owner can see all their organization's locations
    if current_user.role == UserRole.OWNER and current_user.organization_id:
        return await crud.get_locations_by_organization(
            db, current_user.organization_id, include_inactive=True
        )
    
    # Manager/Staff can only see their location
    if current_user.location_id:
        location = await crud.get_location_by_id(db, current_user.location_id)
        return [location] if location else []
    
    return []


@router.get("/locations/{loc_id}", response_model=LocationWithOrganization)
async def get_location(
    loc_id: UUID,
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db)
):
    """Get location by ID."""
    location = await crud.get_location_by_id(db, loc_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    if not check_location_access(current_user, loc_id):
        # For owner, also check organization
        if current_user.role == UserRole.OWNER:
            if location.organization_id != current_user.organization_id:
                raise HTTPException(status_code=403, detail="Access denied")
        else:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return location


@router.patch("/locations/{loc_id}", response_model=LocationResponse)
async def update_location(
    loc_id: UUID,
    loc_data: LocationUpdate,
    current_user: User = Depends(get_current_owner_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update location (admin or owner only)."""
    location = await crud.get_location_by_id(db, loc_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    if current_user.role != UserRole.ADMIN:
        if location.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    location = await crud.update_location(db, loc_id, loc_data)
    return location


# ==================== User Management Routes ====================

@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_owner_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new user (admin or owner only)."""
    # Check if username already exists
    existing = await crud.get_user_by_username(db, user_data.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Non-admin can only create users in their organization
    if current_user.role != UserRole.ADMIN:
        if user_data.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Can only create users in your organization")
        
        # Owner can't create admin users
        if user_data.role == UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Cannot create admin users")
        
        # Owner can't create owner for other organizations
        if user_data.role == UserRole.OWNER and user_data.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Cannot create owner for other organizations")
    
    user = await crud.create_user(db, user_data)
    return user


@router.get("/users", response_model=List[UserResponse])
async def get_users(
    organization_id: Optional[UUID] = None,
    location_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_manager_or_above),
    db: AsyncSession = Depends(get_db)
):
    """Get users (filtered by access)."""
    # Admin can see all
    if current_user.role == UserRole.ADMIN:
        if location_id:
            return await crud.get_users_by_location(db, location_id, include_inactive=True)
        if organization_id:
            return await crud.get_users_by_organization(db, organization_id, include_inactive=True)
        # Return all users - this could be a lot, consider pagination
        from sqlalchemy import select
        result = await db.execute(select(User).order_by(User.username))
        return list(result.scalars().all())
    
    # Owner can see all users in their organization
    if current_user.role == UserRole.OWNER and current_user.organization_id:
        return await crud.get_users_by_organization(
            db, current_user.organization_id, include_inactive=True
        )
    
    # Manager can see users in their location
    if current_user.role == UserRole.MANAGER and current_user.location_id:
        return await crud.get_users_by_location(db, current_user.location_id, include_inactive=True)
    
    return []


@router.get("/users/{user_id}", response_model=UserWithDetails)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_manager_or_above),
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID."""
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check access
    if current_user.role != UserRole.ADMIN:
        if user.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return user


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_owner_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update user (admin or owner only)."""
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Non-admin can only update users in their organization
    if current_user.role != UserRole.ADMIN:
        if user.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    updated_user = await crud.update_user(db, user_id, user_data)
    return updated_user


@router.put("/users/{user_id}/password")
async def reset_user_password(
    user_id: UUID,
    password_data: UserPasswordUpdate,
    current_user: User = Depends(get_current_owner_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Reset user password (admin or owner only)."""
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Non-admin can only reset passwords in their organization
    if current_user.role != UserRole.ADMIN:
        if user.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    await crud.update_user_password(db, user_id, password_data.new_password)
    
    return {"message": "Password reset successfully"}
