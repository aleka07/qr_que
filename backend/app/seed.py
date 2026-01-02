"""
Seed script to create initial data: admin user, demo organization with locations.

Run with:
    python -m app.seed
"""

import asyncio
import logging
from datetime import datetime
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import AsyncSessionLocal, engine, Base
from app.models import User, Organization, Location, UserRole
from app.auth import get_password_hash
from app.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


async def create_tables():
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Tables created")


async def seed_admin(db: AsyncSession) -> User:
    """Create admin user if not exists."""
    result = await db.execute(select(User).where(User.username == settings.admin_username))
    admin = result.scalar_one_or_none()
    
    if admin:
        logger.info(f"Admin user '{settings.admin_username}' already exists")
        return admin
    
    admin = User(
        id=uuid.uuid4(),
        username=settings.admin_username,
        email="admin@qrque.local",
        hashed_password=get_password_hash(settings.admin_password),
        full_name="System Administrator",
        role=UserRole.ADMIN,
        organization_id=None,  # Admin has no organization
        location_id=None,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    
    logger.info(f"Created admin user: {admin.username}")
    return admin


async def seed_demo_organization(db: AsyncSession) -> tuple:
    """Create demo organization with locations and users."""
    
    # Check if demo org exists
    result = await db.execute(select(Organization).where(Organization.slug == "demo"))
    demo_org = result.scalar_one_or_none()
    
    if demo_org:
        logger.info("Demo organization already exists")
        # Get demo user
        result = await db.execute(select(User).where(User.username == settings.demo_username))
        demo_user = result.scalar_one_or_none()
        # Get locations
        result = await db.execute(select(Location).where(Location.organization_id == demo_org.id))
        locations = list(result.scalars().all())
        return demo_org, locations, demo_user
    
    # Create demo organization
    demo_org = Organization(
        id=uuid.uuid4(),
        name="Demo Restaurant",
        slug="demo",
        logo_url=None,
        is_active=True,
        is_demo=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(demo_org)
    await db.flush()
    
    logger.info(f"Created demo organization: {demo_org.name}")
    
    # Create demo locations
    locations_data = [
        {
            "name": "Demo - ТРЦ Mega Almaty",
            "slug": "demo-mega-almaty",
            "mall_name": "Mega Almaty",
            "city": "Almaty",
            "address": "ул. Розыбакиева, 247А"
        },
        {
            "name": "Demo - ТРЦ Dostyk Plaza",
            "slug": "demo-dostyk-plaza",
            "mall_name": "Dostyk Plaza",
            "city": "Almaty",
            "address": "пр. Достык, 111"
        },
        {
            "name": "Demo - ТРЦ Khan Shatyr",
            "slug": "demo-khan-shatyr",
            "mall_name": "Khan Shatyr",
            "city": "Astana",
            "address": "пр. Туран, 37"
        }
    ]
    
    locations = []
    for loc_data in locations_data:
        location = Location(
            id=uuid.uuid4(),
            organization_id=demo_org.id,
            name=loc_data["name"],
            slug=loc_data["slug"],
            mall_name=loc_data["mall_name"],
            city=loc_data["city"],
            address=loc_data["address"],
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(location)
        locations.append(location)
        logger.info(f"Created location: {location.name}")
    
    await db.flush()
    
    # Create demo owner user
    demo_owner = User(
        id=uuid.uuid4(),
        username=settings.demo_username,
        email="demo@qrque.local",
        hashed_password=get_password_hash(settings.demo_password),
        full_name="Demo Owner",
        role=UserRole.OWNER,
        organization_id=demo_org.id,
        location_id=None,  # Owner can access all locations
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(demo_owner)
    
    logger.info(f"Created demo owner user: {demo_owner.username}")
    
    # Create staff users for each location
    for i, location in enumerate(locations):
        staff_user = User(
            id=uuid.uuid4(),
            username=f"demo_staff_{i+1}",
            email=f"staff{i+1}@demo.qrque.local",
            hashed_password=get_password_hash("staff123"),
            full_name=f"Demo Staff {i+1}",
            role=UserRole.STAFF,
            organization_id=demo_org.id,
            location_id=location.id,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(staff_user)
        logger.info(f"Created staff user: {staff_user.username} for {location.name}")
    
    await db.commit()
    
    return demo_org, locations, demo_owner


async def seed_sample_organization(db: AsyncSession) -> None:
    """Create a sample real organization to demonstrate multi-tenant capability."""
    
    # Check if sample org exists
    result = await db.execute(select(Organization).where(Organization.slug == "kfc-sample"))
    sample_org = result.scalar_one_or_none()
    
    if sample_org:
        logger.info("Sample organization already exists")
        return
    
    # Create sample organization
    sample_org = Organization(
        id=uuid.uuid4(),
        name="KFC Kazakhstan (Sample)",
        slug="kfc-sample",
        logo_url=None,
        is_active=True,
        is_demo=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(sample_org)
    await db.flush()
    
    logger.info(f"Created sample organization: {sample_org.name}")
    
    # Create sample locations
    locations_data = [
        {
            "name": "KFC - Mega Almaty",
            "slug": "kfc-mega-almaty",
            "mall_name": "Mega Almaty",
            "city": "Almaty",
            "address": "ул. Розыбакиева, 247А, фудкорт"
        },
        {
            "name": "KFC - Esentai Mall",
            "slug": "kfc-esentai",
            "mall_name": "Esentai Mall",
            "city": "Almaty",
            "address": "пр. Аль-Фараби, 77/8"
        }
    ]
    
    locations = []
    for loc_data in locations_data:
        location = Location(
            id=uuid.uuid4(),
            organization_id=sample_org.id,
            name=loc_data["name"],
            slug=loc_data["slug"],
            mall_name=loc_data["mall_name"],
            city=loc_data["city"],
            address=loc_data["address"],
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(location)
        locations.append(location)
        logger.info(f"Created location: {location.name}")
    
    await db.flush()
    
    # Create owner for this organization
    owner = User(
        id=uuid.uuid4(),
        username="kfc_owner",
        email="owner@kfc-sample.local",
        hashed_password=get_password_hash("kfc123"),
        full_name="KFC Owner",
        role=UserRole.OWNER,
        organization_id=sample_org.id,
        location_id=None,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(owner)
    logger.info(f"Created owner user: {owner.username}")
    
    await db.commit()


async def main():
    """Main seed function."""
    logger.info("Starting seed process...")
    
    # Create tables
    await create_tables()
    
    async with AsyncSessionLocal() as db:
        # Create admin
        admin = await seed_admin(db)
        
        # Create demo organization
        demo_org, demo_locations, demo_user = await seed_demo_organization(db)
        
        # Create sample organization
        await seed_sample_organization(db)
    
    logger.info("=" * 50)
    logger.info("Seed completed successfully!")
    logger.info("=" * 50)
    logger.info("")
    logger.info("Created accounts:")
    logger.info("")
    logger.info("🔑 ADMIN (can see everything):")
    logger.info(f"   Username: {settings.admin_username}")
    logger.info(f"   Password: {settings.admin_password}")
    logger.info("")
    logger.info("🎭 DEMO (demo organization owner):")
    logger.info(f"   Username: {settings.demo_username}")
    logger.info(f"   Password: {settings.demo_password}")
    logger.info("")
    logger.info("👥 DEMO STAFF (one per location):")
    logger.info("   Username: demo_staff_1, demo_staff_2, demo_staff_3")
    logger.info("   Password: staff123")
    logger.info("")
    logger.info("🏢 SAMPLE KFC OWNER:")
    logger.info("   Username: kfc_owner")
    logger.info("   Password: kfc123")
    logger.info("")


if __name__ == "__main__":
    asyncio.run(main())
