"""
Database Configuration
======================
This file sets up our connection to the database using SQLAlchemy.

For beginners - here's what's happening:
1. We create an "engine" - this is the connection to our database
2. We create a "SessionLocal" - this is how we talk to the database
3. We create a "Base" class - all our models (tables) will inherit from this
4. We create a "get_db" function - FastAPI uses this to give each request a database session

Think of it like this:
- Engine = The car (connection to database)
- Session = A single trip in the car (one conversation with the database)
- Base = The blueprint all tables are built from
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Import our settings
from app.core.config import settings


# ====================
# STEP 1: CREATE ENGINE
# ====================
# The engine is the starting point for any SQLAlchemy application.
# It's the "home base" for the database connection.

# For SQLite, we need this special setting:
# check_same_thread=False allows multiple threads to use the same connection
# (FastAPI uses multiple threads to handle requests)
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # Only needed for SQLite!
)


# ====================
# STEP 2: CREATE SESSION FACTORY
# ====================
# SessionLocal is a "factory" that creates database sessions.
# Each session is like opening a conversation with the database.

# autocommit=False: We manually control when to save changes (safer)
# autoflush=False: We manually control when to send changes to DB
# bind=engine: Connect sessions to our database engine
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ====================
# STEP 3: CREATE BASE CLASS
# ====================
# Base is the class that all our database models will inherit from.
# When a model inherits from Base, SQLAlchemy knows it's a database table.
#
# Example:
#   class User(Base):
#       __tablename__ = "users"
#       id = Column(Integer, primary_key=True)
#       name = Column(String)

Base = declarative_base()


# ====================
# STEP 4: DEPENDENCY FUNCTION
# ====================
# This is a special function that FastAPI will call for each request.
# It gives each request its own database session, then cleans up after.

def get_db():
    """
    Get a database session for a request.
    
    This is a "generator function" (notice the 'yield' keyword).
    - When a request comes in, it creates a new session
    - The request uses the session to read/write data
    - When the request is done, the session is closed (cleanup)
    
    Usage in FastAPI:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    # Create a new session
    db = SessionLocal()
    try:
        # Give the session to the request
        yield db
    finally:
        # Always close the session when done (cleanup)
        # This runs even if there's an error!
        db.close()


# ====================
# STEP 5: TABLE CREATION FUNCTION
# ====================
def create_tables():
    """
    Create all database tables.
    
    This looks at all classes that inherit from Base and creates
    their tables in the database if they don't exist.
    
    IMPORTANT: We must import all models BEFORE calling this function!
    That's why we import them here - so Base "knows" about them.
    
    Called once when the app starts up (see main.py lifespan).
    """
    # Import all models here so Base knows about them
    # This import registers the models with Base.metadata
    from app.models import User, ServiceRequest  # noqa: F401
    
    # Create all tables that don't exist yet
    # If tables already exist, this does nothing (safe to call multiple times)
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database tables created/verified:")
    print("   - users")
    print("   - service_requests")
