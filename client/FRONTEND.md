# 🎨 Frontend Setup Guide

## Overview

The frontend is built with **Next.js 14**, **TypeScript**, **Tailwind CSS**, and **Axios** for API communication. It includes authentication, role-based routing, and a mobile-first design.

---

## 🚀 Getting Started

### Prerequisites

- **Node.js 18+** and npm
- Backend API running on `http://localhost:8000`

### Installation

```bash
cd client
npm install
```

### Development Server

```bash
npm run dev
```

Visit: **http://localhost:3000**

---

## 📁 Project Structure

```
client/
├── src/
│   └── app/
│       ├── layout.tsx          # Root layout with AuthProvider
│       ├── page.tsx            # Home/landing page
│       ├── login/
│       │   └── page.tsx        # Login with OTP
│       ├── customer/
│       │   └── page.tsx        # Customer dashboard
│       ├── provider/
│       │   └── page.tsx        # Provider dashboard
│       └── admin/
│           └── page.tsx        # Admin dashboard
│
├── components/
│   └── Layout.tsx              # Reusable layout component
│
├── context/
│   └── AuthContext.tsx         # Authentication state management
│
├── hooks/
│   └── useAuth.ts              # Authentication hook
│
├── lib/
│   └── api.ts                  # API client with axios
│
├── tailwind.config.ts          # Tailwind configuration
├── tsconfig.json               # TypeScript configuration
└── package.json                # Dependencies
```

---

## 🔐 Authentication System

### AuthContext

Manages authentication state globally using React Context:

```typescript
// context/AuthContext.tsx
interface User {
  id: number;
  name: string | null;
  phone: string;
  role: 'customer' | 'provider' | 'admin';
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (token: string, user: User) => void;
  logout: () => void;
  isLoading: boolean;
}
```

**Features:**
- ✅ Persists to localStorage
- ✅ Auto-loads on app init
- ✅ Provides to all components via Context

### useAuth Hook

Convenient hook for accessing auth state:

```typescript
import { useAuth } from '@/hooks/useAuth';

function MyComponent() {
  const {
    user,
    token,
    login,
    logout,
    isLoading,
    isAuthenticated,
    isCustomer,
    isProvider,
    isAdmin
  } = useAuth();

  // Use auth state and helpers
}
```

### Login Flow

1. User enters phone number
2. Backend sends OTP (demo: always "1234")
3. User enters OTP and optional name
4. Backend verifies and returns JWT + user data
5. Frontend stores in localStorage
6. User redirected to role-based dashboard

---

## 🌐 API Integration

### API Client (`lib/api.ts`)

Axios instance with automatic token injection:

```typescript
import api from '@/lib/api';

// Token is automatically attached from localStorage
const response = await api.get('/customer/active-request');
```

**Features:**
- ✅ Base URL configuration
- ✅ Auto-attaches Bearer token
- ✅ Handles 401 errors (redirects to login)
- ✅ Pre-configured API methods

### Pre-configured API Methods

```typescript
import { authAPI, customerAPI, providerAPI, adminAPI } from '@/lib/api';

// Authentication
await authAPI.requestOTP(phone);
await authAPI.verifyOTP(phone, otp, name);

// Customer
await customerAPI.createServiceRequest(data);
await customerAPI.getActiveRequest();
await customerAPI.acceptOffer(offerId);

// Provider
await providerAPI.getNearbyRequests(radiusKm);
await providerAPI.createOffer(data);
await providerAPI.updateJobStatus(jobId, status);

// Admin
await adminAPI.getUsers(role);
await adminAPI.getProviders();
await adminAPI.updateProviderVerification(profileId, isVerified);
```

---

## 🎨 Layout System

### Layout Component

Provides consistent layout with:
- Mobile-first design (`max-w-md`)
- Centered content
- Header with user info and logout
- Responsive navigation

```tsx
import Layout from '@/components/Layout';

export default function MyPage() {
  return (
    <Layout>
      <h1>My Content</h1>
    </Layout>
  );
}
```

**Props:**
- `children` - Page content
- `showHeader` - Show/hide header (default: true)

---

## 🎯 Pages

### Home Page (`/`)

- **Purpose:** Landing page for unauthenticated users
- **Features:**
  - Hero section
  - "Login / Continue" button
  - Service overview
  - How it works explanation
- **Auto-redirect:** Logged-in users redirect to their dashboard

### Login Page (`/login`)

- **Purpose:** Phone + OTP authentication
- **Features:**
  - Two-step form (phone → OTP)
  - Shows demo OTP for development
  - Optional name field for new users
  - Error handling
- **Flow:**
  1. Enter phone → Request OTP
  2. Enter OTP (1234) → Verify
  3. Redirect to role dashboard

### Customer Dashboard (`/customer`)

- **Protected:** Requires customer role
- **Purpose:** Customer service request management
- **Coming Soon:**
  - Create service requests
  - View and accept offers
  - Track active jobs

### Provider Dashboard (`/provider`)

- **Protected:** Requires provider role
- **Purpose:** Provider job and offer management
- **Coming Soon:**
  - View nearby requests
  - Send offers
  - Manage active jobs
  - Update profile

### Admin Dashboard (`/admin`)

- **Protected:** Requires admin role
- **Purpose:** System monitoring and management
- **Coming Soon:**
  - View all users
  - Verify providers
  - Monitor requests and jobs
  - System analytics

---

## 🛡️ Route Protection

All dashboard pages use role-based protection:

```tsx
export default function CustomerDashboard() {
  const router = useRouter();
  const { isAuthenticated, isCustomer, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && (!isAuthenticated || !isCustomer)) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, isCustomer, router]);

  // Component content
}
```

---

## 🎨 Styling with Tailwind CSS

### Configuration

Tailwind is configured in `tailwind.config.ts`:

```typescript
const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      // Custom colors, fonts, etc.
    },
  },
  plugins: [],
};
```

### Common Patterns

**Button:**
```tsx
<button className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg shadow-lg">
  Click Me
</button>
```

**Card:**
```tsx
<div className="bg-white rounded-lg shadow-md p-6">
  <h3 className="font-semibold text-gray-900 mb-2">Title</h3>
  <p className="text-gray-600">Content</p>
</div>
```

**Input:**
```tsx
<input
  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
  type="text"
  placeholder="Enter text"
/>
```

---

## ⚙️ Environment Variables

Create `.env.local`:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Access in code:
```typescript
const apiUrl = process.env.NEXT_PUBLIC_API_URL;
```

---

## 🧪 Testing the Frontend

### 1. Start Backend

```bash
cd backend
uvicorn main:app --reload
```

### 2. Start Frontend

```bash
cd client
npm run dev
```

### 3. Test Login Flow

1. Go to http://localhost:3000
2. Click "Login / Continue"
3. Enter phone: `+1234567890`
4. Click "Request OTP"
5. Enter OTP: `1234`
6. Enter name (optional)
7. Click "Verify & Login"
8. You'll be redirected to customer dashboard

### 4. Test Different Roles

To test provider or admin roles, manually update the user in the database:

```sql
-- Make user a provider
UPDATE users SET role = 'provider' WHERE phone = '+1234567890';

-- Make user an admin
UPDATE users SET role = 'admin' WHERE phone = '+1234567890';
```

Then login again to get new token with updated role.

---

## 📱 Mobile-First Design

The app uses a mobile-first approach:

- **Max width:** `max-w-md` (448px)
- **Centered:** `mx-auto`
- **Responsive:** Scales well on all devices
- **Touch-friendly:** Large tap targets (44px+)

### Example:

```tsx
<main className="max-w-md mx-auto px-4 py-6">
  {/* Mobile-optimized content */}
</main>
```

---

## 🚀 Deployment

### Build for Production

```bash
npm run build
npm run start
```

### Environment Variables (Production)

Update `.env.production`:

```bash
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

### Deployment Platforms

- **Vercel:** Automatic deployment from Git
- **Netlify:** Static site hosting
- **Docker:** Custom deployment

---

## 🔜 Next Steps

### Customer Features
1. Create service request form
2. View active request with offers
3. Accept offer functionality
4. Job tracking with provider location
5. Request history

### Provider Features
1. Profile setup and editing
2. Location tracking
3. Nearby requests map/list
4. Send offer form
5. Active jobs management
6. Job status updates

### Admin Features
1. User management table
2. Provider verification interface
3. Request monitoring
4. Job tracking
5. System analytics dashboard

### General Improvements
1. Real-time updates (WebSocket)
2. Push notifications
3. Error boundaries
4. Loading states
5. Form validation
6. Toast notifications
7. Map integration (Google Maps)
8. Payment integration

---

## 🛠️ Available Scripts

```bash
npm run dev        # Start development server
npm run build      # Build for production
npm run start      # Start production server
npm run lint       # Run ESLint
```

---

## 📚 Key Dependencies

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "next": "14.0.4",
    "axios": "^1.6.2"
  },
  "devDependencies": {
    "typescript": "^5.3.3",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "@types/react": "^18.2.45",
    "@types/node": "^20.10.5"
  }
}
```

---

## ✨ Features Implemented

✅ **Authentication System**
- Phone + OTP login
- JWT token management
- localStorage persistence
- Auto token injection

✅ **Role-Based Routing**
- Customer, Provider, Admin roles
- Protected routes
- Auto-redirect based on role

✅ **API Integration**
- Axios client
- Pre-configured methods
- Error handling
- Token refresh on 401

✅ **UI Components**
- Responsive layout
- Mobile-first design
- Tailwind CSS styling
- Loading states

✅ **Pages**
- Landing page
- Login page
- Role dashboards

**The frontend foundation is complete and ready for feature development! 🎉**

