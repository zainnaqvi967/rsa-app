"""
Test script to verify database models and relationships.

Run this script to create sample data and test the database setup.
"""

from backend.database import SessionLocal, init_db
from backend.models import (
    User, UserRole,
    ProviderProfile,
    ServiceRequest, ServiceType, VehicleType, RequestStatus,
    Offer, OfferStatus,
    Job, JobStatus
)


def test_database_setup():
    """Test database initialization and model creation."""
    print("🧪 Testing database setup...")
    
    # Initialize database
    init_db()
    print("✅ Database initialized")
    
    # Create a session
    db = SessionLocal()
    
    try:
        # Test 1: Create a customer user
        print("\n📝 Creating customer user...")
        customer = User(
            name="John Doe",
            phone="+1234567890",
            role=UserRole.CUSTOMER
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
        print(f"✅ Customer created: {customer}")
        
        # Test 2: Create a provider user with profile
        print("\n📝 Creating provider user...")
        provider = User(
            name="Jane Mechanic",
            phone="+0987654321",
            role=UserRole.PROVIDER
        )
        db.add(provider)
        db.commit()
        db.refresh(provider)
        
        provider_profile = ProviderProfile(
            user_id=provider.id,
            city="San Francisco",
            services_offered="flat_tyre,jump_start,fuel",
            vehicle_types="both",
            is_verified=True,
            current_lat=37.7749,
            current_lng=-122.4194,
            is_online=True
        )
        db.add(provider_profile)
        db.commit()
        db.refresh(provider_profile)
        print(f"✅ Provider created: {provider}")
        print(f"✅ Provider profile created: {provider_profile}")
        
        # Test 3: Create a service request
        print("\n📝 Creating service request...")
        service_request = ServiceRequest(
            customer_id=customer.id,
            service_type=ServiceType.FLAT_TYRE,
            vehicle_type=VehicleType.CAR,
            description="Flat tire on Highway 101",
            price_offered=75.0,
            lat=37.7849,
            lng=-122.4094,
            status=RequestStatus.PENDING_OFFERS
        )
        db.add(service_request)
        db.commit()
        db.refresh(service_request)
        print(f"✅ Service request created: {service_request}")
        
        # Test 4: Create an offer
        print("\n📝 Creating offer...")
        offer = Offer(
            service_request_id=service_request.id,
            provider_id=provider.id,
            price=65.0,
            eta_minutes=15,
            status=OfferStatus.PENDING
        )
        db.add(offer)
        db.commit()
        db.refresh(offer)
        print(f"✅ Offer created: {offer}")
        
        # Test 5: Accept offer and create job
        print("\n📝 Accepting offer and creating job...")
        offer.status = OfferStatus.ACCEPTED
        service_request.status = RequestStatus.OFFER_SELECTED
        
        job = Job(
            service_request_id=service_request.id,
            offer_id=offer.id,
            status=JobStatus.ASSIGNED
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        print(f"✅ Job created: {job}")
        
        # Test 6: Query relationships
        print("\n🔍 Testing relationships...")
        
        # Get customer with their requests
        customer_from_db = db.query(User).filter(User.id == customer.id).first()
        print(f"\nCustomer: {customer_from_db.name}")
        print(f"  Requests: {len(customer_from_db.service_requests)}")
        
        # Get provider with their profile
        provider_from_db = db.query(User).filter(User.id == provider.id).first()
        print(f"\nProvider: {provider_from_db.name}")
        print(f"  Profile: {provider_from_db.provider_profile}")
        print(f"  Offers: {len(provider_from_db.offers)}")
        
        # Get service request with offers
        request_from_db = db.query(ServiceRequest).filter(ServiceRequest.id == service_request.id).first()
        print(f"\nService Request #{request_from_db.id}")
        print(f"  Status: {request_from_db.status}")
        print(f"  Offers: {len(request_from_db.offers)}")
        print(f"  Job: {request_from_db.job}")
        
        print("\n✅ All tests passed! Database models are working correctly.")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        db.rollback()
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    test_database_setup()

