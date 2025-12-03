"""
Authentication Router
=====================
This router handles user registration and login.

Endpoints:
- POST /auth/register - Create a new user account
- POST /auth/login    - Login and get JWT token
- GET  /auth/me       - Get current user info (protected)

For beginners:
- These endpoints are the "front door" of your API
- Users must register first, then login to get a token
- The token is used for all other protected endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Our modules
from app.database import get_db
from app.models import User, UserRole
from app.schemas import (
    UserCreate,
    UserLogin,
    UserRead,
    Token,
    TokenWithUser,
)
from app.utils.security import (
    hash_password,
    verify_password,
    create_token_for_user,
)
from app.dependencies import get_current_user


# ====================
# CREATE ROUTER
# ====================
# APIRouter groups related endpoints together
# prefix="/auth" means all routes start with /auth
# tags=["Authentication"] groups them in Swagger UI

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ====================
# REGISTER ENDPOINT
# ====================
@router.post(
    "/register",
    response_model=TokenWithUser,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Email already registered"},
    }
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    **What this endpoint does:**
    1. Check if email is already taken
    2. Hash the password (never store plain text!)
    3. Create the user in database
    4. Generate a JWT token
    5. Return the token and user info
    
    **Request body (UserCreate):**
    - `full_name`: User's full name (required)
    - `email`: Valid email address (required, must be unique)
    - `password`: Password, min 6 characters (required)
    - `phone`: Phone number (optional)
    - `role`: User role - customer/provider/admin (optional, defaults to customer)
    
    **Returns:**
    - `access_token`: JWT token for authentication
    - `token_type`: Always "bearer"
    - `user`: The created user's information (without password)
    
    **Example:**
    ```json
    POST /auth/register
    {
        "full_name": "John Doe",
        "email": "john@example.com",
        "password": "secret123",
        "role": "customer"
    }
    ```
    """
    
    # Step 1: Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered. Please use a different email or login."
        )
    
    # Step 2: Hash the password
    # NEVER store plain text passwords!
    hashed_password = hash_password(user_data.password)
    
    # Step 3: Create the user object
    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        phone=user_data.phone,
        role=user_data.role,
        password_hash=hashed_password
    )
    
    # Step 4: Save to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Refresh to get the auto-generated ID
    
    # Step 5: Create JWT token for the new user
    access_token = create_token_for_user(
        user_id=new_user.id,
        role=new_user.role.value
    )
    
    # Step 6: Return token and user info
    return TokenWithUser(
        access_token=access_token,
        token_type="bearer",
        user=UserRead.model_validate(new_user)
    )


# ====================
# LOGIN ENDPOINT
# ====================
@router.post(
    "/login",
    response_model=TokenWithUser,
    summary="Login to get access token",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid email or password"},
    }
)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login with email and password to get a JWT token.
    
    **What this endpoint does:**
    1. Find user by email
    2. Verify password against stored hash
    3. Generate a JWT token
    4. Return the token and user info
    
    **Request body (UserLogin):**
    - `email`: Your registered email address
    - `password`: Your password
    
    **Returns:**
    - `access_token`: JWT token for authentication
    - `token_type`: Always "bearer"
    - `user`: Your user information
    
    **How to use the token:**
    Include it in the Authorization header of subsequent requests:
    ```
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    ```
    
    **Example:**
    ```json
    POST /auth/login
    {
        "email": "john@example.com",
        "password": "secret123"
    }
    ```
    """
    
    # Step 1: Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    # Step 2: Verify user exists and password matches
    # We use the same error message for both cases (security best practice)
    # This prevents attackers from knowing if an email exists
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Step 3: Create JWT token
    access_token = create_token_for_user(
        user_id=user.id,
        role=user.role.value
    )
    
    # Step 4: Return token and user info
    return TokenWithUser(
        access_token=access_token,
        token_type="bearer",
        user=UserRead.model_validate(user)
    )


# ====================
# GET CURRENT USER ENDPOINT
# ====================
@router.get(
    "/me",
    response_model=UserRead,
    summary="Get current user info",
    responses={
        200: {"description": "Current user information"},
        401: {"description": "Not authenticated"},
    }
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Get the currently logged-in user's information.
    
    **This is a protected endpoint!**
    You must include a valid JWT token in the Authorization header.
    
    **How to call:**
    ```
    GET /auth/me
    Authorization: Bearer <your_token>
    ```
    
    **Returns:**
    User information (id, name, email, role, timestamps)
    
    **Use case:**
    - Frontend can call this on page load to get user info
    - Useful to verify the token is still valid
    - Get updated user info after profile changes
    """
    
    # The dependency already verified the token and loaded the user
    # We just return it!
    return UserRead.model_validate(current_user)

