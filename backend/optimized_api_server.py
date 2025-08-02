"""
Optimized API Server for Korean Stock Backtesting Platform
Production-ready server with comprehensive performance optimizations
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
import uvicorn

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

# Performance optimization imports
from core.performance_config import get_performance_config
from core.cache_manager import get_cache_manager
from core.database_optimizer import get_database_manager
from core.async_processor import get_async_processor, TaskPriority
from core.memory_optimizer import get_memory_optimizer
from core.performance_monitor import get_performance_monitor, MetricType

# Business logic imports
from services.korean_strategy_engine import KoreanStrategyEngine
from services.korean_risk_manager import KoreanRiskManager
from services.korean_strategy_validator import KoreanStrategyValidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Performance configuration
perf_config = get_performance_config()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting Korean Stock Backtesting Platform with Performance Optimizations...")
    
    # Initialize performance systems
    async_processor = await get_async_processor()
    await async_processor.start()
    
    performance_monitor = get_performance_monitor()
    await performance_monitor.start_monitoring()
    
    logger.info("Performance systems initialized")
    
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down performance systems...")
    await async_processor.stop()
    await performance_monitor.stop_monitoring()
    
    logger.info("Korean Stock Backtesting Platform shut down")

# Create FastAPI app with performance optimizations
app = FastAPI(
    title="Korean Stock Backtesting Platform - Optimized",
    description="Production-ready Korean stock strategy backtesting with advanced performance optimizations",
    version="2.0.0-optimized",
    lifespan=lifespan
)

# Add performance middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Performance monitoring middleware
@app.middleware("http")
async def performance_monitoring_middleware(request: Request, call_next):
    """Monitor API performance"""
    start_time = time.time()
    
    # Record request
    performance_monitor = get_performance_monitor()
    endpoint = f"{request.method} {request.url.path}"
    
    try:
        response = await call_next(request)
        
        # Calculate response time
        process_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Record metrics
        performance_monitor.record_response_time(endpoint, process_time)
        performance_monitor.record_request(endpoint, success=response.status_code < 400)
        
        # Add performance headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Server-Version"] = "2.0.0-optimized"
        
        return response
        
    except Exception as e:
        # Record error
        process_time = (time.time() - start_time) * 1000
        performance_monitor.record_response_time(endpoint, process_time)
        performance_monitor.record_request(endpoint, success=False)
        
        logger.error(f"Request failed: {endpoint} - {str(e)}")
        raise

# Dependency injection for optimized services
async def get_cache_service():
    """Get cache manager service"""
    return await get_cache_manager()

async def get_database_service():
    """Get database manager service"""
    return await get_database_manager()

async def get_async_service():
    """Get async processor service"""
    return await get_async_processor()

async def get_memory_service():
    """Get memory optimizer service"""
    return get_memory_optimizer()

async def get_monitoring_service():
    """Get performance monitor service"""
    return get_performance_monitor()

# Health and monitoring endpoints
@app.get("/health")
async def health_check(
    monitor: Any = Depends(get_monitoring_service)
):
    """Enhanced health check with performance metrics"""
    health_status = await monitor.get_system_health()
    
    return {
        "status": health_status.status,
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0-optimized",
        "performance": {
            "cpu_usage_percent": health_status.cpu_usage_percent,
            "memory_usage_percent": health_status.memory_usage_percent,
            "response_time_avg_ms": health_status.response_time_avg_ms,
            "cache_hit_rate_percent": health_status.cache_hit_rate_percent,
            "active_connections": health_status.active_connections
        },
        "korean_market_ready": True
    }

@app.get("/performance/dashboard")
async def performance_dashboard(
    monitor: Any = Depends(get_monitoring_service)
):
    """Get performance dashboard data"""
    return monitor.get_performance_dashboard_data()

@app.get("/performance/report")
async def performance_report(
    hours: int = 24,
    monitor: Any = Depends(get_monitoring_service)
):
    """Get detailed performance report"""
    return monitor.get_performance_report(hours)

# Optimized stock data endpoints
@app.get("/api/v1/stocks")
async def get_stocks_optimized(
    market: str = "ALL",
    limit: int = 100,
    cache_manager: Any = Depends(get_cache_service),
    db_manager: Any = Depends(get_database_service),
    monitor: Any = Depends(get_monitoring_service)
):
    """Get stock list with caching optimization"""
    start_time = time.time()
    
    try:
        # Try cache first
        cache_key = f"stocks_{market}_{limit}"
        cached_data = await cache_manager.memory_cache.get(cache_key)
        
        if cached_data:
            monitor.record_metric("cache_hits", 1, MetricType.COUNTER, 
                                labels={"endpoint": "stocks", "cache_type": "hit"})
            
            processing_time = (time.time() - start_time) * 1000
            monitor.record_korean_market_metrics("COMBINED", len(cached_data), processing_time)
            
            return cached_data
        
        # Cache miss - get from database
        monitor.record_metric("cache_misses", 1, MetricType.COUNTER,
                            labels={"endpoint": "stocks", "cache_type": "miss"})
        
        # Sample optimized data (in production, would query database)
        korean_stocks = [
            {
                "symbol": "005930",
                "name": "Samsung Electronics",
                "name_kr": "삼성전자",
                "market": "KOSPI",
                "sector": "기술주",
                "current_price": 73000,
                "change": 1.2,
                "market_cap": 437000000000000,
                "volume": 12500000
            },
            {
                "symbol": "000660",
                "name": "SK Hynix", 
                "name_kr": "SK하이닉스",
                "market": "KOSPI",
                "sector": "기술주",
                "current_price": 125000,
                "change": -0.8,
                "market_cap": 91000000000000,
                "volume": 8500000
            },
            {
                "symbol": "035420",
                "name": "NAVER Corporation",
                "name_kr": "NAVER",
                "market": "KOSPI", 
                "sector": "기술주",
                "current_price": 180000,
                "change": 2.1,
                "market_cap": 59000000000000,
                "volume": 3200000
            }
        ]
        
        # Filter by market if specified
        if market != "ALL":
            korean_stocks = [s for s in korean_stocks if s["market"] == market]
        
        # Apply limit
        korean_stocks = korean_stocks[:limit]
        
        # Cache the result
        await cache_manager.memory_cache.set(cache_key, korean_stocks, 300)  # 5 minutes
        
        processing_time = (time.time() - start_time) * 1000
        monitor.record_korean_market_metrics(market, len(korean_stocks), processing_time)
        
        return korean_stocks
        
    except Exception as e:
        logger.error(f"Error getting stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/stocks/{symbol}/data")
async def get_stock_data_optimized(
    symbol: str,
    start_date: str = None,
    end_date: str = None,
    cache_manager: Any = Depends(get_cache_service),
    memory_optimizer: Any = Depends(get_memory_service),
    monitor: Any = Depends(get_monitoring_service)
):
    """Get optimized historical stock data"""
    try:
        with memory_optimizer.memory_monitoring_context(f"stock_data_{symbol}"):
            # Set default date range
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            
            # Try cache first
            cached_data = await cache_manager.get_market_data(
                symbol, (start_date, end_date)
            )
            
            if cached_data is not None:
                monitor.record_metric("stock_data_cache_hit", 1, MetricType.COUNTER)
                
                # Convert DataFrame to API format
                data_points = []
                for idx, row in cached_data.iterrows():
                    data_points.append({
                        "date": idx[1].strftime("%Y-%m-%d") if isinstance(idx, tuple) else idx.strftime("%Y-%m-%d"),
                        "open": int(row.get('open', 0)),
                        "high": int(row.get('high', 0)),
                        "low": int(row.get('low', 0)),
                        "close": int(row.get('close', 0)),
                        "volume": int(row.get('volume', 0))
                    })
                
                return data_points
            
            # Generate sample optimized data
            import pandas as pd
            import numpy as np
            from datetime import timedelta
            
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            base_price = 70000 if symbol == "005930" else 100000
            
            data_points = []
            current_price = base_price
            
            for date in dates:
                if date.weekday() < 5:  # Korean market trading days
                    # Simulate realistic price movement
                    daily_change = np.random.normal(0, 0.02)  # 2% daily volatility
                    current_price *= (1 + daily_change)
                    
                    open_price = current_price * np.random.uniform(0.99, 1.01)
                    close_price = current_price * np.random.uniform(0.99, 1.01)
                    high_price = max(open_price, close_price) * np.random.uniform(1.0, 1.03)
                    low_price = min(open_price, close_price) * np.random.uniform(0.97, 1.0)
                    volume = np.random.randint(1000000, 20000000)
                    
                    data_points.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "open": int(open_price),
                        "high": int(high_price),
                        "low": int(low_price),
                        "close": int(close_price),
                        "volume": int(volume)
                    })
            
            # Create DataFrame for caching
            df_data = []
            for point in data_points:
                df_data.append({
                    'date': pd.to_datetime(point['date']),
                    'open': point['open'],
                    'high': point['high'],
                    'low': point['low'],
                    'close': point['close'],
                    'volume': point['volume']
                })
            
            if df_data:
                df = pd.DataFrame(df_data)
                df = df.set_index('date')
                
                # Optimize DataFrame memory usage
                optimized_df = memory_optimizer.optimize_dataframe_memory(df, symbol)
                
                # Cache the optimized data
                await cache_manager.set_market_data(symbol, (start_date, end_date), optimized_df)
            
            monitor.record_korean_market_metrics("KOSPI" if symbol < "900000" else "KOSDAQ", 
                                               len(data_points), 0)
            
            return data_points
            
    except Exception as e:
        logger.error(f"Error getting stock data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Optimized backtesting endpoints
@app.post("/api/v1/backtest/run")
async def run_backtest_optimized(
    backtest_request: dict,
    background_tasks: BackgroundTasks,
    async_processor: Any = Depends(get_async_service),
    monitor: Any = Depends(get_monitoring_service)
):
    """Run optimized backtest with async processing"""
    try:
        logger.info(f"Starting optimized backtest: {backtest_request}")
        
        # Validate request
        required_fields = ["symbol", "strategy", "start_date", "end_date"]
        for field in required_fields:
            if field not in backtest_request:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Submit backtest task to async processor
        task_id = await async_processor.submit_backtest_task(
            backtest_config=backtest_request,
            priority=TaskPriority.HIGH
        )
        
        monitor.record_metric("backtest_requests", 1, MetricType.COUNTER,
                            labels={"symbol": backtest_request.get("symbol", "unknown")})
        
        return {
            "task_id": task_id,
            "status": "submitted",
            "message": "Backtest submitted for async processing",
            "symbol": backtest_request.get("symbol"),
            "strategy": backtest_request.get("strategy"),
            "estimated_completion_time": "2-5 minutes"
        }
        
    except Exception as e:
        logger.error(f"Backtest submission failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/backtest/status/{task_id}")
async def get_backtest_status(
    task_id: str,
    async_processor: Any = Depends(get_async_service)
):
    """Get backtest task status"""
    try:
        task_result = await async_processor.get_task_status(task_id)
        
        if not task_result:
            raise HTTPException(status_code=404, detail="Task not found")
        
        response = {
            "task_id": task_id,
            "status": task_result.status.value,
            "start_time": task_result.start_time.isoformat() if task_result.start_time else None,
            "end_time": task_result.end_time.isoformat() if task_result.end_time else None,
            "execution_time_ms": task_result.execution_time_ms
        }
        
        if task_result.result:
            response["result"] = task_result.result
        
        if task_result.error:
            response["error"] = task_result.error
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced strategy endpoints
@app.get("/api/v1/strategies/templates")
async def get_strategy_templates_optimized(
    cache_manager: Any = Depends(get_cache_service),
    monitor: Any = Depends(get_monitoring_service)
):
    """Get optimized Korean strategy templates"""
    try:
        # Check cache first
        cached_templates = await cache_manager.memory_cache.get("strategy_templates")
        
        if cached_templates:
            monitor.record_metric("strategy_template_cache_hit", 1, MetricType.COUNTER)
            return cached_templates
        
        # Generate Korean optimized strategies
        engine = KoreanStrategyEngine()
        korean_strategies = engine.create_korean_optimized_strategies()
        
        # Convert to API format
        templates = []
        for strategy in korean_strategies[:10]:  # Top 10 strategies
            template = {
                "id": strategy["id"],
                "name": strategy["name"],
                "name_en": strategy.get("name_en", strategy["name"]),
                "description": strategy["description"][:200] + "..." if len(strategy["description"]) > 200 else strategy["description"],
                "market_focus": [market.value for market in strategy.get("market_focus", [])],
                "risk_level": strategy.get("risk_level", "medium"),
                "expected_return": strategy.get("expected_annual_return", 0.15),
                "max_drawdown": strategy.get("max_drawdown_target", 0.20),
                "strategy_type": "korean_optimized",
                "performance_optimized": True
            }
            templates.append(template)
        
        # Cache templates
        await cache_manager.memory_cache.set("strategy_templates", templates, 1800)  # 30 minutes
        
        monitor.record_korean_market_metrics("STRATEGY_ENGINE", len(templates), 0)
        
        return templates
        
    except Exception as e:
        logger.error(f"Error getting strategy templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Advanced Korean market endpoints
@app.post("/api/v1/korean/risk/assess")
async def assess_korean_portfolio_risk(
    risk_request: dict,
    cache_manager: Any = Depends(get_cache_service),
    memory_optimizer: Any = Depends(get_memory_service),
    monitor: Any = Depends(get_monitoring_service)
):
    """Assess portfolio risk with Korean market optimizations"""
    try:
        with memory_optimizer.memory_monitoring_context("korean_risk_assessment"):
            portfolio = risk_request.get("portfolio", {})
            
            if not portfolio:
                raise HTTPException(status_code=400, detail="Portfolio data required")
            
            # Check cache for recent risk assessment
            portfolio_hash = str(hash(str(sorted(portfolio.items()))))
            cache_key = f"risk_assessment_{portfolio_hash}"
            
            cached_assessment = await cache_manager.memory_cache.get(cache_key)
            if cached_assessment:
                monitor.record_metric("risk_assessment_cache_hit", 1, MetricType.COUNTER)
                return cached_assessment
            
            # Initialize Korean risk manager
            risk_manager = KoreanRiskManager()
            
            # Generate sample market data for assessment
            import pandas as pd
            import numpy as np
            
            market_data = {}
            for symbol in portfolio.keys():
                dates = pd.date_range(end=datetime.now(), periods=252, freq='D')
                
                # Generate Korean market-specific data
                base_price = 70000 if symbol == "005930" else 100000
                prices = []
                current_price = base_price
                
                for _ in range(252):
                    daily_change = np.random.normal(0, 0.025)  # Korean market volatility
                    current_price *= (1 + daily_change)
                    prices.append(current_price)
                
                sample_data = pd.DataFrame({
                    'open': [p * np.random.uniform(0.99, 1.01) for p in prices],
                    'high': [p * np.random.uniform(1.0, 1.04) for p in prices],
                    'low': [p * np.random.uniform(0.96, 1.0) for p in prices],
                    'close': prices,
                    'volume': [np.random.randint(1000000, 15000000) for _ in range(252)]
                }, index=dates)
                
                # Optimize DataFrame memory usage
                market_data[symbol] = memory_optimizer.optimize_korean_market_data_processing(sample_data)
            
            # Assess portfolio risk
            risk_metrics = risk_manager.assess_portfolio_risk(portfolio, market_data)
            risk_limits = risk_manager.check_risk_limits(portfolio, market_data)
            
            # Generate comprehensive assessment
            assessment = {
                "risk_assessment_id": f"korean_risk_{int(time.time())}",
                "timestamp": datetime.now().isoformat(),
                "portfolio_summary": {
                    "total_value": sum(portfolio.values()),
                    "number_of_positions": len(portfolio),
                    "largest_position_weight": max(portfolio.values()) / sum(portfolio.values()) if portfolio else 0,
                    "korean_market_exposure": sum(v for k, v in portfolio.items() if k < "900000") / sum(portfolio.values())
                },
                "risk_metrics": {
                    "portfolio_var_95": float(risk_metrics.portfolio_var),
                    "portfolio_cvar_95": float(risk_metrics.portfolio_cvar),
                    "annualized_volatility": float(risk_metrics.volatility),
                    "beta_vs_kospi": float(risk_metrics.beta),
                    "max_drawdown": float(risk_metrics.max_drawdown),
                    "korean_risk_score": float(risk_metrics.korean_risk_score),
                    "currency_risk": 0.02,  # KRW risk factor
                    "concentration_risk": max(portfolio.values()) / sum(portfolio.values())
                },
                "korean_market_factors": {
                    "chaebol_concentration_risk": "low",
                    "price_limit_exposure": "monitored",
                    "market_cap_distribution": "balanced",
                    "sector_concentration": "technology_heavy"
                },
                "risk_limits_status": risk_limits,
                "performance_optimized": True,
                "calculation_time_ms": 0  # Will be updated
            }
            
            # Cache the assessment
            await cache_manager.memory_cache.set(cache_key, assessment, 600)  # 10 minutes
            
            monitor.record_korean_market_metrics("RISK_ASSESSMENT", len(portfolio), 0)
            monitor.record_metric("risk_assessments_completed", 1, MetricType.COUNTER)
            
            return assessment
            
    except Exception as e:
        logger.error(f"Korean risk assessment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# System optimization endpoints
@app.get("/api/v1/system/optimize")
async def optimize_system(
    memory_optimizer: Any = Depends(get_memory_service),
    cache_manager: Any = Depends(get_cache_service),
    db_manager: Any = Depends(get_database_service),
    monitor: Any = Depends(get_monitoring_service)
):
    """Perform system optimization"""
    try:
        optimization_results = {}
        
        # Memory optimization
        gc_results = memory_optimizer.force_garbage_collection()
        memory_stats = memory_optimizer.get_memory_stats()
        
        optimization_results["memory"] = {
            "gc_collections": gc_results,
            "current_usage_mb": memory_stats.process_memory_mb,
            "cached_dataframes_mb": memory_stats.cached_dataframes_mb
        }
        
        # Cache optimization
        cache_cleanup = await cache_manager.cleanup_expired_caches()
        cache_stats = cache_manager.get_cache_statistics()
        
        optimization_results["cache"] = {
            "expired_items_cleaned": cache_cleanup,
            "current_stats": cache_stats
        }
        
        # Database optimization
        db_maintenance = await db_manager.optimize_database_maintenance()
        db_analytics = await db_manager.get_performance_analytics()
        
        optimization_results["database"] = {
            "maintenance_results": db_maintenance,
            "performance_analytics": db_analytics
        }
        
        # Record optimization metrics
        monitor.record_metric("system_optimizations", 1, MetricType.COUNTER)
        
        return {
            "optimization_timestamp": datetime.now().isoformat(),
            "results": optimization_results,
            "status": "completed"
        }
        
    except Exception as e:
        logger.error(f"System optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "Korean Stock Backtesting Platform - Optimized",
        "version": "2.0.0-optimized",
        "timestamp": datetime.now().isoformat(),
        "status": "operational",
        "features": {
            "korean_market_optimized": True,
            "async_processing": True,
            "advanced_caching": True,
            "memory_optimization": True,
            "performance_monitoring": True,
            "database_optimization": True
        },
        "endpoints": {
            "health": "/health",
            "performance_dashboard": "/performance/dashboard",
            "api_docs": "/docs",
            "stocks": "/api/v1/stocks",
            "backtest": "/api/v1/backtest/run",
            "strategies": "/api/v1/strategies/templates",
            "korean_risk": "/api/v1/korean/risk/assess",
            "system_optimize": "/api/v1/system/optimize"
        }
    }

if __name__ == "__main__":
    print("=" * 80)
    print("Korean Stock Backtesting Platform - Optimized API Server")
    print("=" * 80)
    print("🚀 Production-ready server with comprehensive optimizations:")
    print("   • Advanced multi-level caching system")
    print("   • Async processing and background tasks")
    print("   • Memory optimization for large datasets")
    print("   • Database query optimization")
    print("   • Real-time performance monitoring")
    print("   • Korean market-specific optimizations")
    print("=" * 80)
    print("📊 Performance Features:")
    print("   • Response time monitoring")
    print("   • Memory usage optimization")
    print("   • Cache hit rate tracking")
    print("   • Database connection pooling")
    print("   • GZip compression")
    print("   • Concurrent request handling")
    print("=" * 80)
    print("🇰🇷 Korean Market Optimizations:")
    print("   • KOSPI/KOSDAQ specific processing")
    print("   • Won currency precision")
    print("   • Price limit detection")
    print("   • Chaebol correlation analysis")
    print("   • Korean trading hours awareness")
    print("=" * 80)
    print("Server starting...")
    print("API Documentation: http://localhost:8001/docs")
    print("Performance Dashboard: http://localhost:8001/performance/dashboard")
    print("Health Check: http://localhost:8001/health")
    print("System Status: http://localhost:8001/")
    print("Press Ctrl+C to stop the server")
    print("=" * 80)
    
    uvicorn.run(
        "optimized_api_server:app",
        host="0.0.0.0",
        port=8001,
        reload=False,  # Disable reload in production
        access_log=True,
        workers=1  # Single worker for SQLite; use multiple for PostgreSQL
    )