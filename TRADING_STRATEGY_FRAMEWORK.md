# Korean Stock Trading Strategy Framework
## Comprehensive Backtesting System for KOSPI/KOSDAQ Markets

---

## 1. Essential Technical Indicators for Korean Markets

### 1.1 Primary Indicators (Must-Have)

#### **Moving Averages**
```python
# Implementation priorities for Korean retail investors
MA_TYPES = {
    'SMA': [5, 10, 20, 60, 120],  # Standard periods for Korean markets
    'EMA': [12, 26, 50, 200],     # Exponential moving averages
    'WMA': [10, 20, 50],          # Weighted moving averages
}

# Korean-specific periods
KOREAN_MA_PERIODS = {
    '단기': [5, 10, 20],          # Short-term (daily trading)
    '중기': [60, 120],            # Medium-term (2-6 months)
    '장기': [200, 250]            # Long-term (yearly trends)
}
```

**Rationale**: Korean retail investors heavily rely on moving average crossovers. The 5-day and 20-day MAs are particularly popular for identifying short-term trends.

#### **RSI (Relative Strength Index)**
```python
RSI_CONFIG = {
    'periods': [14, 9, 25],       # 14-day is standard, 9 for faster signals
    'overbought': 70,             # Korean market standard
    'oversold': 30,
    'extreme_overbought': 80,     # For volatile KOSDAQ stocks
    'extreme_oversold': 20,
}
```

**Korean Market Adjustment**: KOSDAQ stocks often require adjusted RSI levels (75/25) due to higher volatility.

#### **MACD (Moving Average Convergence Divergence)**
```python
MACD_CONFIG = {
    'fast_period': 12,
    'slow_period': 26,
    'signal_period': 9,
    'histogram_threshold': 0.1,   # Minimum histogram value for signals
}
```

#### **Bollinger Bands**
```python
BOLLINGER_CONFIG = {
    'period': 20,
    'std_dev': 2.0,
    'korean_adjustment': {
        'kospi_std': 1.8,         # Less volatile, tighter bands
        'kosdaq_std': 2.2,        # More volatile, wider bands
    }
}
```

### 1.2 Secondary Indicators (Important)

#### **Stochastic Oscillator**
- Very popular among Korean day traders
- %K period: 14, %D period: 3
- Overbought: 80, Oversold: 20

#### **Volume Indicators**
```python
VOLUME_INDICATORS = {
    'volume_ma': [10, 20, 50],    # Volume moving averages
    'volume_ratio': True,         # Current volume vs average
    'price_volume_trend': True,    # PVT indicator
    'on_balance_volume': True,     # OBV for trend confirmation
}
```

**Korean Market Insight**: Volume analysis is crucial in Korean markets due to frequent institutional vs retail battles.

#### **Williams %R**
- Period: 14
- Overbought: -20, Oversold: -80
- Popular for timing entries in trending stocks

### 1.3 Advanced Indicators (Optional)

#### **Korean Market Specific**
```python
KOREAN_SPECIFIC = {
    'foreign_buying_ratio': True,  # Foreign investor activity
    'program_trading_ratio': True, # Algorithmic trading impact
    'individual_vs_institution': True, # Retail vs institutional flow
    'theme_sector_rotation': True, # Sector momentum tracking
}
```

#### **Momentum Indicators**
- Average Directional Index (ADX)
- Commodity Channel Index (CCI)
- Rate of Change (ROC)

---

## 2. Strategy Logic Framework

### 2.1 Strategy Definition Structure

```python
class StrategyDefinition:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        
        # Entry Conditions
        self.entry_conditions = []
        self.entry_logic = 'AND'  # 'AND' or 'OR'
        
        # Exit Conditions
        self.exit_conditions = []
        self.exit_logic = 'OR'    # Usually OR for exits
        
        # Position Management
        self.position_sizing = {}
        self.risk_management = {}
        
        # Filters
        self.stock_filters = {}
        self.market_filters = {}

class Condition:
    def __init__(self, indicator, comparison, value, timeframe='daily'):
        self.indicator = indicator      # 'RSI', 'MA_5', 'MACD_signal', etc.
        self.comparison = comparison    # '>', '<', '>=', '<=', '==', 'cross_above', 'cross_below'
        self.value = value             # Numeric value or another indicator
        self.timeframe = timeframe     # 'daily', 'weekly', 'monthly'
        self.lookback_period = 1       # How many periods to check
```

### 2.2 Entry Condition Examples

#### **Technical Entry Conditions**
```python
ENTRY_CONDITIONS = {
    # Moving Average Crossovers
    'ma_golden_cross': {
        'indicator_1': 'MA_5',
        'comparison': 'cross_above',
        'indicator_2': 'MA_20',
        'confirmation_periods': 2
    },
    
    # RSI Oversold Recovery
    'rsi_oversold_recovery': {
        'indicator': 'RSI_14',
        'comparison': '>',
        'value': 30,
        'previous_condition': 'RSI_14 < 30 for 2 periods'
    },
    
    # Bollinger Band Squeeze
    'bb_squeeze_breakout': {
        'indicator': 'price',
        'comparison': 'cross_above',
        'value': 'BB_upper',
        'volume_confirmation': 'volume > volume_ma_20 * 1.5'
    },
    
    # Volume Breakout
    'volume_breakout': {
        'volume_condition': 'volume > volume_ma_10 * 2',
        'price_condition': 'price > high_20d',
        'rsi_filter': 'RSI_14 < 70'
    }
}
```

#### **Korean Market Specific Entries**
```python
KOREAN_ENTRY_CONDITIONS = {
    # Theme Stock Momentum
    'theme_momentum': {
        'sector_rotation': 'sector_rank <= 3',
        'relative_strength': 'stock_performance > kospi_performance * 1.2',
        'news_sentiment': 'positive_news_count >= 2'
    },
    
    # Foreign Investment Flow
    'foreign_buying': {
        'foreign_net_buying': '> 0 for 3 consecutive days',
        'stock_momentum': 'price > MA_5',
        'market_cap_filter': '>= 1000억원'
    }
}
```

### 2.3 Exit Condition Framework

```python
EXIT_CONDITIONS = {
    # Profit Taking
    'profit_targets': {
        'fixed_percentage': [5, 10, 15, 20],  # Take profits at these levels
        'trailing_stop': {
            'initial_stop': 5,    # Initial trailing distance
            'step_up': 2,         # Move stop up by 2% for every 5% gain
            'max_trailing': 15    # Maximum trailing distance
        }
    },
    
    # Stop Loss
    'stop_loss': {
        'fixed_percentage': 3,      # 3% stop loss
        'atr_based': 'ATR_14 * 2',  # ATR-based stop
        'support_based': 'below_support_level'
    },
    
    # Technical Exits
    'technical_exits': {
        'ma_cross_below': 'price cross_below MA_5',
        'rsi_overbought': 'RSI_14 > 70 for 2 periods',
        'volume_exhaustion': 'volume < volume_ma_10 * 0.5'
    },
    
    # Time-based Exits
    'time_exits': {
        'max_holding_period': 30,   # Maximum days to hold
        'end_of_week': True,        # Exit on Friday (day trading)
        'earnings_before': 2        # Exit 2 days before earnings
    }
}
```

---

## 3. Portfolio Management Features

### 3.1 Position Sizing Methods

```python
POSITION_SIZING = {
    # Fixed Amount
    'fixed_amount': {
        'amount_per_trade': 1000000,  # 1 million KRW per trade
        'max_positions': 10
    },
    
    # Percentage of Portfolio
    'percentage_based': {
        'per_position': 10,           # 10% per position
        'max_total_exposure': 80      # Maximum 80% invested
    },
    
    # Risk-based Sizing (Kelly Criterion)
    'risk_based': {
        'risk_per_trade': 2,          # Risk 2% of portfolio per trade
        'stop_loss_distance': 5,      # 5% stop loss
        'position_size': 'portfolio_value * (risk_per_trade / stop_loss_distance)'
    },
    
    # Volatility-based Sizing
    'volatility_adjusted': {
        'target_volatility': 15,      # Target 15% portfolio volatility
        'lookback_period': 20,        # 20-day volatility calculation
        'rebalance_frequency': 'weekly'
    }
}
```

### 3.2 Rebalancing Logic

```python
REBALANCING_RULES = {
    # Time-based Rebalancing
    'time_based': {
        'frequency': 'monthly',       # Monthly, weekly, quarterly
        'day_of_month': 1,           # First trading day of month
        'method': 'equal_weight'      # Equal weight or target allocation
    },
    
    # Threshold-based Rebalancing
    'threshold_based': {
        'deviation_threshold': 5,     # Rebalance if position deviates >5%
        'minimum_rebalance_amount': 100000,  # Minimum KRW to rebalance
        'check_frequency': 'daily'
    },
    
    # Volatility-based Rebalancing
    'volatility_based': {
        'vol_threshold': 20,          # Rebalance if portfolio vol > 20%
        'cool_down_period': 5,        # Wait 5 days between rebalances
        'emergency_rebalance': 30     # Emergency rebalance if vol > 30%
    }
}
```

### 3.3 Cash Management

```python
CASH_MANAGEMENT = {
    'minimum_cash_ratio': 10,         # Always keep 10% cash
    'maximum_cash_ratio': 30,         # Maximum 30% cash (market timing)
    'emergency_cash_reserve': 5,      # 5% emergency reserve
    'margin_usage': {
        'allowed': False,             # No margin for retail backtesting
        'max_leverage': 1.0           # No leverage
    }
}
```

---

## 4. Performance Metrics for Korean Retail Investors

### 4.1 Core Performance Metrics

```python
PERFORMANCE_METRICS = {
    # Return Metrics
    'returns': {
        'total_return': 'Final portfolio value / Initial investment - 1',
        'annualized_return': 'CAGR calculation',
        'monthly_returns': 'Month-by-month performance',
        'yearly_returns': 'Annual performance breakdown'
    },
    
    # Risk Metrics
    'risk': {
        'maximum_drawdown': 'Largest peak-to-trough decline',
        'volatility': 'Annualized standard deviation',
        'downside_deviation': 'Volatility of negative returns only',
        'var_95': '95% Value at Risk (daily)',
        'cvar_95': '95% Conditional Value at Risk'
    },
    
    # Risk-Adjusted Returns
    'risk_adjusted': {
        'sharpe_ratio': '(Return - Risk_free_rate) / Volatility',
        'sortino_ratio': '(Return - Risk_free_rate) / Downside_deviation',
        'calmar_ratio': 'Annualized_return / Maximum_drawdown',
        'information_ratio': 'Excess_return / Tracking_error'
    }
}
```

### 4.2 Korean Market Specific Metrics

```python
KOREAN_SPECIFIC_METRICS = {
    # Benchmark Comparisons
    'benchmarks': {
        'kospi_outperformance': 'Strategy return - KOSPI return',
        'kosdaq_outperformance': 'Strategy return - KOSDAQ return',
        'sector_relative_performance': 'Performance vs sector indices',
    },
    
    # Trading Efficiency
    'trading_efficiency': {
        'win_rate': 'Percentage of profitable trades',
        'profit_factor': 'Gross_profit / Gross_loss',
        'average_win_loss_ratio': 'Average_win / Average_loss',
        'consecutive_losses': 'Maximum consecutive losing trades'
    },
    
    # Cost Analysis
    'costs': {
        'total_transaction_costs': 'All brokerage fees and taxes',
        'turnover_ratio': 'Trading volume / Average portfolio value',
        'cost_adjusted_return': 'Net return after all costs',
        'tax_efficiency': 'Pre-tax vs post-tax returns'
    }
}
```

### 4.3 Behavioral Metrics

```python
BEHAVIORAL_METRICS = {
    # Holding Period Analysis
    'holding_periods': {
        'average_holding_period': 'Average days per position',
        'median_holding_period': 'Median holding period',
        'holding_period_distribution': 'Distribution by time buckets'
    },
    
    # Position Sizing Analysis
    'position_analysis': {
        'average_position_size': 'Mean position size in KRW and %',
        'position_size_consistency': 'Standard deviation of position sizes',
        'largest_position_impact': 'Impact of largest position on returns'
    },
    
    # Market Timing
    'market_timing': {
        'cash_utilization': 'Average percentage invested',
        'market_exposure_by_volatility': 'Exposure during high/low vol periods',
        'seasonal_performance': 'Performance by month/quarter'
    }
}
```

---

## 5. Common Korean Trading Strategy Templates

### 5.1 Moving Average Strategies

#### **5-20 Golden Cross Strategy**
```python
STRATEGY_5_20_GOLDEN_CROSS = {
    'name': '5일-20일 골든크로스 전략',
    'description': 'Korean retail favorite - 5-day MA crosses above 20-day MA',
    'entry_conditions': [
        'MA_5 cross_above MA_20',
        'volume > volume_ma_10 * 1.2',  # Volume confirmation
        'RSI_14 < 70'                    # Not overbought
    ],
    'exit_conditions': [
        'MA_5 cross_below MA_20',        # Death cross
        'profit >= 10%',                 # 10% profit target
        'loss >= 5%'                     # 5% stop loss
    ],
    'position_sizing': 'equal_weight',
    'max_positions': 8,
    'stock_universe': 'KOSPI_200'
}
```

#### **Triple Moving Average Strategy**
```python
STRATEGY_TRIPLE_MA = {
    'name': '삼중 이동평균 전략',
    'description': 'MA_5 > MA_20 > MA_60 trend following',
    'entry_conditions': [
        'MA_5 > MA_20',
        'MA_20 > MA_60',
        'price > MA_5',
        'volume_ratio > 1.0'
    ],
    'exit_conditions': [
        'MA_5 < MA_20',
        'profit >= 15%',
        'loss >= 7%',
        'holding_period >= 30'
    ]
}
```

### 5.2 Momentum Strategies

#### **RSI Divergence Strategy**
```python
STRATEGY_RSI_DIVERGENCE = {
    'name': 'RSI 다이버전스 전략',
    'description': 'Buy on bullish RSI divergence, popular among Korean technical analysts',
    'entry_conditions': [
        'price_makes_lower_low',
        'RSI_makes_higher_low',          # Bullish divergence
        'RSI_14 < 40',                   # Oversold region
        'volume_increasing'
    ],
    'exit_conditions': [
        'RSI_14 > 70',                   # Overbought exit
        'profit >= 12%',
        'loss >= 6%'
    ],
    'filters': {
        'min_market_cap': 500,           # 500억원 minimum
        'max_pe_ratio': 30,
        'exclude_penny_stocks': True
    }
}
```

#### **Breakout Strategy**
```python
STRATEGY_BREAKOUT = {
    'name': '돌파매매 전략',
    'description': 'Buy on resistance breakout with volume',
    'entry_conditions': [
        'price > high_20d',              # 20-day high breakout
        'volume > volume_ma_20 * 2',     # Strong volume
        'RSI_14 > 50',                   # Momentum confirmation
        'price > MA_20'                  # Above trend
    ],
    'exit_conditions': [
        'price < MA_10',                 # Trend reversal
        'profit >= 20%',                 # Higher profit target for breakouts
        'loss >= 8%',
        'volume < volume_ma_10 * 0.7'    # Volume exhaustion
    ]
}
```

### 5.3 Mean Reversion Strategies

#### **Bollinger Band Bounce**
```python
STRATEGY_BB_BOUNCE = {
    'name': '볼린저밴드 바운스 전략',
    'description': 'Buy at lower band, sell at upper band',
    'entry_conditions': [
        'price <= BB_lower',
        'RSI_14 < 35',                   # Oversold
        'price_change_3d < -5%',         # Recent decline
        'fundamental_score > 60'          # Quality filter
    ],
    'exit_conditions': [
        'price >= BB_upper',
        'RSI_14 > 65',
        'profit >= 8%',                  # Lower target for mean reversion
        'loss >= 4%'
    ]
}
```

### 5.4 Sector Rotation Strategy

#### **Theme Sector Momentum**
```python
STRATEGY_THEME_MOMENTUM = {
    'name': '테마주 모멘텀 전략',
    'description': 'Korean market theme/sector rotation strategy',
    'entry_conditions': [
        'sector_momentum_rank <= 3',      # Top 3 performing sectors
        'stock_sector_rank <= 5',        # Top 5 stocks in sector
        'news_sentiment_score > 70',     # Positive news flow
        'foreign_buying_ratio > 0',      # Foreign buying interest
        'relative_strength > 1.2'        # Outperforming market
    ],
    'exit_conditions': [
        'sector_momentum_rank > 8',       # Sector losing momentum
        'relative_strength < 0.9',       # Underperforming market
        'profit >= 25%',                 # Higher target for theme plays
        'loss >= 10%',
        'holding_period >= 14'           # Quick theme rotation
    ],
    'filters': {
        'exclude_speculative': True,     # Avoid pure speculation
        'min_liquidity': 1000000000      # 10억원 daily volume minimum
    }
}
```

---

## 6. Risk Management Features

### 6.1 Stop-Loss Implementation

```python
STOP_LOSS_TYPES = {
    # Fixed Percentage Stop Loss
    'fixed_percentage': {
        'percentage': [3, 5, 7, 10],     # Common stop levels
        'calculation': 'entry_price * (1 - stop_percentage)',
        'adjustment': 'none'             # Fixed at entry
    },
    
    # Trailing Stop Loss
    'trailing_stop': {
        'initial_distance': 5,           # 5% initial trailing distance
        'step_size': 1,                  # Move in 1% increments
        'activation_profit': 3,          # Start trailing after 3% profit
        'maximum_distance': 15           # Never more than 15% away
    },
    
    # ATR-Based Stop Loss
    'atr_based': {
        'atr_period': 14,                # 14-day ATR calculation
        'atr_multiplier': 2.0,           # 2x ATR distance
        'minimum_stop': 2,               # Minimum 2% stop
        'maximum_stop': 10               # Maximum 10% stop
    },
    
    # Support/Resistance Stop
    'technical_stop': {
        'support_level': 'previous_low_20d',
        'buffer': 1,                     # 1% below support
        'dynamic_adjustment': True,      # Adjust as support changes
        'minimum_distance': 2            # At least 2% from entry
    }
}
```

### 6.2 Take-Profit Mechanisms

```python
TAKE_PROFIT_TYPES = {
    # Fixed Targets
    'fixed_targets': {
        'levels': [5, 10, 15, 20, 25],   # Multiple profit levels
        'partial_exit': {
            '5%': 25,                    # Sell 25% at 5% profit
            '10%': 50,                   # Sell 50% at 10% profit
            '20%': 100                   # Sell remaining at 20%
        }
    },
    
    # Risk-Reward Ratio
    'risk_reward': {
        'ratio': 2.0,                    # 2:1 reward to risk
        'calculation': 'entry_price + (stop_distance * ratio)',
        'adjustment': 'dynamic'          # Adjust with stop movement
    },
    
    # Technical Targets
    'technical_targets': {
        'resistance_levels': 'previous_high_20d',
        'fibonacci_levels': [1.618, 2.618, 4.236],
        'bollinger_upper': True,
        'volume_profile_resistance': True
    }
}
```

### 6.3 Portfolio-Level Risk Controls

```python
PORTFOLIO_RISK_CONTROLS = {
    # Position Limits
    'position_limits': {
        'max_single_position': 15,       # Maximum 15% in one stock
        'max_sector_exposure': 25,       # Maximum 25% in one sector
        'max_positions': 15,             # Maximum 15 positions
        'min_diversification': 8         # Minimum 8 positions when invested
    },
    
    # Drawdown Controls
    'drawdown_controls': {
        'max_portfolio_drawdown': 15,    # Stop trading at 15% drawdown
        'daily_loss_limit': 3,           # Stop trading at 3% daily loss
        'monthly_loss_limit': 8,         # Review strategy at 8% monthly loss
        'consecutive_loss_limit': 5      # Review after 5 consecutive losses
    },
    
    # Volatility Controls
    'volatility_controls': {
        'max_portfolio_volatility': 20,  # Target maximum 20% volatility
        'volatility_lookback': 30,       # 30-day volatility calculation
        'vol_adjustment_frequency': 'weekly',
        'emergency_deleveraging': 30     # Reduce positions if vol > 30%
    },
    
    # Correlation Controls
    'correlation_controls': {
        'max_position_correlation': 0.7, # Maximum 0.7 correlation between positions
        'correlation_lookback': 60,      # 60-day correlation calculation
        'correlation_check_frequency': 'weekly',
        'force_diversification': True    # Force sale if correlation too high
    }
}
```

### 6.4 Market Condition Filters

```python
MARKET_FILTERS = {
    # Market Regime Detection
    'market_regime': {
        'bull_market': {
            'condition': 'KOSPI_MA_200 > KOSPI_MA_200_20d_ago',
            'max_exposure': 90,          # Allow up to 90% exposure
            'aggressive_sizing': True
        },
        'bear_market': {
            'condition': 'KOSPI_MA_200 < KOSPI_MA_200_20d_ago',
            'max_exposure': 40,          # Reduce to 40% exposure
            'defensive_sizing': True
        },
        'sideways_market': {
            'condition': 'abs(KOSPI_20d_return) < 5%',
            'max_exposure': 70,
            'mean_reversion_focus': True
        }
    },
    
    # Volatility Filters
    'volatility_filter': {
        'low_vol': {
            'vix_condition': 'VIX < 15',
            'position_sizing': 'normal',
            'strategy_preference': 'momentum'
        },
        'high_vol': {
            'vix_condition': 'VIX > 25',
            'position_sizing': 'reduced',
            'strategy_preference': 'mean_reversion',
            'max_new_positions': 2       # Limit new positions in high vol
        }
    },
    
    # Economic Calendar Filters
    'event_filters': {
        'earnings_season': {
            'avoid_new_positions': True,  # No new positions during earnings
            'reduce_size_before_earnings': True,
            'days_before_earnings': 2
        },
        'fomc_meetings': {
            'reduce_exposure': 20,        # Reduce exposure by 20%
            'days_before_after': [1, 1]   # 1 day before and after
        },
        'korean_holidays': {
            'pre_holiday_exit': True,     # Exit positions before holidays
            'post_holiday_entry_delay': 1 # Wait 1 day after holiday
        }
    }
}
```

---

## 7. Implementation Recommendations

### 7.1 Priority Implementation Order

1. **Phase 1 (MVP - 2 months)**
   - Core technical indicators: MA, RSI, MACD, Bollinger Bands
   - Simple entry/exit logic with AND/OR conditions
   - Fixed percentage position sizing
   - Basic performance metrics (return, MDD, Sharpe ratio)
   - 2-3 template strategies (MA crossover, RSI oversold)

2. **Phase 2 (Months 3-4)**
   - Advanced indicators: Stochastic, Williams %R, Volume indicators
   - Complex condition combinations
   - Risk-based position sizing
   - Comprehensive performance analytics
   - 5-7 strategy templates including Korean market specific ones

3. **Phase 3 (Months 5-6)**
   - Korean market specific indicators and filters
   - Advanced risk management features
   - Portfolio optimization
   - Market regime detection
   - Full strategy template library (10+ strategies)

### 7.2 Korean Market Considerations

1. **Trading Hours**: Incorporate Korean market hours (9:00-15:30 KST)
2. **Holiday Calendar**: Account for Korean holidays and market closures
3. **Circuit Breakers**: Model KOSPI/KOSDAQ circuit breaker mechanisms
4. **Transaction Costs**: Include realistic Korean brokerage fees and taxes
5. **Liquidity Constraints**: Model bid-ask spreads and market impact
6. **Foreign Investment Limits**: Consider foreign ownership restrictions

### 7.3 Data Quality Requirements

1. **Survivorship Bias**: Include delisted stocks in backtests
2. **Point-in-Time Data**: Ensure no look-ahead bias in fundamental data
3. **Corporate Actions**: Adjust for stock splits, dividends, spin-offs
4. **Data Validation**: Implement data quality checks and error handling
5. **Real-time Updates**: Ensure data freshness for current analysis

This framework provides a comprehensive foundation for Korean stock backtesting that addresses the specific needs of retail investors while incorporating professional trading best practices. The modular design allows for phased implementation and easy customization based on user feedback and market requirements.