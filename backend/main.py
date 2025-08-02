from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime
from typing import Optional

from routers import strategy, backtest, market_data
from database import engine, Base
from config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("🚀 Database tables created")
    yield
    print("📴 Application shutdown")

app = FastAPI(
    title="Korean Stock Backtesting API",
    description="API for Korean stock strategy backtesting with KOSPI/KOSDAQ data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(strategy.router, prefix="/api/v1/strategy", tags=["Strategy"])
app.include_router(backtest.router, prefix="/api/v1/backtest", tags=["Backtest"])
app.include_router(market_data.router, prefix="/api/v1/market-data", tags=["Market Data"])

@app.get("/")
async def root():
    return {
        "message": "Korean Stock Backtesting API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )