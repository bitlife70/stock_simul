# Professional Korean Stock Backtesting Engine

## Overview

This document describes the implementation of a professional-grade backtesting engine for the Korean Stock Backtesting Simulation project. The system replaces mock simulation results with real market data analysis and sophisticated strategy execution.

## Architecture

### Core Components

1. **KoreanStockBacktester** - Main backtesting orchestrator
2. **StrategyEngine** - Advanced strategy execution with Korean market optimizations
3. **Portfolio** - Sophisticated portfolio management with transaction costs
4. **KoreanMarketConstraints** - Market-specific rules and limitations
5. **Trade/Position Classes** - Data structures for tracking trades and positions

### Key Features

- **Real Korean Market Data**: Integration with FinanceDataReader and pykrx
- **Professional Strategies**: Golden Cross, RSI Reversal, Bollinger Band Breakout
- **Korean Market Constraints**: Trading hours, price limits, transaction costs
- **Performance Analytics**: Comprehensive metrics including Sharpe ratio, drawdown analysis
- **Transaction Cost Modeling**: Realistic brokerage fees and taxes

## Strategy Implementations

### 1. Golden Cross Strategy
- **Logic**: Buy when 5-day MA crosses above 20-day MA
- **Exit**: Death cross or stop-loss (5% default)
- **Parameters**: `short_period`, `long_period`, `stop_loss`
- **Korean Optimization**: Adjusted for market volatility patterns

### 2. RSI Reversal Strategy
- **Logic**: Buy when RSI crosses above oversold (25), sell when crosses below overbought (75)
- **Parameters**: `rsi_period`, `oversold_level`, `overbought_level`
- **Korean Optimization**: More aggressive thresholds for higher volatility

### 3. Bollinger Band Breakout Strategy
- **Logic**: Buy on upper band breakout with volume confirmation
- **Exit**: Lower band breakdown or mean reversion
- **Parameters**: `bb_period`, `bb_std`, `volume_confirm`
- **Korean Optimization**: Volume confirmation for retail/institutional activity

## Korean Market Constraints

### Trading Hours
- **Regular Session**: 09:00-15:30 KST
- **Market Holidays**: Korean holidays excluded
- **Weekend Trading**: Disabled

### Price Limits (상한가/하한가)
- **Large Cap**: ±15% daily limit
- **General Stocks**: ±30% daily limit
- **Automatic Detection**: Based on previous close

### Transaction Costs
- **Brokerage Fee**: 0.015% (realistic Korean rates)
- **Transaction Tax**: 0.25% (sell orders only)
- **Market Impact**: 0.01% (slippage modeling)

### Risk-Free Rate
- **Korean 3-Year Treasury**: ~3% (for Sharpe ratio calculations)

## API Integration

### Endpoint: `/api/v1/backtest/run`

**Request Parameters:**
```json
{
  "symbol": "005930",
  "strategy": "golden_cross",
  "start_date": "2023-01-01",
  "end_date": "2024-01-01",
  "initial_capital": 10000000,
  "short_period": 5,
  "long_period": 20,
  "stop_loss": 0.05
}
```

**Response Format:**
```json
{
  "total_return": 0.1234,
  "annual_return": 0.0987,
  "win_rate": 0.6543,
  "total_trades": 45,
  "winning_trades": 29,
  "losing_trades": 16,
  "max_drawdown": -0.0876,
  "sharpe_ratio": 1.23,
  "volatility": 0.1654,
  "initial_capital": 10000000,
  "final_capital": 11234000,
  "total_profit": 1234000,
  "avg_win": 145000,
  "avg_loss": -89000,
  "trading_days": 247,
  "symbol": "005930",
  "period": "2023-01-01 to 2024-01-01",
  "profit_factor": 1.63,
  "trade_details": [...],
  "equity_curve": [...]
}
```

## Performance Metrics

### Core Metrics
- **Total Return**: Overall portfolio performance
- **Annual Return**: Annualized return rate
- **Win Rate**: Percentage of profitable trades
- **Max Drawdown**: Largest peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted return (using Korean risk-free rate)

### Trade Analytics
- **Total Trades**: Number of completed round trips
- **Average Win/Loss**: Mean profit/loss per trade
- **Profit Factor**: Ratio of gross profit to gross loss
- **Holding Period**: Average days per position

### Korean Market Specific
- **Price Limit Events**: Detection of 상한가/하한가 hits
- **Market Session Analysis**: Performance by trading session
- **Volume Profile**: Institutional vs retail activity patterns

## Data Sources

### Primary: FinanceDataReader
- **Coverage**: KOSPI/KOSDAQ stocks
- **Data Quality**: High-quality OHLCV data
- **Reliability**: Stable API with good uptime

### Secondary: pykrx
- **Coverage**: Official Korean Exchange data
- **Features**: Real-time and historical data
- **Fallback**: Used when FinanceDataReader fails

### Fallback: Sample Data Generation
- **Purpose**: Demo and testing when APIs unavailable
- **Quality**: Realistic price movements and volume patterns
- **Notice**: Clearly marked as sample data

## Installation and Setup

### Required Packages
```bash
pip install fastapi uvicorn pandas numpy scipy pytz
pip install FinanceDataReader pykrx
```

### Quick Start
```bash
# Method 1: Professional startup (recommended)
python start_professional_api.py

# Method 2: Direct API server
python api_server.py

# Method 3: Test the engine
python test_backtesting_engine.py
```

### Configuration
- **Port**: 8001 (matches frontend expectations)
- **Logging**: INFO level with detailed trade execution logs
- **Fallback**: Automatic fallback to sample data if APIs fail

## Testing

### Test Suite: `test_backtesting_engine.py`
- **Golden Cross Test**: Samsung Electronics (005930)
- **RSI Reversal Test**: SK Hynix (000660)
- **Bollinger Breakout Test**: NAVER (035420)
- **API Integration Test**: Full stack testing

### Expected Results
- **Realistic Returns**: -20% to +40% annual returns
- **Trade Frequency**: 10-100 trades per year
- **Win Rates**: 35-70% depending on strategy
- **Drawdowns**: 5-30% maximum drawdown

## Production Considerations

### Performance Optimization
- **Data Caching**: Historical data cached to reduce API calls
- **Batch Processing**: Multiple symbols processed efficiently
- **Memory Management**: Large datasets handled with streaming

### Error Handling
- **API Failures**: Graceful fallback to alternative data sources
- **Network Issues**: Retry logic with exponential backoff
- **Invalid Parameters**: Comprehensive input validation

### Monitoring
- **Trade Logging**: All trade executions logged with timestamps
- **Performance Tracking**: Real-time performance metrics
- **Error Reporting**: Detailed error messages and stack traces

### Security
- **Input Validation**: All user inputs sanitized
- **Rate Limiting**: API calls rate-limited to prevent abuse
- **Data Privacy**: No personal information stored or transmitted

## Limitations and Future Enhancements

### Current Limitations
- **Single Asset**: One stock per backtest (can be extended)
- **Daily Data**: No intraday analysis (can be added)
- **Basic Strategies**: Three core strategies (extensible framework)

### Planned Enhancements
- **Multi-Asset Portfolios**: Portfolio-level backtesting
- **Advanced Strategies**: Machine learning integration
- **Real-Time Trading**: Paper trading capabilities
- **Performance Attribution**: Detailed performance breakdown

## Korean Market Specifics

### Market Microstructure
- **Tick Size**: Appropriate tick sizes by price level
- **Order Types**: Market and limit order simulation
- **Circuit Breakers**: Trading halts on extreme movements

### Cultural Factors
- **Retail Participation**: High retail investor activity
- **Gap Trading**: Frequent overnight gaps
- **News Impact**: Rapid price movements on news

### Regulatory Environment
- **Short Selling**: Restrictions and costs
- **Foreign Investment**: Limits and reporting requirements
- **Tax Implications**: Capital gains and transaction taxes

## Support and Troubleshooting

### Common Issues
1. **Data API Failures**: Check internet connection and API status
2. **Import Errors**: Ensure all required packages installed
3. **Performance Issues**: Reduce date range or use sample data

### Log Files
- **API Logs**: Detailed request/response logging
- **Backtest Logs**: Trade execution and performance logs
- **Error Logs**: Exception handling and troubleshooting info

### Contact Information
- **System Issues**: Check GitHub issues and documentation
- **Data Problems**: Verify Korean market data source status
- **Performance Questions**: Review metrics calculation methodology

---

**Note**: This professional backtesting engine transforms the project from a demo application to a serious Korean market analysis tool suitable for educational and research purposes.