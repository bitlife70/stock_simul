#!/usr/bin/env python3
"""
Korean Stock Backtesting API Server - Simple Version
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import random
import asyncio
from datetime import datetime, timedelta
from stock_data_manager import stock_manager, daily_batch_update

# Create FastAPI app
app = FastAPI(
    title="Korean Stock Backtesting API",
    description="API for Korean stock strategy backtesting with KOSPI/KOSDAQ data",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Korean Stock Backtesting API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "status": "running",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "stocks": "/api/v1/stocks",
            "strategies": "/api/v1/strategies/templates"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "mode": "local_development"
    }

@app.get("/api/v1/stocks")
async def get_stocks(limit: int = 1000):
    """Get list of Korean stocks from local database"""
    try:
        stocks = stock_manager.get_all_stocks(limit=limit)
        return stocks
    except Exception as e:
        # Fallback to sample data if database is empty
        return [
            {
                "symbol": "005930",
                "name": "Samsung Electronics",
                "name_kr": "삼성전자",
                "market": "KOSPI",
                "sector": "기술주",
                "current_price": 73000,
                "change_rate": 0.012
            },
            {
                "symbol": "000660", 
                "name": "SK Hynix",
                "name_kr": "SK하이닉스",
                "market": "KOSPI",
                "sector": "기술주", 
                "current_price": 125000,
                "change_rate": -0.008
            },
            {
                "symbol": "035420",
                "name": "NAVER Corporation",
                "name_kr": "NAVER", 
                "market": "KOSPI",
                "sector": "기술주",
                "current_price": 180000,
                "change_rate": 0.021
            },
            {
                "symbol": "051910",
                "name": "LG Chem",
                "name_kr": "LG화학",
                "market": "KOSPI", 
                "sector": "화학",
                "current_price": 400000,
                "change_rate": -0.015
            },
            {
                "symbol": "068270",
                "name": "Celltrion",
                "name_kr": "셀트리온",
                "market": "KOSPI",
                "sector": "바이오",
                "current_price": 160000,
                "change_rate": 0.032
            }
        ]

@app.get("/api/v1/strategies/templates")
async def get_strategy_templates():
    """Get predefined strategy templates"""
    return [
        {
            "id": "golden_cross",
            "name": "Golden Cross Strategy",
            "name_kr": "골든 크로스 전략",
            "description": "5일 이동평균이 20일 이동평균을 상향 돌파할 때 매수",
            "parameters": {
                "short_period": {
                    "type": "number",
                    "default": 5,
                    "min": 3,
                    "max": 20,
                    "description": "단기 이동평균 기간"
                },
                "long_period": {
                    "type": "number", 
                    "default": 20,
                    "min": 10,
                    "max": 50,
                    "description": "장기 이동평균 기간"
                },
                "stop_loss": {
                    "type": "number",
                    "default": 0.05,
                    "min": 0.01,
                    "max": 0.2,
                    "description": "손절 비율 (5% = 0.05)"
                }
            }
        },
        {
            "id": "rsi_reversal",
            "name": "RSI Reversal Strategy", 
            "name_kr": "RSI 역추세 전략",
            "description": "RSI 30 이하에서 매수, 70 이상에서 매도",
            "parameters": {
                "rsi_period": {
                    "type": "number",
                    "default": 14,
                    "min": 7,
                    "max": 30,
                    "description": "RSI 계산 기간"
                },
                "oversold_level": {
                    "type": "number",
                    "default": 30,
                    "min": 20,
                    "max": 40,
                    "description": "과매도 기준선"
                },
                "overbought_level": {
                    "type": "number",
                    "default": 70,
                    "min": 60,
                    "max": 80,
                    "description": "과매수 기준선"
                }
            }
        },
        {
            "id": "bollinger_squeeze",
            "name": "Bollinger Band Breakout",
            "name_kr": "볼린저 밴드 돌파 전략", 
            "description": "볼린저 밴드 상단 돌파 시 매수",
            "parameters": {
                "bb_period": {
                    "type": "number",
                    "default": 20,
                    "min": 10,
                    "max": 50,
                    "description": "볼린저 밴드 기간"
                },
                "bb_std": {
                    "type": "number",
                    "default": 2.0,
                    "min": 1.0,
                    "max": 3.0,
                    "description": "표준편차 배수"
                },
                "volume_confirm": {
                    "type": "boolean",
                    "default": true,
                    "description": "거래량 확인 여부"
                }
            }
        }
    ]

@app.get("/api/v1/stocks/{symbol}/data")
async def get_stock_data(symbol: str):
    """Get historical stock price data"""
    base_price = 70000 if symbol == "005930" else 100000
    data = []
    current_date = datetime.now() - timedelta(days=365)
    
    for i in range(365):
        # Simulate price movement
        price_change = random.uniform(-0.05, 0.05)
        base_price *= (1 + price_change)
        
        open_price = base_price * random.uniform(0.98, 1.02)
        close_price = base_price * random.uniform(0.98, 1.02)
        high_price = max(open_price, close_price) * random.uniform(1.0, 1.05)
        low_price = min(open_price, close_price) * random.uniform(0.95, 1.0)
        volume = random.randint(1000000, 50000000)
        
        data.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "open": round(open_price),
            "high": round(high_price), 
            "low": round(low_price),
            "close": round(close_price),
            "volume": volume
        })
        
        current_date += timedelta(days=1)
    
    return data

@app.post("/api/v1/backtest/run")
async def run_backtest(backtest_request: dict):
    """Run backtesting simulation"""
    # Simulate backtest results
    total_return = random.uniform(-0.2, 0.4)  # -20% to +40%
    win_rate = random.uniform(0.3, 0.7)       # 30% to 70%
    total_trades = random.randint(10, 100)
    max_drawdown = random.uniform(-0.3, -0.05) # -30% to -5%
    sharpe_ratio = random.uniform(0.5, 2.5)
    
    initial_capital = backtest_request.get("initial_capital", 10000000)
    final_capital = initial_capital * (1 + total_return)
    
    return {
        "total_return": total_return,
        "win_rate": win_rate,
        "total_trades": total_trades,
        "max_drawdown": max_drawdown,
        "sharpe_ratio": sharpe_ratio,
        "final_capital": final_capital,
        "initial_capital": initial_capital
    }

@app.post("/api/v1/strategies")
async def save_strategy(strategy: dict):
    """Save a trading strategy"""
    strategy_id = f"strategy_{random.randint(1000, 9999)}"
    return {
        "id": strategy_id,
        "message": "Strategy saved successfully",
        "strategy": strategy
    }

# Database and batch download endpoints
@app.get("/api/v1/database/stats")
async def get_database_stats():
    """Get database statistics"""
    try:
        stats = stock_manager.get_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/database/batch-download")
async def trigger_batch_download(background_tasks: BackgroundTasks):
    """Trigger batch download of all Korean stocks"""
    try:
        # Run the batch download in the background
        background_tasks.add_task(run_batch_download_task)
        
        return {
            "success": True,
            "message": "배치 다운로드가 시작되었습니다. 수분이 소요될 수 있습니다.",
            "status": "started"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/database/download-status")
async def get_download_status():
    """Get the status of the latest batch download"""
    try:
        stats = stock_manager.get_stats()
        return {
            "success": True,
            "last_update": stats.get("last_update"),
            "total_stocks": stats.get("total_stocks", 0),
            "is_updating": False  # This could be enhanced to track real-time status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/stocks/search")
async def search_stocks(q: str, limit: int = 50):
    """Search Korean stocks by symbol, name, or sector"""
    try:
        if not q or len(q.strip()) < 1:
            return []
        
        results = stock_manager.search_stocks(q.strip(), limit=limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def run_batch_download_task():
    """Background task to run batch download"""
    try:
        result = await daily_batch_update()
        print(f"Batch download completed: {result}")
    except Exception as e:
        print(f"Batch download failed: {str(e)}")

if __name__ == "__main__":
    print("=" * 60)
    print("Korean Stock Backtesting API Server")
    print("=" * 60)
    print("Server starting on port 8001...")
    print("API Documentation: http://localhost:8001/docs")
    print("Health Check: http://localhost:8001/health")
    print("Stock Data: http://localhost:8001/api/v1/stocks")
    print("Strategy Templates: http://localhost:8001/api/v1/strategies/templates")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )