"""
Main FastAPI application for Roadside Assistance Marketplace.

This module initializes the FastAPI app, sets up CORS, database, and routes.
"""

import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.database import init_db
from backend.models import User, ProviderProfile, ServiceRequest, Offer, Job
from backend.deps import get_current_user
from backend.routers import auth, customer, provider, admin
from backend.schemas import UserRead


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for startup and shutdown.
    
    Initializes the database on startup.
    """
    # Startup: Initialize database
    print("🚀 Starting up... Initializing database")
    init_db()
    print("✅ Database initialized successfully")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")


app = FastAPI(
    title="Roadside Assistance Marketplace API",
    description="API for connecting customers with roadside assistance providers",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware to allow frontend requests
# Allow all origins for now (production should be more restrictive)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(customer.router)
app.include_router(provider.router)
app.include_router(admin.router)


@app.get("/")
def read_root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to Roadside Assistance Marketplace API",
        "status": "healthy",
        "version": "0.1.0",
        "docs": "/docs",
        "models": {
            "users": "User authentication and roles",
            "provider_profiles": "Provider service capabilities",
            "service_requests": "Customer assistance requests",
            "offers": "Provider bids on requests",
            "jobs": "Active service delivery tracking"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/models")
def list_models():
    """
    List all available database models and their status.
    
    Returns information about the data model structure.
    """
    return {
        "models": [
            {
                "name": "User",
                "table": "users",
                "description": "Customers, providers, and admins"
            },
            {
                "name": "ProviderProfile",
                "table": "provider_profiles",
                "description": "Provider service details and location"
            },
            {
                "name": "ServiceRequest",
                "table": "service_requests",
                "description": "Customer requests for assistance"
            },
            {
                "name": "Offer",
                "table": "offers",
                "description": "Provider offers on requests"
            },
            {
                "name": "Job",
                "table": "jobs",
                "description": "Active service jobs"
            }
        ]
    }


@app.get("/me", response_model=UserRead)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    This is a protected endpoint that requires a valid JWT token.
    Use this to test authentication.
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
        Current user information
    
    Example:
        ```bash
        curl -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \\
             http://localhost:8000/me
        ```
    """
    return current_user

