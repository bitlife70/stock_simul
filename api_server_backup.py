#!/usr/bin/env python3
"""
Korean Stock Backtesting API Server
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import random
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Korean Stock Backtesting API",
    description="API for Korean stock strategy backtesting with KOSPI/KOSDAQ data",
    version="1.0.0-dev"
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
        "version": "1.0.0-dev",
        "timestamp": datetime.now().isoformat(),
        "status": "running",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "stocks": "/api/v1/stocks",
            "market_overview": "/api/v1/market-overview"
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
async def get_sample_stocks():
    """Sample Korean stock data for testing"""
    return [
        {
            "symbol": "005930",
            "name": "Samsung Electronics",
            "name_kr": "삼성전자",
            "market": "KOSPI",
            "sector": "기술주",
            "current_price": 73000,
            "change": 1.2
        },
        {
            "symbol": "000660", 
            "name": "SK Hynix",
            "name_kr": "SK하이닉스",
            "market": "KOSPI",
            "sector": "기술주", 
            "current_price": 125000,
            "change": -0.8
        },
        {
            "symbol": "035420",
            "name": "NAVER Corporation",
            "name_kr": "NAVER", 
            "market": "KOSPI",
            "sector": "기술주",
            "current_price": 180000,
            "change": 2.1
        },
        {
            "symbol": "051910",
            "name": "LG Chem",
            "name_kr": "LG화학",
            "market": "KOSPI", 
            "sector": "화학",
            "current_price": 400000,
            "change": -1.5
        },
        {
            "symbol": "068270",
            "name": "Celltrion",
            "name_kr": "셀트리온",
            "market": "KOSPI",
            "sector": "바이오",
            "current_price": 160000,
            "change": 3.2
        }
    ]

@app.get("/api/v1/market-overview")
async def get_market_overview():
    """Market overview data"""
    return {
        "market": "ALL",
        "total_stocks": 5,
        "active_stocks": 5,
        "latest_data_date": "2025-07-31",
        "kospi_index": 2500.45,
        "kospi_change": 0.8,
        "kosdaq_index": 750.12,
        "kosdaq_change": -0.3,
        "status": "sample_data"
    }

@app.get("/api/v1/stocks/{symbol}")
async def get_stock_detail(symbol: str):
    """Get detailed stock information"""
    # Sample stock data
    stock_data = {
        "005930": {
            "symbol": "005930",
            "name": "삼성전자", 
            "market": "KOSPI",
            "current_price": 73000,
            "open": 72500,
            "high": 74000,
            "low": 72000,
            "volume": 12500000,
            "market_cap": 437000000000000,
            "pe_ratio": 15.2
        }
    }
    
    if symbol in stock_data:
        return stock_data[symbol]
    else:
        return {"error": "Stock not found", "symbol": symbol}

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
                        "type": "number",
                        "default": 5,
                        "min": 3,
                        "max": 15,
                        "description": "단기 이동평균 기간"
                    },
                    "long_ma": {
                        "type": "number",
                        "default": 20,  
                        "min": 15,
                        "max": 50,
                        "description": "장기 이동평균 기간"
                    },
                    "volume_threshold": {
                        "type": "number",
                        "default": 1.5,
                        "min": 1.0,
                        "max": 3.0,
                        "description": "거래량 확인 배수 (평균 대비)"
                    },
                    "volatility_filter": {
                        "type": "number",
                        "default": 0.08,
                        "min": 0.05,
                        "max": 0.15,
                        "description": "최대 변동성 필터 (8% = 0.08)"
                    },
                    "stop_loss": {
                        "type": "number",
                        "default": 0.07,
                        "min": 0.03,
                        "max": 0.15,
                        "description": "손절 비율"
                    },
                    "take_profit": {
                        "type": "number", 
                        "default": 0.20,
                        "min": 0.10,
                        "max": 0.50,
                        "description": "익절 비율"
                    }
                }
            },
            {
                "id": "korean_rsi_advanced",
                "name": "한국형 RSI 고급전략",
                "name_en": "Korean Advanced RSI Strategy",
                "description": "한국 시장의 높은 변동성을 고려한 RSI 역추세 전략 - KOSPI/KOSDAQ 특성에 맞춘 매개변수 최적화",
                "market_focus": ["KOSDAQ"],
                "risk_level": "medium-high", 
                "expected_return": 0.25,
                "max_drawdown": 0.18,
                "strategy_type": "enhanced_basic",
                "parameters": {
                    "rsi_period": {
                        "type": "number",
                        "default": 12,
                        "min": 9,
                        "max": 21,
                        "description": "RSI 계산 기간 (한국시장 최적화)"
                    },
                    "oversold_level": {
                        "type": "number",
                        "default": 25,
                        "min": 15,
                        "max": 35,
                        "description": "과매도 기준선 (KOSDAQ 최적화)"
                    },
                    "overbought_level": {
                        "type": "number",
                        "default": 75,
                        "min": 65,
                        "max": 85,
                        "description": "과매수 기준선"
                    },
                    "trend_filter": {
                        "type": "number",
                        "default": 60,
                        "min": 30,
                        "max": 120,
                        "description": "추세 필터 이동평균 기간"
                    },
                    "volume_surge": {
                        "type": "number",
                        "default": 2.0,
                        "min": 1.5,
                        "max": 5.0,
                        "description": "거래량 급증 배수"
                    },
                    "max_holding_days": {
                        "type": "number",
                        "default": 30,
                        "min": 10,
                        "max": 90,
                        "description": "최대 보유 기간 (일)"
                    }
                }
            },
            {
                "id": "korean_breakout_volatility",
                "name": "한국형 변동성 돌파전략", 
                "name_en": "Korean Volatility Breakout Strategy",
                "description": "한국 시장의 변동성 특성을 고려한 돌파 전략 - 상한가/하한가 시스템과 급등락 패턴 활용",
                "market_focus": ["KOSDAQ"],
                "risk_level": "high",
                "expected_return": 0.35,
                "max_drawdown": 0.25,
                "strategy_type": "enhanced_basic",
                "parameters": {
                    "breakout_period": {
                        "type": "number",
                        "default": 20,
                        "min": 10,
                        "max": 40,
                        "description": "돌파 기준 기간"
                    },
                    "volume_confirmation": {
                        "type": "number",
                        "default": 3.0,
                        "min": 2.0,
                        "max": 10.0,
                        "description": "거래량 확인 배수"
                    },
                    "atr_multiplier": {
                        "type": "number",
                        "default": 2.0,
                        "min": 1.0,
                        "max": 4.0,
                        "description": "ATR 기반 스탑로스 배수"
                    },
                    "price_limit_filter": {
                        "type": "boolean",
                        "default": true,
                        "description": "상한가/하한가 필터 사용"
                    },
                    "gap_threshold": {
                        "type": "number",
                        "default": 0.03,
                        "min": 0.01,
                        "max": 0.10,
                        "description": "갭 임계값 (3% = 0.03)"
                    }
                }
            }
        ]
        
        templates.extend(basic_templates)
        
        return templates
        
    except Exception as e:
        logger.error(f"Error loading Korean strategy templates: {e}")
        # Fallback to basic templates
        return [
            {
                "id": "golden_cross",
                "name": "Golden Cross Strategy",
                "name_kr": "골든 크로스 전략",
                "description": "5일 이동평균이 20일 이동평균을 상향 돌파할 때 매수",
                "strategy_type": "basic",
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
                    }
                }
            }
        ]

@app.get("/api/v1/stocks/{symbol}/data")
async def get_stock_data(symbol: str):
    """Get historical stock price data"""
    # Sample historical data for testing
    import random
    from datetime import datetime, timedelta
    
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
    """Run professional Korean stock backtesting simulation"""
    try:
        # Import the professional backtesting engine
        from backtesting_engine import run_professional_backtest
        
        # Log the backtest request
        logger.info(f"Starting backtest for: {backtest_request}")
        
        # Map frontend parameters to backtest engine format
        symbol = backtest_request.get("symbol", "005930")
        strategy_id = backtest_request.get("strategy", "golden_cross")
        start_date = backtest_request.get("start_date", "2023-01-01")
        end_date = backtest_request.get("end_date", "2024-12-31")
        initial_capital = int(backtest_request.get("initial_capital", 10000000))
        
        # Extract strategy parameters
        strategy_parameters = {}
        if strategy_id == "golden_cross":
            strategy_parameters = {
                "short_period": backtest_request.get("short_period", 5),
                "long_period": backtest_request.get("long_period", 20),
                "stop_loss": backtest_request.get("stop_loss", 0.05)
            }
        elif strategy_id == "rsi_reversal":
            strategy_parameters = {
                "rsi_period": backtest_request.get("rsi_period", 14),
                "oversold_level": backtest_request.get("oversold_level", 30),
                "overbought_level": backtest_request.get("overbought_level", 70)
            }
        elif strategy_id == "bollinger_squeeze":
            strategy_parameters = {
                "bb_period": backtest_request.get("bb_period", 20),
                "bb_std": backtest_request.get("bb_std", 2.0),
                "volume_confirm": backtest_request.get("volume_confirm", True)
            }
        
        # Prepare backtest configuration
        backtest_config = {
            "symbol": symbol,
            "strategy_id": strategy_id,
            "start_date": start_date,
            "end_date": end_date,
            "initial_capital": initial_capital,
            "strategy_parameters": strategy_parameters
        }
        
        # Run the professional backtest
        results = await run_professional_backtest(backtest_config)
        
        # Log successful completion
        logger.info(f"Backtest completed successfully for {symbol}")
        
        return results
        
    except Exception as e:
        logger.error(f"Professional backtest failed: {e}")
        
        # Fallback to basic simulation if the professional engine fails
        import random
        initial_capital = backtest_request.get("initial_capital", 10000000)
        total_return = random.uniform(-0.15, 0.25)  # More conservative range
        win_rate = random.uniform(0.35, 0.65)
        total_trades = random.randint(15, 80)
        max_drawdown = random.uniform(-0.25, -0.08)
        sharpe_ratio = random.uniform(0.3, 1.8)
        final_capital = initial_capital * (1 + total_return)
        
        return {
            "total_return": total_return,
            "win_rate": win_rate,
            "total_trades": total_trades,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe_ratio,
            "final_capital": final_capital,
            "initial_capital": initial_capital,
            "error": f"Professional engine failed: {str(e)}",
            "fallback_mode": True
        }

@app.post("/api/v1/strategies")
async def save_strategy(strategy: dict):
    """Save a trading strategy"""
    # In a real implementation, this would save to database
    strategy_id = f"strategy_{random.randint(1000, 9999)}"
    return {
        "id": strategy_id,
        "message": "Strategy saved successfully",
        "strategy": strategy
    }

@app.post("/api/v1/strategies/analyze")
async def analyze_strategy(analysis_request: dict):
    """Analyze a strategy with Korean market optimization"""
    try:
        import sys
        import os
        import pandas as pd
        import numpy as np
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        
        from services.korean_strategy_engine import KoreanStrategyEngine
        from services.korean_strategy_validator import KoreanStrategyValidator
        
        strategy_config = analysis_request.get("strategy", {})
        symbol = analysis_request.get("symbol", "005930")
        period_days = analysis_request.get("period_days", 252)
        
        # Generate sample data for analysis
        dates = pd.date_range(end=datetime.now(), periods=period_days, freq='D')
        sample_data = pd.DataFrame({
            'date': dates,
            'open': np.random.normal(70000, 5000, period_days),
            'high': np.random.normal(72000, 5000, period_days),
            'low': np.random.normal(68000, 5000, period_days),
            'close': np.random.normal(70000, 5000, period_days),
            'volume': np.random.randint(1000000, 10000000, period_days)
        })
        sample_data.set_index('date', inplace=True)
        
        # Ensure price consistency (high >= low, etc.)
        sample_data['high'] = np.maximum(sample_data[['open', 'close']].max(axis=1), sample_data['high'])
        sample_data['low'] = np.minimum(sample_data[['open', 'close']].min(axis=1), sample_data['low'])
        
        # Initialize Korean strategy engine
        engine = KoreanStrategyEngine()
        
        # Calculate strategy signals
        df_with_signals = engine.calculate_strategy_signals(sample_data, strategy_config, symbol)
        
        # Generate sample returns based on signals
        returns = []
        position = 0
        for i in range(1, len(df_with_signals)):
            if df_with_signals.iloc[i]['buy_signal'] and position == 0:
                position = 1
            elif df_with_signals.iloc[i]['sell_signal'] and position == 1:
                position = 0
            
            if position == 1:
                daily_return = (df_with_signals.iloc[i]['close'] - df_with_signals.iloc[i-1]['close']) / df_with_signals.iloc[i-1]['close']
            else:
                daily_return = 0
            
            returns.append(daily_return)
        
        strategy_returns = pd.Series(returns, index=df_with_signals.index[1:])
        
        # Create benchmark returns (KOSPI simulation)
        benchmark_returns = sample_data['close'].pct_change().dropna()
        benchmark_returns = benchmark_returns * 0.8 + np.random.normal(0, 0.01, len(benchmark_returns))  # Simulate KOSPI
        
        # Validate strategy
        validator = KoreanStrategyValidator()
        validation_result = validator.validate_strategy(
            strategy_returns=strategy_returns,
            benchmark_type=validator.BenchmarkType.KOSPI,
            custom_benchmark=benchmark_returns
        )
        
        # Calculate signal statistics
        total_signals = len(df_with_signals[df_with_signals['buy_signal'] == True])
        signal_strength_avg = df_with_signals['signal_strength'].mean()
        
        return {
            "analysis_id": f"analysis_{random.randint(1000, 9999)}",
            "strategy_id": strategy_config.get("id", "unknown"),
            "analysis_period": f"{period_days} days",
            "signal_analysis": {
                "total_buy_signals": int(total_signals),
                "avg_signal_strength": float(signal_strength_avg),
                "signal_frequency": float(total_signals / period_days * 252),  # Annualized
                "last_signal_date": df_with_signals[df_with_signals['buy_signal'] == True].index[-1].strftime('%Y-%m-%d') if total_signals > 0 else None
            },
            "performance_metrics": validation_result.get("metrics", {}),
            "korean_market_analysis": validation_result.get("korean_market_tests", {}),
            "overall_assessment": validation_result.get("overall_assessment", {}),
            "recommendations": validation_result.get("overall_assessment", {}).get("recommendations", []),
            "investment_suitability": validation_result.get("overall_assessment", {}).get("investment_suitability", {})
        }
        
    except Exception as e:
        logger.error(f"Error analyzing strategy: {e}")
        return {
            "error": str(e),
            "analysis_id": f"error_{random.randint(1000, 9999)}"
        }

@app.post("/api/v1/risk/assess")
async def assess_portfolio_risk(risk_request: dict):
    """Assess portfolio risk with Korean market adjustments"""
    try:
        import sys
        import os
        import pandas as pd
        import numpy as np
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        
        from services.korean_risk_manager import KoreanRiskManager
        
        portfolio = risk_request.get("portfolio", {})  # {"005930": 1000000, "000660": 500000}
        
        if not portfolio:
            return {"error": "Portfolio data required"}
        
        # Generate sample market data for risk assessment
        market_data = {}
        for symbol in portfolio.keys():
            dates = pd.date_range(end=datetime.now(), periods=252, freq='D')
            sample_data = pd.DataFrame({
                'open': np.random.normal(70000, 5000, 252),
                'high': np.random.normal(72000, 5000, 252),
                'low': np.random.normal(68000, 5000, 252),
                'close': np.random.normal(70000, 5000, 252),
                'volume': np.random.randint(1000000, 10000000, 252)
            }, index=dates)
            
            # Ensure price consistency
            sample_data['high'] = np.maximum(sample_data[['open', 'close']].max(axis=1), sample_data['high'])
            sample_data['low'] = np.minimum(sample_data[['open', 'close']].min(axis=1), sample_data['low'])
            
            market_data[symbol] = sample_data
        
        # Initialize risk manager
        risk_manager = KoreanRiskManager()
        
        # Assess portfolio risk
        risk_metrics = risk_manager.assess_portfolio_risk(portfolio, market_data)
        
        # Check risk limits
        risk_limits = risk_manager.check_risk_limits(portfolio, market_data)
        
        # Get suggestions if needed
        suggestions = []
        if risk_limits["overall_status"] != "OK":
            suggestions = risk_manager.suggest_risk_adjustments(portfolio, market_data, risk_limits)
        
        # Generate comprehensive risk report
        risk_report = risk_manager.generate_risk_report(portfolio, market_data)
        
        return {
            "risk_assessment_id": f"risk_{random.randint(1000, 9999)}",
            "timestamp": datetime.now().isoformat(),
            "portfolio_summary": {
                "total_value": sum(portfolio.values()),
                "number_of_positions": len(portfolio),
                "largest_position": max(portfolio.values()) / sum(portfolio.values()) if portfolio else 0
            },
            "risk_metrics": {
                "portfolio_var": float(risk_metrics.portfolio_var),
                "portfolio_cvar": float(risk_metrics.portfolio_cvar),
                "volatility": float(risk_metrics.volatility),
                "beta": float(risk_metrics.beta),
                "max_drawdown": float(risk_metrics.max_drawdown),
                "korean_risk_score": float(risk_metrics.korean_risk_score)
            },
            "risk_limits_check": risk_limits,
            "improvement_suggestions": suggestions,
            "overall_risk_level": risk_report.get("overall_risk_level", "medium"),
            "korean_market_factors": {
                "chaebol_concentration": "analyzed",
                "price_limit_exposure": "monitored", 
                "volatility_adjustment": "applied",
                "currency_risk": "assessed"
            }
        }
        
    except Exception as e:
        logger.error(f"Error assessing portfolio risk: {e}")
        return {
            "error": str(e),
            "risk_assessment_id": f"error_{random.randint(1000, 9999)}"
        }

@app.get("/api/v1/strategies/recommendations")
async def get_strategy_recommendations(market_conditions: str = "normal"):
    """Get Korean market strategy recommendations based on current conditions"""
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        
        from services.korean_strategy_engine import KoreanStrategyEngine
        
        engine = KoreanStrategyEngine()
        
        # Parse market conditions
        conditions = {
            "volatility": "medium",
            "usd_krw_trend": "neutral", 
            "market_phase": "neutral"
        }
        
        if market_conditions == "high_volatility":
            conditions["volatility"] = "high"
        elif market_conditions == "bull_market":
            conditions["market_phase"] = "bull_market"
        elif market_conditions == "bear_market":
            conditions["market_phase"] = "bear_market"
        
        # Get recommendations
        recommended_strategies = engine.get_korean_strategy_recommendations(conditions)
        
        # Get full strategy details for recommendations
        all_strategies = engine.create_korean_optimized_strategies()
        strategy_details = []
        
        for strategy_id in recommended_strategies:
            for strategy in all_strategies:
                if strategy["id"] == strategy_id:
                    strategy_details.append({
                        "id": strategy["id"],
                        "name": strategy["name"],
                        "name_en": strategy.get("name_en", strategy["name"]),
                        "description": strategy["description"][:150] + "..." if len(strategy["description"]) > 150 else strategy["description"],
                        "risk_level": strategy.get("risk_level", "medium"),
                        "expected_return": strategy.get("expected_annual_return", 0.15),
                        "market_focus": [market.value for market in strategy.get("market_focus", [])],
                        "suitability_score": random.uniform(0.7, 0.95),  # Simulated scoring
                        "current_market_fit": "high" if strategy_id in recommended_strategies[:2] else "medium"
                    })
                    break
        
        return {
            "recommendation_id": f"rec_{random.randint(1000, 9999)}",
            "market_conditions": conditions,
            "timestamp": datetime.now().isoformat(),
            "recommended_strategies": strategy_details,
            "market_analysis": {
                "kospi_trend": "neutral",
                "kosdaq_trend": "neutral", 
                "volatility_level": conditions["volatility"],
                "foreign_flow": "neutral",
                "sector_rotation": "technology_favored"
            },
            "implementation_guidance": [
                "Start with lower position sizes in high volatility periods",
                "Monitor Korean market-specific indicators (price limits, gaps)",
                "Consider currency impact for export-heavy stocks",
                "Maintain sector diversification within Korean market constraints"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting strategy recommendations: {e}")
        return {
            "error": str(e),
            "recommendation_id": f"error_{random.randint(1000, 9999)}"
        }

@app.get("/api/v1/indicators/korean")
async def get_korean_market_indicators():
    """Get Korean market-specific technical indicators"""
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        
        from utils.technical_indicators import TechnicalIndicatorCalculator
        
        calculator = TechnicalIndicatorCalculator()
        
        # Get available indicators organized by category
        available_indicators = calculator.get_available_indicators()
        
        return {
            "korean_market_indicators": available_indicators,
            "indicator_descriptions": {
                "korean_momentum": "한국 시장 특화 모멘텀 지표 (3, 5, 10, 20일)",
                "price_limit_detection": "상한가/하한가 감지 및 근접도 분석",
                "gap_analysis": "갭업/갭다운 패턴 및 갭 메우기 분석", 
                "institutional_vs_retail": "기관 vs 개인 거래량 패턴 분석",
                "korean_volatility": "한국 시장 변동성 (KOSPI/KOSDAQ 조정)",
                "won_precision": "원화 단위 최적화 (1000원, 100원, 10원 단위)",
                "chaebol_correlation": "재벌 그룹 연관성 분석",
                "sector_rotation": "한국 시장 섹터 순환 지표"
            },
            "usage_guidelines": {
                "kospi_optimized": "KOSPI 종목에는 더 보수적인 매개변수 사용",
                "kosdaq_optimized": "KOSDAQ 종목에는 변동성 조정 매개변수 사용",
                "price_limit_awareness": "상한가/하한가 근접 시 거래 전략 조정",
                "volume_analysis": "한국 시장 특유의 거래량 패턴 고려",
                "gap_management": "빈번한 갭 발생을 고려한 포지션 관리"
            },
            "market_hours": {
                "regular_session": "09:00 - 15:30",
                "lunch_break": "11:30 - 12:30", 
                "pre_market": "08:00 - 09:00",
                "after_hours": "15:40 - 18:00"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting Korean market indicators: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    print("=" * 60)
    print("Korean Stock Backtesting API Server")
    print("=" * 60)
    print("Server starting...")
    print("API Documentation: http://localhost:8001/docs")
    print("Health Check: http://localhost:8001/health")
    print("Sample Stock Data: http://localhost:8001/api/v1/stocks")
    print("Strategy Templates: http://localhost:8001/api/v1/strategies/templates")
    print("Backtest Endpoint: http://localhost:8001/api/v1/backtest/run")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        access_log=True
    )