#!/usr/bin/env python3
"""
Local development server for Korean Stock Backtesting App
Run this script to start the development environment without Docker
"""

import sys
import subprocess
import os
from pathlib import Path

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    # Basic dependencies for MVP
    basic_deps = [
        "fastapi",
        "uvicorn[standard]",
        "pydantic",
        "sqlalchemy",
        "pandas",
        "requests",
        "python-dotenv"
    ]
    
    try:
        for dep in basic_deps:
            print(f"Installing {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
        
        # Try to install Korean stock data libraries
        try:
            print("Installing FinanceDataReader...")
            subprocess.run([sys.executable, "-m", "pip", "install", "FinanceDataReader"], check=True)
        except:
            print("⚠️  Warning: FinanceDataReader installation failed")
        
        try:
            print("Installing pykrx...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pykrx"], check=True)
        except:
            print("⚠️  Warning: pykrx installation failed")
            
        print("✅ Dependencies installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_database():
    """Create SQLite database"""
    print("🗄️  Setting up database...")
    
    # Change to backend directory
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    # Create a simple database setup script
    db_setup = '''
import sqlite3
import sys
import os

# Add current directory to path for imports
sys.path.append(os.getcwd())

try:
    from database import init_db, test_db_connection
    
    print("Creating database tables...")
    init_db()
    
    if test_db_connection():
        print("✅ Database setup successful!")
    else:
        print("❌ Database connection test failed")
        
except Exception as e:
    print(f"Database setup error: {e}")
    # Create basic SQLite database as fallback
    conn = sqlite3.connect("stock_backtesting.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Basic SQLite database created")
'''
    
    with open("setup_db.py", "w", encoding="utf-8") as f:
        f.write(db_setup)
    
    try:
        subprocess.run([sys.executable, "setup_db.py"], check=True)
        return True
    except Exception as e:
        print(f"Database setup error: {e}")
        return False

def start_backend():
    """Start FastAPI backend server"""
    print("🚀 Starting backend server...")
    
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    # Create a simplified main.py for local development
    simple_main = '''
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime

app = FastAPI(
    title="Korean Stock Backtesting API - Local Dev",
    description="Simplified API for local development",
    version="1.0.0-dev"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Korean Stock Backtesting API - Local Development",
        "version": "1.0.0-dev",
        "timestamp": datetime.now().isoformat(),
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "mode": "local_development"
    }

@app.get("/api/v1/stocks")
async def get_sample_stocks():
    """Sample stock data for testing"""
    return [
        {"symbol": "005930", "name": "삼성전자", "market": "KOSPI"},
        {"symbol": "000660", "name": "SK하이닉스", "market": "KOSPI"},
        {"symbol": "035420", "name": "NAVER", "market": "KOSPI"},
        {"symbol": "051910", "name": "LG화학", "market": "KOSPI"},
        {"symbol": "068270", "name": "셀트리온", "market": "KOSPI"}
    ]

@app.get("/api/v1/market-data/overview")
async def get_market_overview():
    """Sample market overview"""
    return {
        "total_stocks": 5,
        "active_stocks": 5,
        "latest_data_date": "2025-07-31",
        "status": "sample_data"
    }

if __name__ == "__main__":
    print("🚀 Starting Korean Stock Backtesting API...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
'''
    
    with open("main_simple.py", "w", encoding="utf-8") as f:
        f.write(simple_main)
    
    print("📖 API Documentation will be available at: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("📊 Sample Stock Data: http://localhost:8000/api/v1/stocks")
    print("🛑 Press Ctrl+C to stop the server")
    
    try:
        subprocess.run([sys.executable, "main_simple.py"])
    except KeyboardInterrupt:
        print("\\n🛑 Server stopped")

def main():
    """Main function to set up and run local development environment"""
    print("🇰🇷 Korean Stock Backtesting App - Local Development Setup")
    print("=" * 60)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies. Exiting.")
        return
    
    print("\\n" + "=" * 60)
    print("🎉 Setup complete! Starting development server...")
    print("=" * 60)
    
    # Start backend server
    start_backend()

if __name__ == "__main__":
    main()