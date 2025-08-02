#!/usr/bin/env python3
"""
Simple local development server for Korean Stock Backtesting App
"""

import sys
import subprocess
import os

def install_basic_deps():
    """Install minimal dependencies"""
    deps = ["fastapi", "uvicorn"]
    
    for dep in deps:
        print(f"Installing {dep}...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
        except:
            print(f"Failed to install {dep}")

def create_simple_server():
    """Create a simple FastAPI server"""
    server_code = '''
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Korean Stock Backtesting API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Korean Stock Backtesting API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/v1/stocks")
async def get_stocks():
    return [
        {"symbol": "005930", "name": "Samsung Electronics", "market": "KOSPI"},
        {"symbol": "000660", "name": "SK Hynix", "market": "KOSPI"},
        {"symbol": "035420", "name": "NAVER", "market": "KOSPI"}
    ]

if __name__ == "__main__":
    print("Starting Korean Stock Backtesting API...")
    print("API Docs: http://localhost:8000/docs")
    print("Press Ctrl+C to stop")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
'''
    
    with open("simple_server.py", "w") as f:
        f.write(server_code)

def main():
    print("Korean Stock Backtesting App - Local Setup")
    print("=" * 50)
    
    install_basic_deps()
    create_simple_server()
    
    print("Starting server...")
    subprocess.run([sys.executable, "simple_server.py"])

if __name__ == "__main__":
    main()