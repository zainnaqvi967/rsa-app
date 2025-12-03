"""
Seed script to populate the database with demo users for testing.

Usage:
    python seed.py
"""

from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine, Base
from backend.models import User, ProviderProfile
from datetime import datetime


def seed_database():
    """Create demo users for all roles."""
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    try:
        print("\n🌱 Seeding database with demo users...\n")
        
        # Check if users already exist
        existing_admin = db.query(User).filter(User.phone == "+923001234567").first()
        if existing_admin:
            print("⚠️  Demo users already exist. Delete roadside_assistance.db to reseed.\n")
            return
        
        # 1. Create Admin User
        admin_user = User(
            name="Admin User",
            phone="+923001234567",
            role="admin",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(admin_user)
        db.flush()
        print(f"✅ Admin User Created")
        print(f"   Phone: {admin_user.phone}")
        print(f"   Name: {admin_user.name}")
        print(f"   Role: {admin_user.role}\n")
        
        # 2. Create Provider User with Profile
        provider_user = User(
            name="Ali Mechanic",
            phone="+923009876543",
            role="provider",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(provider_user)
        db.flush()
        
        provider_profile = ProviderProfile(
            user_id=provider_user.id,
            city="Islamabad",
            services_offered="flat_tyre,jump_start,fuel,tow,key_lock",
            vehicle_types="both",
            is_verified=True,
            average_rating=4.8,
            total_ratings=24,
            current_lat=33.6844,  # Islamabad coordinates
            current_lng=73.0479,
            is_online=True
        )
        db.add(provider_profile)
        print(f"✅ Provider User Created")
        print(f"   Phone: {provider_user.phone}")
        print(f"   Name: {provider_user.name}")
        print(f"   Role: {provider_user.role}")
        print(f"   City: {provider_profile.city}")
        print(f"   Location: {provider_profile.current_lat}, {provider_profile.current_lng}")
        print(f"   Services: {provider_profile.services_offered}")
        print(f"   Online: {provider_profile.is_online}")
        print(f"   Verified: {provider_profile.is_verified}\n")
        
        # 3. Create Customer User
        customer_user = User(
            name="Sara Khan",
            phone="+923111234567",
            role="customer",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(customer_user)
        db.flush()
        print(f"✅ Customer User Created")
        print(f"   Phone: {customer_user.phone}")
        print(f"   Name: {customer_user.name}")
        print(f"   Role: {customer_user.role}\n")
        
        # Commit all changes
        db.commit()
        
        print("=" * 60)
        print("🎉 Database seeded successfully!\n")
        print("📱 Login Credentials (OTP is always: 1234)")
        print("=" * 60)
        print(f"Admin:    {admin_user.phone}")
        print(f"Provider: {provider_user.phone}")
        print(f"Customer: {customer_user.phone}")
        print("=" * 60)
        print("\n💡 Quick Test:")
        print("1. Start backend: uvicorn main:app --reload")
        print("2. Start frontend: cd client && npm run dev")
        print("3. Login with any phone above using OTP: 1234")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

