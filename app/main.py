"""
Main Application Entry Point
============================
This is where our FastAPI application starts!

To run this application:
    uvicorn app.main:app --reload

Then open your browser to:
    http://localhost:8000        - Root endpoint
    http://localhost:8000/docs   - Interactive API documentation (Swagger UI)
    http://localhost:8000/redoc  - Alternative documentation (ReDoc)

For beginners:
- FastAPI automatically generates documentation from your code
- The --reload flag makes the server restart when you change code
- 'app.main:app' means "in the app folder, in main.py, use the 'app' variable"
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import our database setup
from app.database import create_tables
from app.core.config import settings

# Import all routers
from app.routers import auth
from app.routers import requests as customer_requests
from app.routers import provider
from app.routers import admin


# ====================
# LIFESPAN EVENTS
# ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    - Code BEFORE 'yield' runs on STARTUP
    - Code AFTER 'yield' runs on SHUTDOWN
    """
    # === STARTUP ===
    print("=" * 60)
    print("🚀 Starting RSA Backend...")
    print(f"📊 Database: {settings.DATABASE_URL}")
    
    # Create all database tables
    create_tables()
    
    print("=" * 60)
    print("✅ Ready to accept requests!")
    print("")
    print("📖 API Documentation:")
    print("   Swagger UI: http://localhost:8000/docs")
    print("   ReDoc:      http://localhost:8000/redoc")
    print("")
    print("🔑 Quick Start:")
    print("   1. POST /admin/setup        → Create admin (one-time)")
    print("   2. POST /auth/register      → Register user")
    print("   3. POST /auth/login         → Get JWT token")
    print("   4. Click 🔒 Authorize       → Enter token")
    print("=" * 60)
    
    yield
    
    # === SHUTDOWN ===
    print("=" * 60)
    print("👋 Shutting down RSA Backend...")
    print("✅ Cleanup complete. Goodbye!")
    print("=" * 60)


# ====================
# CREATE THE APP
# ====================
app = FastAPI(
    title=settings.APP_NAME,
    description="""
## 🚗 Roadside Assistance Platform API

Connect customers who need help with service providers (mechanics, tow trucks, etc.)

---

### 👥 Roles

| Role | What they do |
|------|--------------|
| **Customer** | Create help requests, view offers, track jobs |
| **Provider** | View open requests, accept jobs, update status |
| **Admin** | Monitor platform, manage users |

---

### 🔐 Authentication

1. **Register:** `POST /auth/register` with email, password, role
2. **Login:** `POST /auth/login` to get JWT token
3. **Authorize:** Click the 🔒 button above and enter your token
4. **Use API:** All protected endpoints now work!

---

### 🚀 Quick Test Flows

**Customer Flow:**
```
POST /auth/register (role: customer)
POST /auth/login
POST /requests/              → Create help request
GET  /requests/my            → View your requests
```

**Provider Flow:**
```
POST /auth/register (role: provider)
POST /auth/login
GET  /provider/requests/open           → See available jobs
POST /provider/requests/{id}/accept    → Accept a job
PATCH /provider/requests/{id}/status   → Update progress
```

**Admin Flow:**
```
POST /admin/setup            → Create first admin (one-time)
POST /auth/login             → Login as admin
GET  /admin/requests         → View all requests
GET  /admin/users            → View all users
GET  /admin/stats            → Platform statistics
```
    """,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


# ====================
# CORS MIDDLEWARE
# ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ====================
# INCLUDE ROUTERS
# ====================
# Each router handles a specific area of the API

# Authentication (register, login, me)
app.include_router(auth.router)

# Customer endpoints (create/view requests)
app.include_router(customer_requests.router)

# Provider endpoints (view open, accept, update status)
app.include_router(provider.router)

# Admin endpoints (view all, manage users)
app.include_router(admin.router)


# ====================
# BASIC ENDPOINTS
# ====================
@app.get("/", tags=["Health"])
def root():
    """
    Root endpoint - basic API information.
    """
    return {
        "message": "Welcome to RSA - Roadside Assistance API! 🚗",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "auth": {
                "register": "POST /auth/register",
                "login": "POST /auth/login",
                "me": "GET /auth/me"
            },
            "customer": {
                "create_request": "POST /requests/",
                "my_requests": "GET /requests/my",
                "view_request": "GET /requests/{id}"
            },
            "provider": {
                "open_requests": "GET /provider/requests/open",
                "accept": "POST /provider/requests/{id}/accept",
                "update_status": "PATCH /provider/requests/{id}/status",
                "my_jobs": "GET /provider/requests/my"
            },
            "admin": {
                "setup": "POST /admin/setup",
                "all_requests": "GET /admin/requests",
                "all_users": "GET /admin/users",
                "stats": "GET /admin/stats"
            }
        }
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "rsa-backend"}


# ====================
# FOR DIRECT EXECUTION
# ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
