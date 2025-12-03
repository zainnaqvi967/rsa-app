"""
Security Utilities
==================
This module handles password hashing and JWT token operations.

For beginners:
- NEVER store plain text passwords! Always hash them.
- A "hash" is a one-way transformation. You can't reverse it.
- JWT (JSON Web Token) is how we keep users logged in without sessions.

How JWT works:
1. User logs in with email/password
2. Server creates a JWT containing user info (id, role)
3. Server sends JWT to client
4. Client includes JWT in every request (Authorization header)
5. Server verifies JWT and knows who the user is

The JWT is like a "signed badge" - the server can verify it's authentic
because only the server knows the SECRET_KEY used to sign it.
"""

from datetime import datetime, timedelta
from typing import Optional, Any

# Password hashing library
from passlib.context import CryptContext

# JWT library
from jose import JWTError, jwt

# Our settings
from app.core.config import settings


# ====================
# PASSWORD HASHING
# ====================
# CryptContext handles password hashing using bcrypt algorithm
# bcrypt is slow by design - this makes brute-force attacks harder

pwd_context = CryptContext(
    schemes=["bcrypt"],  # Use bcrypt algorithm
    deprecated="auto"    # Automatically handle old hash formats
)


def hash_password(password: str) -> str:
    """
    Hash a plain text password.
    
    Args:
        password: The plain text password from user input
    
    Returns:
        The hashed password (safe to store in database)
    
    Example:
        >>> hash_password("mypassword123")
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G5Q3H5Q3H5Q3H5'
    
    The same password will produce DIFFERENT hashes each time
    (due to random "salt"), but verify_password will still work!
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: The password the user typed in
        hashed_password: The hash stored in the database
    
    Returns:
        True if password matches, False otherwise
    
    Example:
        >>> hashed = hash_password("mypassword123")
        >>> verify_password("mypassword123", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)


# ====================
# JWT TOKEN OPERATIONS
# ====================

def create_access_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary with data to encode in the token
              Typically includes: {"sub": user_id, "role": "customer"}
        expires_delta: How long until the token expires
                      If not provided, uses default from settings
    
    Returns:
        The encoded JWT token string
    
    How the token looks (decoded):
    {
        "sub": "123",           # Subject (user ID)
        "role": "customer",     # User's role
        "exp": 1699999999       # Expiration timestamp
    }
    
    The actual token is a long encoded string like:
    eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM...
    """
    # Copy the data so we don't modify the original
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Add expiration to the token data
    to_encode.update({"exp": expire})
    
    # Create the JWT token
    # jwt.encode() creates the token string
    encoded_jwt = jwt.encode(
        to_encode,                    # Data to encode
        settings.JWT_SECRET_KEY,      # Secret key for signing
        algorithm=settings.JWT_ALGORITHM  # Algorithm (HS256)
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    """
    Decode and verify a JWT access token.
    
    Args:
        token: The JWT token string from Authorization header
    
    Returns:
        The decoded token data (dict) if valid, None if invalid
    
    This function:
    1. Checks the token signature (was it signed with our secret?)
    2. Checks if token is expired
    3. Returns the payload if everything is valid
    
    Example:
        >>> data = decode_access_token("eyJhbGciOiJIUzI1...")
        >>> print(data)
        {"sub": "123", "role": "customer", "exp": 1699999999}
    """
    try:
        # jwt.decode() verifies signature and expiration automatically
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        # Token is invalid (bad signature, expired, malformed, etc.)
        return None


def create_token_for_user(user_id: int, role: str) -> str:
    """
    Convenience function to create a token for a user.
    
    Args:
        user_id: The user's database ID
        role: The user's role (customer, provider, admin)
    
    Returns:
        JWT access token
    
    Example:
        >>> token = create_token_for_user(user_id=123, role="customer")
    """
    token_data = {
        "sub": str(user_id),  # "sub" is standard JWT claim for subject
        "role": role
    }
    return create_access_token(token_data)

