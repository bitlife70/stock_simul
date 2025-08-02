"""
Korean Market-Optimized Trading Strategy Engine

This module provides professional-grade trading strategies specifically optimized for Korean stock markets
(KOSPI/KOSDAQ) with advanced technical analysis and risk management tailored for Korean retail investors.

Key Features:
- Korean market-specific strategies (Chaebol Rotation, Won-Dollar Impact, etc.)
- Advanced technical indicators with Korean market parameter optimizations
- Risk management adapted for Korean market volatility patterns
- Comprehensive strategy validation against Korean market benchmarks
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, date, timedelta
import logging
from dataclasses import dataclass
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

from utils.technical_indicators import TechnicalIndicatorCalculator

logger = logging.getLogger(__name__)

class MarketType(Enum):
    KOSPI = "KOSPI"
    KOSDAQ = "KOSDAQ"
    ALL = "ALL"

class PositionSizing(Enum):
    EQUAL_WEIGHT = "equal_weight"
    RISK_BASED = "risk_based"
    KELLY_CRITERION = "kelly_criterion"
    VOLATILITY_ADJUSTED = "volatility_adjusted"
    KOREAN_SECTOR_BALANCED = "korean_sector_balanced"

@dataclass
class KoreanMarketParameters:
    """Korean market-specific parameters for strategy optimization"""
    # Trading session parameters
    market_open_time: str = "09:00"
    market_close_time: str = "15:30"
    lunch_break_start: str = "11:30"
    lunch_break_end: str = "12:30"
    
    # Price limit parameters
    daily_price_limit: float = 0.30  # 30% daily price limit
    price_tick_size: int = 1  # Minimum price movement in won
    
    # Korean market volatility adjustments
    kospi_volatility_multiplier: float = 1.0
    kosdaq_volatility_multiplier: float = 1.3
    
    # Currency and economic factors
    usd_krw_impact_threshold: float = 0.02  # 2% USD/KRW movement threshold
    foreign_ownership_threshold: float = 0.20  # 20% foreign ownership
    
    # Sector rotation parameters
    chaebol_correlation_threshold: float = 0.7
    sector_momentum_period: int = 20
    
    # Risk-free rate (Korean 3-year treasury bond)
    risk_free_rate: float = 0.032  # 3.2% annual

class KoreanStrategyEngine:
    """Advanced Korean market trading strategy engine"""
    
    def __init__(self):
        self.calculator = TechnicalIndicatorCalculator()
        self.market_params = KoreanMarketParameters()
        
        # Korean market sector mappings
        self.korean_sectors = {
            "technology": ["005930", "000660", "035420"],  # Samsung, SK Hynix, Naver
            "automotive": ["005380", "000270", "012330"],  # Hyundai, Kia, Mobis
            "petrochemical": ["051910", "010950", "011170"],  # LG Chem, S-Oil, Lotte Chemical
            "steel": ["005490", "004020", "014820"],  # POSCO, Hyundai Steel, Dongkuk Steel
            "finance": ["055550", "086790", "316140"],  # Shinhan, Hana, Woori
            "bio": ["068270", "207940", "196170"],  # Celltrion, Samsung Biologics, KnJ
            "retail": ["069960", "282330", "051900"],  # Shinsegae, BGF Retail, LG H&H
            "construction": ["000720", "047040", "001040"],  # Hyundai, CJ Corp, CJ CheilJedang
        }
        
        # Chaebol group mappings for rotation strategies
        self.chaebol_groups = {
            "samsung": ["005930", "000810", "028050", "018260", "032830"],
            "lg": ["051910", "066570", "003550", "034220", "006360"],
            "sk": ["000660", "096770", "034730", "017800", "018880"],
            "hyundai": ["005380", "000270", "012330", "001450", "005490"],
            "lotte": ["011170", "023530", "280360", "071050", "041610"]
        }
    
    def create_korean_optimized_strategies(self) -> List[Dict[str, Any]]:
        """Create a comprehensive set of Korean market-optimized trading strategies"""
        
        strategies = []
        
        # 1. Enhanced Golden Cross Strategy (Korean Market Optimized)
        strategies.append(self._create_enhanced_golden_cross_strategy())
        
        # 2. Korean Market RSI Strategy with Won Volatility Adjustment
        strategies.append(self._create_korean_rsi_strategy())
        
        # 3. Chaebol Rotation Strategy
        strategies.append(self._create_chaebol_rotation_strategy())
        
        # 4. KOSPI/KOSDAQ Momentum Strategy
        strategies.append(self._create_kospi_kosdaq_momentum_strategy())
        
        # 5. Korean Market Timing Strategy
        strategies.append(self._create_korean_market_timing_strategy())
        
        # 6. Won-Dollar Impact Strategy
        strategies.append(self._create_usd_krw_impact_strategy())
        
        # 7. Korean Volatility Breakout Strategy
        strategies.append(self._create_korean_volatility_breakout_strategy())
        
        # 8. Korean Gap Trading Strategy
        strategies.append(self._create_korean_gap_trading_strategy())
        
        # 9. Korean Sector Rotation Strategy
        strategies.append(self._create_korean_sector_rotation_strategy())
        
        # 10. Korean Value-Momentum Strategy
        strategies.append(self._create_korean_value_momentum_strategy())
        
        return strategies
    
    def _create_enhanced_golden_cross_strategy(self) -> Dict[str, Any]:
        """Enhanced Golden Cross strategy with Korean market optimizations"""
        return {
            "id": "enhanced_golden_cross_kr",
            "name": "향상된 골든크로스 전략",
            "name_en": "Enhanced Golden Cross Strategy (Korean Optimized)",
            "description": "한국 시장에 최적화된 골든크로스 전략 - 거래량, 변동성, 원달러 환율을 고려한 고도화된 버전",
            "market_focus": [MarketType.KOSPI, MarketType.KOSDAQ],
            "risk_level": "medium",
            "expected_annual_return": 0.18,  # 18% target
            "max_drawdown_target": 0.15,  # 15% max drawdown
            
            "universe": {
                "market": "ALL",
                "min_market_cap": 100_000_000_000,  # 1000억원 minimum
                "min_volume": 100_000,  # Daily volume
                "exclude_price_limits": True,  # Exclude stocks hitting price limits
                "foreign_ownership_min": 0.05,  # At least 5% foreign ownership
                "sector_diversification": True
            },
            
            "entry_conditions": {
                "primary_signal": {
                    "ma_short": 5,
                    "ma_long": 20,
                    "signal": "golden_cross",
                    "confirmation_period": 2  # Must hold for 2 days
                },
                "volume_confirmation": {
                    "volume_ratio_threshold": 1.5,  # 50% above 20-day average
                    "volume_ma_period": 20
                },
                "volatility_filter": {
                    "atr_threshold_max": 0.08,  # Max 8% daily volatility
                    "atr_period": 14
                },
                "korean_specific": {
                    "no_price_limit_hit": True,  # Don't buy stocks that hit upper limit
                    "gap_filter": 0.03,  # Avoid stocks with >3% gaps
                    "won_dollar_trend": "neutral_or_positive"  # USD/KRW trend filter
                },
                "technical_confirmation": {
                    "rsi_range": [30, 70],  # RSI not overbought
                    "macd_positive": True,  # MACD above signal line
                    "bb_position": [0.2, 0.8]  # Not at Bollinger Band extremes
                }
            },
            
            "exit_conditions": {
                "profit_taking": {
                    "target_profit": 0.20,  # 20% profit target
                    "trailing_stop": 0.10,  # 10% trailing stop
                    "partial_profit": {
                        "first_target": 0.08,  # Sell 30% at 8% profit
                        "first_amount": 0.30,
                        "second_target": 0.15,  # Sell 40% at 15% profit
                        "second_amount": 0.40
                    }
                },
                "stop_loss": {
                    "initial_stop": 0.07,  # 7% initial stop loss
                    "atr_stop": True,  # ATR-based dynamic stop
                    "time_stop": 60  # Exit after 60 days if no profit
                },
                "technical_exit": {
                    "death_cross": True,  # MA 5 crosses below MA 20
                    "rsi_overbought": 85,  # Exit when RSI > 85
                    "volume_exhaustion": True  # Exit on volume spike with no price follow-through
                },
                "korean_specific": {
                    "price_limit_exit": True,  # Exit if stock hits upper limit (take profit)
                    "won_dollar_reversal": True,  # Exit on major USD/KRW reversal
                    "sector_weakness": True  # Exit if sector shows weakness
                }
            },
            
            "position_sizing": {
                "method": PositionSizing.VOLATILITY_ADJUSTED,
                "base_position": 0.05,  # 5% base position
                "volatility_target": 0.02,  # 2% daily portfolio volatility target
                "max_position": 0.08,  # 8% maximum single position
                "sector_limit": 0.30  # 30% maximum per sector
            },
            
            "risk_management": {
                "portfolio_stop": 0.20,  # 20% portfolio drawdown limit
                "correlation_limit": 0.70,  # Max correlation between positions
                "sector_concentration": 0.40,  # Max 40% in any sector
                "korean_factors": {
                    "won_volatility_adjustment": True,
                    "chaebol_concentration_limit": 0.25,  # Max 25% in single chaebol
                    "market_timing_override": True  # Override in extreme market conditions
                }
            },
            
            "rebalancing": {
                "frequency": "weekly",
                "min_trade_size": 1000000,  # Minimum 1M won trade
                "commission": 0.0035,  # 0.35% commission
                "slippage": 0.001,  # 0.1% slippage
                "tax_consideration": 0.0025  # 0.25% transaction tax
            }
        }
    
    def _create_korean_rsi_strategy(self) -> Dict[str, Any]:
        """Korean market RSI strategy with volatility adjustments"""
        return {
            "id": "korean_rsi_reversal",
            "name": "한국형 RSI 역추세 전략",
            "name_en": "Korean RSI Reversal Strategy",
            "description": "한국 시장의 높은 변동성을 고려한 RSI 역추세 전략 - KOSPI/KOSDAQ 특성에 맞춘 매개변수 최적화",
            "market_focus": [MarketType.KOSDAQ],  # KOSDAQ focus for higher volatility
            "risk_level": "medium-high",
            "expected_annual_return": 0.25,
            "max_drawdown_target": 0.18,
            
            "universe": {
                "market": "KOSDAQ",
                "min_market_cap": 50_000_000_000,  # 500억원 minimum
                "max_market_cap": 2_000_000_000_000,  # 2조원 maximum (avoid mega caps)
                "min_volume": 500000,
                "beta_range": [0.8, 2.0],  # Higher beta for momentum
                "exclude_new_listings": 90  # Exclude stocks listed < 90 days
            },
            
            "entry_conditions": {
                "rsi_signal": {
                    "period": 12,  # Shorter period for Korean market volatility
                    "oversold_threshold": 25,  # More extreme for KOSDAQ
                    "confirmation_days": 1
                },
                "price_action": {
                    "above_ma": 60,  # Above 60-day MA for trend confirmation
                    "recent_decline": 0.15,  # At least 15% decline from recent high
                    "support_level": True  # Near identified support level
                },
                "volume_pattern": {
                    "volume_surge": 2.0,  # 2x average volume
                    "selling_climax": True  # High volume with price decline
                },
                "korean_specific": {
                    "not_in_decline_phase": True,  # Avoid stocks in continuous decline
                    "institutional_support": True,  # Some institutional buying
                    "sector_rotation_favorable": True
                }
            },
            
            "exit_conditions": {
                "rsi_exit": {
                    "overbought_threshold": 75,  # Higher threshold for Korean market
                    "divergence_exit": True,  # Exit on RSI-price divergence
                    "momentum_fade": True
                },
                "profit_targets": {
                    "quick_profit": {
                        "target": 0.12,  # 12% quick profit
                        "time_limit": 5,  # Within 5 days
                        "partial_exit": 0.50  # Sell 50%
                    },
                    "main_target": 0.25  # 25% main target
                }
            },
            
            "position_sizing": {
                "method": PositionSizing.KELLY_CRITERION,
                "kelly_lookback": 252,  # 1 year lookback
                "max_kelly": 0.25,  # Cap Kelly at 25%
                "min_position": 0.02,  # Minimum 2%
                "volatility_adjustment": True
            }
        }
    
    def _create_chaebol_rotation_strategy(self) -> Dict[str, Any]:
        """Strategy leveraging Korean conglomerate relationships"""
        return {
            "id": "chaebol_rotation",
            "name": "재벌 순환 전략",
            "name_en": "Chaebol Rotation Strategy",
            "description": "한국 재벌 그룹 간 상관관계와 순환 패턴을 활용한 전략 - 삼성, LG, SK, 현대, 롯데 그룹 분석",
            "market_focus": [MarketType.KOSPI],
            "risk_level": "medium",
            "expected_annual_return": 0.22,
            "max_drawdown_target": 0.12,
            
            "universe": {
                "chaebol_groups": ["samsung", "lg", "sk", "hyundai", "lotte"],
                "min_market_cap": 500_000_000_000,  # 5000억원 minimum
                "liquidity_requirement": "high",
                "exclude_holding_companies": False  # Include holding companies
            },
            
            "entry_conditions": {
                # ... detailed chaebol rotation logic
            }
        }
    
    def _create_kospi_kosdaq_momentum_strategy(self) -> Dict[str, Any]:
        """Strategy exploiting KOSPI vs KOSDAQ momentum patterns"""
        return {
            "id": "kospi_kosdaq_momentum",
            "name": "코스피-코스닥 모멘텀 전략",
            "name_en": "KOSPI-KOSDAQ Momentum Strategy",
            "description": "코스피와 코스닥 시장 간 모멘텀 차이를 활용한 전략 - 시장 성격 차이와 자금 이동 패턴 활용",
            "market_focus": [MarketType.ALL],
            "risk_level": "medium-high",
            "expected_annual_return": 0.28,
            "max_drawdown_target": 0.20,
            
            "universe": {
                "dual_market_approach": True,
                "kospi_allocation_range": [0.3, 0.7],
                "kosdaq_allocation_range": [0.3, 0.7],
                "momentum_lookback": 60  # 60-day momentum comparison
            }
        }
    
    def _create_korean_market_timing_strategy(self) -> Dict[str, Any]:
        """Market timing strategy for Korean market patterns"""
        return {
            "id": "korean_market_timing",
            "name": "한국형 마켓 타이밍 전략",
            "name_en": "Korean Market Timing Strategy",
            "description": "한국 시장의 고유한 패턴을 활용한 마켓 타이밍 전략 - 외국인 매매, 프로그램 매매, 원달러 환율 연동",
            "market_focus": [MarketType.ALL],
            "risk_level": "high",
            "expected_annual_return": 0.35,
            "max_drawdown_target": 0.25,
            
            "timing_factors": {
                "foreign_flow": True,  # Foreign investor flow
                "program_trading": True,  # Program trading patterns
                "usd_krw_correlation": True,  # USD/KRW impact
                "vix_korea": True,  # Korean VIX equivalent
                "overnight_gaps": True,  # Overnight gap patterns
                "lunch_break_patterns": True  # Lunch break trading patterns
            }
        }
    
    def _create_usd_krw_impact_strategy(self) -> Dict[str, Any]:
        """Strategy based on USD/KRW currency impact"""
        return {
            "id": "usd_krw_impact",
            "name": "원달러 연동 전략",
            "name_en": "USD/KRW Impact Strategy",
            "description": "원달러 환율 변동이 한국 수출 기업에 미치는 영향을 활용한 전략 - 환율 민감 종목 선별 투자",
            "market_focus": [MarketType.KOSPI],
            "risk_level": "medium",
            "expected_annual_return": 0.20,
            "max_drawdown_target": 0.15,
            
            "currency_factors": {
                "usd_krw_threshold": 0.02,  # 2% movement threshold
                "export_dependency": 0.50,  # 50%+ export revenue
                "currency_hedge_ratio": 0.30,  # Consider hedging ratio
                "sector_focus": ["technology", "automotive", "steel", "petrochemical"]
            }
        }
    
    def _create_korean_volatility_breakout_strategy(self) -> Dict[str, Any]:
        """Volatility breakout strategy adapted for Korean market"""
        return {
            "id": "korean_volatility_breakout",
            "name": "한국형 변동성 돌파 전략",
            "name_en": "Korean Volatility Breakout Strategy",
            "description": "한국 시장의 변동성 특성을 고려한 돌파 전략 - 상한가/하한가 시스템과 급등락 패턴 활용",
            "market_focus": [MarketType.KOSDAQ],
            "risk_level": "high",
            "expected_annual_return": 0.40,
            "max_drawdown_target": 0.30
        }
    
    def _create_korean_gap_trading_strategy(self) -> Dict[str, Any]:
        """Gap trading strategy for Korean market"""
        return {
            "id": "korean_gap_trading",
            "name": "한국형 갭 트레이딩 전략",
            "name_en": "Korean Gap Trading Strategy",
            "description": "한국 시장의 빈번한 갭 발생을 활용한 전략 - 갭업/갭다운 패턴과 갭 메우기 현상 활용",
            "market_focus": [MarketType.ALL],
            "risk_level": "high",
            "expected_annual_return": 0.30,
            "max_drawdown_target": 0.25
        }
    
    def _create_korean_sector_rotation_strategy(self) -> Dict[str, Any]:
        """Sector rotation strategy for Korean market"""
        return {
            "id": "korean_sector_rotation",
            "name": "한국형 섹터 순환 전략",
            "name_en": "Korean Sector Rotation Strategy",
            "description": "한국 시장의 섹터별 순환 패턴을 활용한 전략 - 경제 사이클과 정부 정책에 따른 섹터 로테이션",
            "market_focus": [MarketType.ALL],
            "risk_level": "medium",
            "expected_annual_return": 0.24,
            "max_drawdown_target": 0.18
        }
    
    def _create_korean_value_momentum_strategy(self) -> Dict[str, Any]:
        """Value-momentum combination strategy for Korean market"""
        return {
            "id": "korean_value_momentum",
            "name": "한국형 가치모멘텀 전략",
            "name_en": "Korean Value-Momentum Strategy",
            "description": "한국 시장에서 가치주와 모멘텀의 결합 전략 - PER, PBR 등 가치 지표와 기술적 모멘텀 융합",
            "market_focus": [MarketType.ALL],
            "risk_level": "medium",
            "expected_annual_return": 0.26,
            "max_drawdown_target": 0.16
        }
    
    def calculate_strategy_signals(self, df: pd.DataFrame, strategy_config: Dict[str, Any], 
                                 symbol: str = None) -> pd.DataFrame:
        """Calculate trading signals for Korean market strategies"""
        try:
            # Add all technical indicators
            df = self.calculator.calculate_all_indicators(df, symbol)
            
            # Initialize signal columns
            df['buy_signal'] = False
            df['sell_signal'] = False
            df['signal_strength'] = 0.0
            df['signal_reason'] = ""
            
            strategy_id = strategy_config.get('id')
            
            if strategy_id == 'enhanced_golden_cross_kr':
                df = self._calculate_enhanced_golden_cross_signals(df, strategy_config)
            elif strategy_id == 'korean_rsi_reversal':
                df = self._calculate_korean_rsi_signals(df, strategy_config)
            elif strategy_id == 'chaebol_rotation':
                df = self._calculate_chaebol_rotation_signals(df, strategy_config, symbol)
            elif strategy_id == 'kospi_kosdaq_momentum':
                df = self._calculate_kospi_kosdaq_momentum_signals(df, strategy_config)
            elif strategy_id == 'korean_market_timing':
                df = self._calculate_korean_market_timing_signals(df, strategy_config)
            elif strategy_id == 'usd_krw_impact':
                df = self._calculate_usd_krw_impact_signals(df, strategy_config, symbol)
            
            # Apply Korean market filters
            df = self._apply_korean_market_filters(df, strategy_config)
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating strategy signals: {e}")
            return df
    
    def _calculate_enhanced_golden_cross_signals(self, df: pd.DataFrame, 
                                               config: Dict[str, Any]) -> pd.DataFrame:
        """Calculate signals for enhanced golden cross strategy"""
        try:
            entry_conditions = config.get('entry_conditions', {})
            
            # Primary golden cross signal
            primary = entry_conditions.get('primary_signal', {})
            ma_short = primary.get('ma_short', 5)
            ma_long = primary.get('ma_long', 20)
            confirmation_period = primary.get('confirmation_period', 2)
            
            # Golden cross detection
            golden_cross = (df[f'ma_{ma_short}'] > df[f'ma_{ma_long}']) & \
                          (df[f'ma_{ma_short}'].shift(1) <= df[f'ma_{ma_long}'].shift(1))
            
            # Volume confirmation
            volume_conf = entry_conditions.get('volume_confirmation', {})
            volume_threshold = volume_conf.get('volume_ratio_threshold', 1.5)
            volume_ma_period = volume_conf.get('volume_ma_period', 20)
            
            volume_condition = df[f'volume_ratio_{volume_ma_period}'] > volume_threshold
            
            # Volatility filter
            volatility_filter = entry_conditions.get('volatility_filter', {})
            atr_max = volatility_filter.get('atr_threshold_max', 0.08)
            
            volatility_condition = df['atr_pct'] < (atr_max * 100)
            
            # Technical confirmation
            tech_conf = entry_conditions.get('technical_confirmation', {})
            rsi_range = tech_conf.get('rsi_range', [30, 70])
            
            rsi_condition = (df['rsi_14'] >= rsi_range[0]) & (df['rsi_14'] <= rsi_range[1])
            macd_condition = df['macd'] > df['macd_signal']
            
            # Korean specific filters
            korean_filters = entry_conditions.get('korean_specific', {})
            
            no_price_limit = ~((df['upper_limit_hit'] == 1) | (df['lower_limit_hit'] == 1))
            gap_filter_threshold = korean_filters.get('gap_filter', 0.03)
            no_large_gaps = ~((df['gap_up'] == 1) | (df['gap_down'] == 1))
            
            # Combine all conditions
            buy_condition = (
                golden_cross &
                volume_condition &
                volatility_condition &
                rsi_condition &
                macd_condition &
                no_price_limit &
                no_large_gaps
            )
            
            # Apply confirmation period
            buy_signal = buy_condition.rolling(window=confirmation_period).sum() >= confirmation_period
            
            df['buy_signal'] = buy_signal
            
            # Calculate signal strength
            strength_factors = []
            strength_factors.append(np.where(volume_condition, 0.3, 0))
            strength_factors.append(np.where(volatility_condition, 0.2, 0))
            strength_factors.append(np.where(rsi_condition, 0.2, 0))
            strength_factors.append(np.where(macd_condition, 0.15, 0))
            strength_factors.append(np.where(no_price_limit, 0.15, 0))
            
            df['signal_strength'] = np.sum(strength_factors, axis=0)
            
            # Add signal reasons
            df.loc[buy_signal, 'signal_reason'] = "Enhanced Golden Cross with Korean Market Confirmation"
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating enhanced golden cross signals: {e}")
            return df
    
    def _calculate_korean_rsi_signals(self, df: pd.DataFrame, 
                                    config: Dict[str, Any]) -> pd.DataFrame:
        """Calculate signals for Korean RSI reversal strategy"""  
        try:
            entry_conditions = config.get('entry_conditions', {})
            
            # RSI signal
            rsi_signal = entry_conditions.get('rsi_signal', {})
            rsi_period = rsi_signal.get('period', 12)
            oversold_threshold = rsi_signal.get('oversold_threshold', 25)
            
            rsi_oversold = df[f'rsi_{rsi_period}'] < oversold_threshold
            
            # Price action confirmation
            price_action = entry_conditions.get('price_action', {})
            ma_period = price_action.get('above_ma', 60)
            recent_decline = price_action.get('recent_decline', 0.15)
            
            above_ma_condition = df['close'] > df[f'ma_{ma_period}']
            
            # Calculate recent decline from high
            rolling_high = df['high'].rolling(window=20).max()
            decline_from_high = (rolling_high - df['close']) / rolling_high
            decline_condition = decline_from_high >= recent_decline
            
            # Volume surge
            volume_pattern = entry_conditions.get('volume_pattern', {})
            volume_surge_threshold = volume_pattern.get('volume_surge', 2.0)
            
            volume_surge = df['volume_ratio_20'] > volume_surge_threshold
            
            # Combine conditions
            buy_condition = (
                rsi_oversold &
                above_ma_condition &
                decline_condition &
                volume_surge
            )
            
            df['buy_signal'] = buy_condition
            
            # Exit conditions
            exit_conditions = config.get('exit_conditions', {})
            rsi_exit = exit_conditions.get('rsi_exit', {})
            overbought_threshold = rsi_exit.get('overbought_threshold', 75)
            
            df['sell_signal'] = df[f'rsi_{rsi_period}'] > overbought_threshold
            
            # Signal strength
            strength = 0.0
            strength += np.where(rsi_oversold, 0.4, 0)
            strength += np.where(volume_surge, 0.3, 0)
            strength += np.where(decline_condition, 0.2, 0)
            strength += np.where(above_ma_condition, 0.1, 0)
            
            df['signal_strength'] = strength
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating Korean RSI signals: {e}")
            return df
    
    def _calculate_chaebol_rotation_signals(self, df: pd.DataFrame, 
                                          config: Dict[str, Any], symbol: str) -> pd.DataFrame:
        """Calculate signals for chaebol rotation strategy"""
        try:
            # Determine which chaebol group this stock belongs to
            chaebol_group = self._get_chaebol_group(symbol)
            
            if not chaebol_group:
                return df
            
            # Calculate relative strength vs chaebol peers
            # This would require additional data about peer stocks
            # For now, use sector-based signals
            
            # Momentum signal
            momentum_20 = df['korean_momentum_20']
            sector_outperformance = momentum_20 > momentum_20.rolling(window=60).mean()
            
            # Volume confirmation
            institutional_activity = df['institutional_activity'] == 1
            
            df['buy_signal'] = sector_outperformance & institutional_activity
            df['signal_strength'] = np.where(df['buy_signal'], 0.8, 0.0)
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating chaebol rotation signals: {e}")
            return df
    
    def _calculate_kospi_kosdaq_momentum_signals(self, df: pd.DataFrame, 
                                               config: Dict[str, Any]) -> pd.DataFrame:
        """Calculate signals for KOSPI/KOSDAQ momentum strategy"""
        try:
            # This would require market index data to compare
            # For now, use individual stock momentum
            
            momentum_signal = (df['korean_momentum_10'] > 5.0) & (df['korean_momentum_20'] > 8.0)
            volume_confirmation = df['volume_ratio_20'] > 1.5
            
            df['buy_signal'] = momentum_signal & volume_confirmation
            df['signal_strength'] = np.where(df['buy_signal'], 0.7, 0.0)
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating KOSPI/KOSDAQ momentum signals: {e}")
            return df
    
    def _calculate_korean_market_timing_signals(self, df: pd.DataFrame, 
                                              config: Dict[str, Any]) -> pd.DataFrame:
        """Calculate signals for Korean market timing strategy"""
        try:
            # Market timing based on multiple Korean-specific factors
            timing_factors = config.get('timing_factors', {})
            
            # Overnight gap patterns
            if timing_factors.get('overnight_gaps', False):
                gap_signal = (df['gap_up'] == 1) & (df['volume_ratio_20'] > 2.0)
            else:
                gap_signal = pd.Series([False] * len(df), index=df.index)
            
            # Strong momentum with volume
            momentum_signal = (df['korean_momentum_5'] > 3.0) & (df['volume_spike'] == 1)
            
            # Technical strength
            technical_signal = (df['rsi_14'] > 50) & (df['macd'] > df['macd_signal'])
            
            df['buy_signal'] = gap_signal | (momentum_signal & technical_signal)
            df['signal_strength'] = np.where(df['buy_signal'], 0.9, 0.0)
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating Korean market timing signals: {e}")
            return df
    
    def _calculate_usd_krw_impact_signals(self, df: pd.DataFrame, 
                                        config: Dict[str, Any], symbol: str) -> pd.DataFrame:
        """Calculate signals for USD/KRW impact strategy"""
        try:
            # This would require USD/KRW exchange rate data
            # For now, use export-oriented stock characteristics
            
            # Assume export-oriented stocks benefit from won weakness
            # Use volume and momentum as proxies
            
            export_benefit_signal = (df['korean_momentum_10'] > 2.0) & \
                                  (df['institutional_activity'] == 1)
            
            # Technical confirmation
            technical_strength = (df['close'] > df['ma_20']) & (df['rsi_14'] > 45)
            
            df['buy_signal'] = export_benefit_signal & technical_strength
            df['signal_strength'] = np.where(df['buy_signal'], 0.6, 0.0)
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating USD/KRW impact signals: {e}")
            return df
    
    def _apply_korean_market_filters(self, df: pd.DataFrame, 
                                   config: Dict[str, Any]) -> pd.DataFrame:
        """Apply Korean market-specific filters to signals"""
        try:
            # Filter out signals during price limit hits
            price_limit_filter = ~((df['upper_limit_hit'] == 1) | (df['lower_limit_hit'] == 1))
            
            # Filter out extreme volatility days
            volatility_filter = df['korean_volatility'] < df['korean_volatility'].rolling(20).quantile(0.95)
            
            # Apply filters
            df['buy_signal'] = df['buy_signal'] & price_limit_filter & volatility_filter
            df['sell_signal'] = df['sell_signal'] & price_limit_filter
            
            # Adjust signal strength based on Korean market conditions
            korean_strength_multiplier = np.where(df['korean_strength_index'] >= 2, 1.2, 1.0)
            korean_strength_multiplier = np.where(df['korean_strength_index'] == 0, 0.8, korean_strength_multiplier)
            
            df['signal_strength'] = df['signal_strength'] * korean_strength_multiplier
            
            return df
            
        except Exception as e:
            logger.error(f"Error applying Korean market filters: {e}")
            return df
    
    def _get_chaebol_group(self, symbol: str) -> Optional[str]:
        """Determine which chaebol group a stock belongs to"""
        for group, stocks in self.chaebol_groups.items():
            if symbol in stocks:
                return group
        return None
    
    def calculate_position_size(self, strategy_config: Dict[str, Any], 
                              portfolio_value: float, 
                              stock_price: float,
                              volatility: float) -> Tuple[float, int]:
        """Calculate optimal position size using Korean market parameters"""
        try:
            position_sizing = strategy_config.get('position_sizing', {})
            method = position_sizing.get('method', PositionSizing.EQUAL_WEIGHT)
            
            if method == PositionSizing.EQUAL_WEIGHT:
                base_position = position_sizing.get('base_position', 0.05)
                position_value = portfolio_value * base_position
                
            elif method == PositionSizing.VOLATILITY_ADJUSTED:
                volatility_target = position_sizing.get('volatility_target', 0.02)
                base_position = position_sizing.get('base_position', 0.05)
                
                # Adjust position size based on volatility
                volatility_adjustment = volatility_target / max(volatility, 0.01)
                position_pct = min(base_position * volatility_adjustment, 
                                 position_sizing.get('max_position', 0.08))
                position_value = portfolio_value * position_pct
                
            elif method == PositionSizing.KELLY_CRITERION:
                # Simplified Kelly criterion
                win_rate = 0.55  # Assume 55% win rate
                avg_win = 0.12   # 12% average win
                avg_loss = 0.06  # 6% average loss
                
                kelly_pct = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
                max_kelly = position_sizing.get('max_kelly', 0.25)
                kelly_pct = min(kelly_pct, max_kelly)
                
                position_value = portfolio_value * max(kelly_pct, 0.02)
                
            else:  # Default to equal weight
                position_value = portfolio_value * 0.05
            
            # Calculate number of shares
            shares = int(position_value / stock_price)
            actual_position_value = shares * stock_price
            
            return actual_position_value, shares
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return portfolio_value * 0.05, int(portfolio_value * 0.05 / stock_price)
    
    def validate_strategy_performance(self, returns: pd.Series, 
                                    benchmark_returns: pd.Series,
                                    strategy_config: Dict[str, Any]) -> Dict[str, float]:
        """Validate strategy performance against Korean market benchmarks"""
        try:
            if len(returns) == 0:
                return {}
            
            # Basic performance metrics
            total_return = (1 + returns).prod() - 1
            annual_return = (1 + total_return) ** (252 / len(returns)) - 1
            volatility = returns.std() * np.sqrt(252)
            
            # Risk-adjusted metrics
            risk_free_rate = self.market_params.risk_free_rate
            excess_returns = returns - risk_free_rate / 252
            sharpe_ratio = excess_returns.mean() / returns.std() * np.sqrt(252)
            
            # Downside metrics
            downside_returns = returns[returns < 0]
            downside_volatility = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
            sortino_ratio = excess_returns.mean() / downside_volatility * np.sqrt(252) if downside_volatility > 0 else 0
            
            # Drawdown analysis
            cumulative = (1 + returns).cumprod()
            rolling_max = cumulative.expanding().max()
            drawdown = (cumulative - rolling_max) / rolling_max
            max_drawdown = drawdown.min()
            
            # Calmar ratio
            calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
            
            # Benchmark comparison
            if len(benchmark_returns) > 0:
                benchmark_total_return = (1 + benchmark_returns).prod() - 1
                alpha = total_return - benchmark_total_return
                
                # Beta calculation
                covariance = np.cov(returns, benchmark_returns)[0][1]
                benchmark_variance = benchmark_returns.var()
                beta = covariance / benchmark_variance if benchmark_variance != 0 else 1.0
                
                # Information ratio
                tracking_error = (returns - benchmark_returns).std() * np.sqrt(252)
                information_ratio = alpha / tracking_error if tracking_error > 0 else 0
            else:
                alpha = 0
                beta = 1.0
                information_ratio = 0
            
            # Korean market specific metrics
            win_rate = len(returns[returns > 0]) / len(returns)
            avg_win = returns[returns > 0].mean() if len(returns[returns > 0]) > 0 else 0
            avg_loss = returns[returns < 0].mean() if len(returns[returns < 0]) > 0 else 0
            profit_factor = abs(returns[returns > 0].sum() / returns[returns < 0].sum()) if returns[returns < 0].sum() != 0 else 0
            
            # Korean volatility adjustment
            market_focus = strategy_config.get('market_focus', [MarketType.KOSPI])
            if MarketType.KOSDAQ in market_focus:
                volatility_adjusted_return = annual_return / (volatility * self.market_params.kosdaq_volatility_multiplier)
            else:
                volatility_adjusted_return = annual_return / volatility
            
            return {
                'total_return': float(total_return),
                'annual_return': float(annual_return),
                'volatility': float(volatility),
                'sharpe_ratio': float(sharpe_ratio),
                'sortino_ratio': float(sortino_ratio),
                'calmar_ratio': float(calmar_ratio),
                'max_drawdown': float(max_drawdown),
                'alpha': float(alpha),
                'beta': float(beta),
                'information_ratio': float(information_ratio),
                'win_rate': float(win_rate),
                'avg_win': float(avg_win),
                'avg_loss': float(avg_loss),
                'profit_factor': float(profit_factor),
                'volatility_adjusted_return': float(volatility_adjusted_return)
            }
            
        except Exception as e:
            logger.error(f"Error validating strategy performance: {e}")
            return {}
    
    def get_korean_strategy_recommendations(self, market_conditions: Dict[str, Any]) -> List[str]:
        """Get strategy recommendations based on current Korean market conditions"""
        try:
            recommendations = []
            
            # Market volatility
            volatility = market_conditions.get('volatility', 'medium')
            
            if volatility == 'high':
                recommendations.extend([
                    'korean_volatility_breakout',
                    'korean_gap_trading',
                    'korean_rsi_reversal'
                ])
            elif volatility == 'low':
                recommendations.extend([
                    'enhanced_golden_cross_kr',
                    'chaebol_rotation',
                    'korean_value_momentum'
                ])
            else:
                recommendations.extend([
                    'kospi_kosdaq_momentum',
                    'korean_sector_rotation',
                    'usd_krw_impact'
                ])
            
            # USD/KRW trend
            usd_krw_trend = market_conditions.get('usd_krw_trend', 'neutral')
            if usd_krw_trend in ['weakening_won', 'strengthening_dollar']:
                recommendations.append('usd_krw_impact')
            
            # Market phase
            market_phase = market_conditions.get('market_phase', 'neutral')
            if market_phase == 'bull_market':
                recommendations.extend(['kospi_kosdaq_momentum', 'korean_market_timing'])
            elif market_phase == 'bear_market':
                recommendations.extend(['korean_rsi_reversal', 'korean_value_momentum'])
            
            # Remove duplicates and return top 5
            recommendations = list(dict.fromkeys(recommendations))[:5]
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting strategy recommendations: {e}")
            return ['enhanced_golden_cross_kr']  # Fallback