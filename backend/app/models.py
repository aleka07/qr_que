import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class UserRole(str, enum.Enum):
    """User role enum."""
    ADMIN = "admin"           # Супер-админ, видит всё
    OWNER = "owner"           # Владелец сети (организации)
    MANAGER = "manager"       # Менеджер точки
    STAFF = "staff"           # Персонал точки (касса)


class OrderStatus(str, enum.Enum):
    """Order status enum."""
    PENDING = "pending"      # Создан, QR показан
    SCANNED = "scanned"      # Клиент отсканировал QR
    PREPARING = "preparing"  # В процессе приготовления
    READY = "ready"          # Готов к выдаче
    COMPLETED = "completed"  # Выдан клиенту
    CANCELLED = "cancelled"  # Отменен


class Organization(Base):
    """Organization (network/chain) model - e.g., 'KFC', 'Burger King'."""
    
    __tablename__ = "organizations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True, nullable=False, index=True)  # URL-friendly name
    logo_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_demo = Column(Boolean, default=False, nullable=False)  # Demo account flag
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    locations = relationship("Location", back_populates="organization", cascade="all, delete-orphan")
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Organization(id={self.id}, name={self.name})>"


class Location(Base):
    """Location (point of sale) model - specific location in a mall."""
    
    __tablename__ = "locations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(100), nullable=False)  # e.g., "KFC Mega Almaty"
    slug = Column(String(50), nullable=False, index=True)  # URL-friendly name
    mall_name = Column(String(100), nullable=True)  # ТРЦ - e.g., "Mega Almaty"
    city = Column(String(50), nullable=True)  # Город
    address = Column(Text, nullable=True)  # Полный адрес
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="locations")
    orders = relationship("Order", back_populates="location", cascade="all, delete-orphan")
    users = relationship("User", back_populates="location")
    
    def __repr__(self):
        return f"<Location(id={self.id}, name={self.name}, mall={self.mall_name})>"


class User(Base):
    """User model for authentication and authorization."""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)  # NULL for admin
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=True)  # NULL for admin/owner
    
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.STAFF)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    location = relationship("Location", back_populates="users")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"


class Order(Base):
    """Order model for digital pager system."""
    
    __tablename__ = "orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=True)  # Nullable for backward compatibility
    human_id = Column(String(50), nullable=False, index=True)  # "A-47", "B-12", etc.
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    token = Column(String(50), unique=True, nullable=False, index=True)  # Unique token for client
    device_id = Column(String(100), nullable=False, index=True)  # ID планшета кассы
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    location = relationship("Location", back_populates="orders")
    
    def __repr__(self):
        return f"<Order(id={self.id}, human_id={self.human_id}, status={self.status})>"
