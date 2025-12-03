# 🚀 Quick Start Guide

## Installation Requirements

Before you begin, ensure you have the following installed:

### 1. Python 3.11+
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
  - Make sure to check "Add Python to PATH" during installation
- **macOS**: Use Homebrew: `brew install python@3.11`
- **Linux**: Use your package manager: `sudo apt install python3.11`

Verify installation:
```bash
python --version
# or
python3 --version
```

### 2. Node.js 18+ and npm
- **Windows/macOS/Linux**: Download from [nodejs.org](https://nodejs.org/)
  
Verify installation:
```bash
node --version
npm --version
```

## 🔧 Running the Application

### Backend (FastAPI)

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create a virtual environment:**

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the server:**
```bash
uvicorn main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc

### Frontend (Next.js)

1. **Navigate to client directory:**
```bash
cd client
```

2. **Install dependencies:**
```bash
npm install
```

3. **Run the development server:**
```bash
npm run dev
```

The frontend will be available at: **http://localhost:3000**

## ✅ Testing the Setup

1. Start the backend (in one terminal)
2. Start the frontend (in another terminal)
3. Open http://localhost:3000 in your browser
4. You should see the "Roadside Assistance Marketplace" home page
5. The page will show the API status (it should connect to the backend automatically)

## 🐛 Troubleshooting

### Backend Issues

**"uvicorn: command not found"**
- Make sure you activated the virtual environment
- Run `pip install -r requirements.txt` again

**"Port 8000 already in use"**
- Use a different port: `uvicorn main:app --reload --port 8001`

### Frontend Issues

**"npm: command not found"**
- Install Node.js from nodejs.org

**"Port 3000 already in use"**
- Next.js will automatically prompt to use port 3001

**Backend connection fails**
- Make sure the backend is running on port 8000
- Check CORS settings in `backend/main.py`

## 📚 Next Development Steps

1. **Database Models** - Define SQLAlchemy models in `backend/models/`
2. **API Schemas** - Create Pydantic schemas in `backend/schemas/`
3. **API Routes** - Add endpoints in `backend/routers/`
4. **Frontend Pages** - Build UI components and pages in `client/src/`
5. **Authentication** - Implement user auth system
6. **Real-time Features** - Add WebSocket support for live updates

## 🎯 Project Structure

```
RSA/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── requirements.txt     # Python dependencies
│   ├── models/              # Database models (SQLAlchemy)
│   │   └── __init__.py
│   ├── schemas/             # Request/response schemas (Pydantic)
│   │   └── __init__.py
│   └── routers/             # API endpoints
│       └── __init__.py
│
├── client/
│   ├── src/
│   │   └── app/
│   │       ├── page.tsx     # Home page
│   │       ├── layout.tsx   # Root layout
│   │       └── globals.css  # Global styles
│   ├── package.json         # Node.js dependencies
│   ├── tsconfig.json        # TypeScript config
│   ├── tailwind.config.ts   # Tailwind config
│   └── next.config.js       # Next.js config
│
└── README.md                # This file
```

Happy coding! 🎉

