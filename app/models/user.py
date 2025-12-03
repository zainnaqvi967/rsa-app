"""
User Model
==========
This model represents all users in our system: customers, providers, and admins.

For beginners:
- A "model" is a Python class that represents a database table
- Each instance of the class = one row in the table
- Each attribute of the class = one column in the table

The User model stores:
- Login credentials (email, password hash)
- Profile info (name, phone)
- Role (what type of user they are)
"""

import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, Index
from sqlalchemy.orm import relationship

# Import Base from our database setup
from app.database import Base


# ====================
# USER ROLE ENUM
# ====================
# An Enum is a set of named constants. This ensures 'role' can only be
# one of these three values - no typos like "custmer" or "ADMIN" allowed!

class UserRole(str, enum.Enum):
    """
    Possible roles for a user.
    
    - CUSTOMER: Someone who needs roadside help
    - PROVIDER: Mechanic/tow truck driver who provides help
    - ADMIN: Platform administrator
    """
    CUSTOMER = "customer"
    PROVIDER = "provider"
    ADMIN = "admin"


# ====================
# USER MODEL
# ====================
class User(Base):
    """
    User table - stores all users (customers, providers, admins).
    
    Table name: 'users'
    
    Relationships:
    - One user can create many service requests (as customer)
    - One user can accept many service requests (as provider)
    """
    
    # This is the actual table name in the database
    __tablename__ = "users"
    
    # ====================
    # COLUMNS (Fields)
    # ====================
    
    # Primary Key - unique identifier for each user
    # 'index=True' creates a database index for faster lookups
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Unique identifier for the user"
    )
    
    # User's full name
    # String(100) means max 100 characters
    full_name = Column(
        String(100),
        nullable=False,  # Required field
        comment="User's full name"
    )
    
    # Email address - must be unique (no two users with same email)
    # 'unique=True' enforces this at the database level
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,  # Index for fast email lookups during login
        comment="User's email address (used for login)"
    )
    
    # Phone number - optional but useful for contact
    # String(20) allows international formats like "+1-555-123-4567"
    phone = Column(
        String(20),
        nullable=True,  # Optional field
        comment="User's phone number (optional)"
    )
    
    # User role - uses our Enum defined above
    # 'default=UserRole.CUSTOMER' means new users are customers by default
    role = Column(
        Enum(UserRole),
        nullable=False,
        default=UserRole.CUSTOMER,
        index=True,  # Index for filtering users by role
        comment="User's role: customer, provider, or admin"
    )
    
    # Password hash - NEVER store plain passwords!
    # We store a "hash" which is a one-way encrypted version
    # String(255) because hashes can be long
    password_hash = Column(
        String(255),
        nullable=False,
        comment="Hashed password (never store plain text!)"
    )
    
    # Timestamps - track when records are created/updated
    # 'default=datetime.utcnow' automatically sets the time when created
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="When the user account was created"
    )
    
    # 'onupdate=datetime.utcnow' automatically updates when the record changes
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="When the user account was last updated"
    )
    
    # ====================
    # RELATIONSHIPS
    # ====================
    # Relationships let us easily access related data.
    # They don't create columns - they create convenient Python attributes.
    
    # Service requests created BY this user (as a customer)
    # 'back_populates' creates a two-way link between models
    # 'foreign_keys' specifies which FK to use (since there are two)
    customer_requests = relationship(
        "ServiceRequest",  # The related model (in quotes because it's defined later)
        back_populates="customer",  # The attribute name on ServiceRequest
        foreign_keys="ServiceRequest.customer_id",  # Which FK creates this relationship
        lazy="dynamic"  # Don't load all requests immediately, load when accessed
    )
    
    # Service requests accepted BY this user (as a provider)
    provider_jobs = relationship(
        "ServiceRequest",
        back_populates="provider",
        foreign_keys="ServiceRequest.provider_id",
        lazy="dynamic"
    )
    
    # ====================
    # METHODS
    # ====================
    def __repr__(self):
        """
        String representation of the User.
        This is what you see when you print a User object.
        Useful for debugging!
        """
        return f"<User(id={self.id}, email='{self.email}', role='{self.role.value}')>"
    
    def is_customer(self) -> bool:
        """Check if user is a customer."""
        return self.role == UserRole.CUSTOMER
    
    def is_provider(self) -> bool:
        """Check if user is a provider."""
        return self.role == UserRole.PROVIDER
    
    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == UserRole.ADMIN


# ====================
# TABLE-LEVEL INDEXES
# ====================
# You can also define indexes outside the columns for complex cases
# This creates an index on created_at for sorting users by registration date
Index("ix_users_created_at", User.created_at)

