import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.database import Base


class OrderStatus(str, enum.Enum):
    """Order status enum."""
    PENDING = "pending"      # Создан, QR показан
    SCANNED = "scanned"      # Клиент отсканировал QR
    PREPARING = "preparing"  # В процессе приготовления
    READY = "ready"          # Готов к выдаче
    COMPLETED = "completed"  # Выдан клиенту
    CANCELLED = "cancelled"  # Отменен


class Order(Base):
    """Order model for digital pager system."""
    
    __tablename__ = "orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    human_id = Column(String(50), nullable=False, index=True)  # "A-47", "B-12", etc.
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    token = Column(String(50), unique=True, nullable=False, index=True)  # Unique token for client
    device_id = Column(String(100), nullable=False, index=True)  # ID планшета кассы
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Order(id={self.id}, human_id={self.human_id}, status={self.status})>"
