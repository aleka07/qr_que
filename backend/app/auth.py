"""Authentication module with JWT token handling."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import get_settings
from app.database import get_db
from app.models import User, UserRole
from app.schemas import TokenData

settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    
    return encoded_jwt


def decode_token(token: str) -> Optional[TokenData]:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        username: str = payload.get("username")
        role: str = payload.get("role")
        
        if user_id is None:
            return None
            
        return TokenData(
            user_id=UUID(user_id),
            username=username,
            role=UserRole(role) if role else None
        )
    except JWTError:
        return None


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Get user by username."""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """Get user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """Authenticate user with username and password."""
    user = await get_user_by_username(db, username)
    
    if not user:
        return None
    if not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    
    return user


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get current user from JWT token (optional - returns None if not authenticated)."""
    if not token:
        return None
    
    token_data = decode_token(token)
    if token_data is None or token_data.user_id is None:
        return None
    
    user = await get_user_by_id(db, token_data.user_id)
    if user is None or not user.is_active:
        return None
    
    return user


async def get_current_user_required(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    """Get current user - raises exception if not authenticated."""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


async def get_current_admin(
    current_user: User = Depends(get_current_user_required)
) -> User:
    """Get current user - must be admin."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_current_owner_or_admin(
    current_user: User = Depends(get_current_user_required)
) -> User:
    """Get current user - must be owner or admin."""
    if current_user.role not in [UserRole.ADMIN, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner or admin access required"
        )
    return current_user


async def get_current_manager_or_above(
    current_user: User = Depends(get_current_user_required)
) -> User:
    """Get current user - must be manager, owner, or admin."""
    if current_user.role not in [UserRole.ADMIN, UserRole.OWNER, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access or above required"
        )
    return current_user


def check_location_access(user: User, location_id: UUID) -> bool:
    """Check if user has access to a specific location."""
    # Admin can access everything
    if user.role == UserRole.ADMIN:
        return True
    
    # Owner can access all locations in their organization
    if user.role == UserRole.OWNER:
        # This will be checked in the route with organization check
        return True
    
    # Manager/Staff can only access their assigned location
    if user.location_id == location_id:
        return True
    
    return False


def check_organization_access(user: User, organization_id: UUID) -> bool:
    """Check if user has access to a specific organization."""
    # Admin can access everything
    if user.role == UserRole.ADMIN:
        return True
    
    # Others can only access their own organization
    if user.organization_id == organization_id:
        return True
    
    return False
