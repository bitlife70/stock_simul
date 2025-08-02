"""
Korean Market Risk Management System

Advanced risk management system specifically designed for Korean stock markets,
incorporating unique characteristics such as price limits, market volatility patterns,
currency risks, and regulatory constraints.
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

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class MarketRegime(Enum):
    BULL_MARKET = "bull_market"
    BEAR_MARKET = "bear_market" 
    SIDEWAYS = "sideways"
    HIGH_VOLATILITY = "high_volatility"
    CRISIS = "crisis"

@dataclass
class KoreanRiskParameters:
    """Korean market-specific risk parameters"""
    # Portfolio risk limits
    max_portfolio_volatility: float = 0.20  # 20% annual volatility limit
    max_daily_loss: float = 0.03  # 3% maximum daily loss
    max_drawdown: float = 0.15  # 15% maximum drawdown
    
    # Position risk limits
    max_single_position: float = 0.08  # 8% maximum single position
    max_sector_exposure: float = 0.30  # 30% maximum sector exposure
    max_chaebol_exposure: float = 0.25  # 25% maximum chaebol group exposure
    
    # Korean market specific
    max_price_limit_stocks: int = 3  # Maximum stocks at price limits
    currency_hedge_threshold: float = 0.20  # Hedge when FX exposure > 20%
    won_volatility_multiplier: float = 1.2  # Won volatility adjustment
    
    # Liquidity requirements
    min_daily_volume: int = 1_000_000  # Minimum daily volume in USD
    max_position_vs_volume: float = 0.10  # Max 10% of daily volume
    
    # Time-based limits
    max_holding_period: int = 120  # Maximum 120 days holding
    rebalance_frequency: int = 5  # Rebalance every 5 days

@dataclass
class RiskMetrics:
    """Container for calculated risk metrics"""
    portfolio_var: float = 0.0  # Value at Risk
    portfolio_cvar: float = 0.0  # Conditional Value at Risk
    volatility: float = 0.0  # Portfolio volatility
    beta: float = 1.0  # Market beta
    tracking_error: float = 0.0  # Tracking error vs benchmark
    sharpe_ratio: float = 0.0  # Risk-adjusted return
    max_drawdown: float = 0.0  # Maximum drawdown
    korean_risk_score: float = 0.0  # Korean market specific risk score

class KoreanRiskManager:
    """Advanced risk management system for Korean stock markets"""
    
    def __init__(self, risk_params: Optional[KoreanRiskParameters] = None):
        self.risk_params = risk_params or KoreanRiskParameters()
        self.market_regime = MarketRegime.SIDEWAYS
        
        # Korean market historical data for calibration
        self.kospi_volatility_history = 0.18  # Historical KOSPI volatility
        self.kosdaq_volatility_history = 0.28  # Historical KOSDAQ volatility
        self.usd_krw_volatility = 0.12  # USD/KRW volatility
        
        # Sector correlation matrix (simplified)
        self.sector_correlations = {
            'technology': {'finance': 0.3, 'automotive': 0.4, 'steel': 0.5},
            'finance': {'technology': 0.3, 'automotive': 0.2, 'steel': 0.3},
            'automotive': {'technology': 0.4, 'finance': 0.2, 'steel': 0.6},
            'steel': {'technology': 0.5, 'finance': 0.3, 'automotive': 0.6}
        }
        
        # Chaebol group mappings for concentration risk
        self.chaebol_groups = {
            "samsung": ["005930", "000810", "028050", "018260", "032830"],
            "lg": ["051910", "066570", "003550", "034220", "006360"],  
            "sk": ["000660", "096770", "034730", "017800", "018880"],
            "hyundai": ["005380", "000270", "012330", "001450", "005490"],
            "lotte": ["011170", "023530", "280360", "071050", "041610"]
        }
    
    def assess_portfolio_risk(self, portfolio: Dict[str, float], 
                            market_data: Dict[str, pd.DataFrame],
                            benchmark_returns: Optional[pd.Series] = None) -> RiskMetrics:
        """Comprehensive portfolio risk assessment"""
        try:
            if not portfolio:
                return RiskMetrics()
            
            # Calculate position-level risks
            position_risks = {}
            total_portfolio_value = sum(portfolio.values())
            
            for symbol, position_value in portfolio.items():
                if symbol in market_data:
                    position_risks[symbol] = self._calculate_position_risk(
                        symbol, position_value, market_data[symbol], total_portfolio_value
                    )
            
            # Calculate portfolio-level metrics
            portfolio_volatility = self._calculate_portfolio_volatility(
                portfolio, market_data, position_risks
            )
            
            portfolio_var = self._calculate_portfolio_var(
                portfolio, market_data, confidence_level=0.05
            )
            
            portfolio_cvar = self._calculate_portfolio_cvar(
                portfolio, market_data, confidence_level=0.05
            )
            
            # Korean market specific risk score
            korean_risk_score = self._calculate_korean_risk_score(
                portfolio, market_data, position_risks
            )
            
            # Beta calculation vs Korean market
            portfolio_beta = self._calculate_portfolio_beta(
                portfolio, market_data, benchmark_returns
            )
            
            # Maximum drawdown
            max_drawdown = self._calculate_portfolio_max_drawdown(
                portfolio, market_data
            )
            
            # Tracking error vs benchmark
            tracking_error = self._calculate_tracking_error(
                portfolio, market_data, benchmark_returns
            )
            
            return RiskMetrics(
                portfolio_var=portfolio_var,
                portfolio_cvar=portfolio_cvar,
                volatility=portfolio_volatility,
                beta=portfolio_beta,
                tracking_error=tracking_error,
                max_drawdown=max_drawdown,
                korean_risk_score=korean_risk_score
            )
            
        except Exception as e:
            logger.error(f"Error assessing portfolio risk: {e}")
            return RiskMetrics()
    
    def _calculate_position_risk(self, symbol: str, position_value: float,
                               stock_data: pd.DataFrame, portfolio_value: float) -> Dict[str, float]:
        """Calculate individual position risk metrics"""
        try:
            if len(stock_data) < 30:
                return {"volatility": 0.2, "var": 0.05, "liquidity_risk": 0.5}
            
            returns = stock_data['close'].pct_change().dropna()
            
            # Volatility (annualized)
            volatility = returns.std() * np.sqrt(252)
            
            # Value at Risk (5% confidence level)
            var_5 = np.percentile(returns, 5)
            
            # Liquidity risk based on volume
            avg_volume = stock_data['volume'].mean() if 'volume' in stock_data.columns else 1000000
            position_weight = position_value / portfolio_value
            liquidity_risk = min(position_weight / (avg_volume * 0.1), 1.0)  # Max 10% of volume
            
            # Korean market specific adjustments
            market_type = self._determine_market_type(symbol)
            if market_type == "KOSDAQ":
                volatility *= 1.3  # KOSDAQ volatility adjustment
                liquidity_risk *= 1.2
            
            # Price limit risk
            if 'upper_limit_hit' in stock_data.columns:
                recent_limits = stock_data['upper_limit_hit'].tail(10).sum() + \
                              stock_data['lower_limit_hit'].tail(10).sum()
                price_limit_risk = min(recent_limits / 10.0, 1.0)
            else:
                price_limit_risk = 0.0
            
            return {
                "volatility": float(volatility),
                "var": float(var_5),
                "liquidity_risk": float(liquidity_risk),
                "price_limit_risk": float(price_limit_risk),
                "market_type": market_type
            }
            
        except Exception as e:
            logger.error(f"Error calculating position risk for {symbol}: {e}")
            return {"volatility": 0.2, "var": 0.05, "liquidity_risk": 0.5}
    
    def _calculate_portfolio_volatility(self, portfolio: Dict[str, float],
                                      market_data: Dict[str, pd.DataFrame],
                                      position_risks: Dict[str, Dict]) -> float:
        """Calculate portfolio volatility with correlation adjustments"""
        try:
            total_value = sum(portfolio.values())
            if total_value == 0:
                return 0.0
            
            # Calculate weighted volatility
            weighted_vol = 0.0
            correlation_adjustment = 0.0
            
            for symbol, position_value in portfolio.items():
                weight = position_value / total_value
                position_vol = position_risks.get(symbol, {}).get('volatility', 0.2)
                weighted_vol += (weight ** 2) * (position_vol ** 2)
            
            # Add correlation effects (simplified)
            # In practice, would use full covariance matrix
            n_positions = len(portfolio)
            if n_positions > 1:
                avg_correlation = 0.3  # Assume 30% average correlation for Korean stocks
                correlation_adjustment = 2 * avg_correlation * weighted_vol * 0.5
            
            portfolio_variance = weighted_vol + correlation_adjustment
            return np.sqrt(max(portfolio_variance, 0.0))
            
        except Exception as e:
            logger.error(f"Error calculating portfolio volatility: {e}")
            return 0.2
    
    def _calculate_portfolio_var(self, portfolio: Dict[str, float],
                               market_data: Dict[str, pd.DataFrame],
                               confidence_level: float = 0.05) -> float:
        """Calculate portfolio Value at Risk"""
        try:
            total_value = sum(portfolio.values())
            if total_value == 0:
                return 0.0
            
            # Monte Carlo simulation for VaR
            n_simulations = 1000
            portfolio_returns = []
            
            # Get return series for each position
            return_series = {}
            for symbol in portfolio.keys():
                if symbol in market_data and len(market_data[symbol]) > 30:
                    returns = market_data[symbol]['close'].pct_change().dropna()
                    return_series[symbol] = returns.tail(252)  # Last year of data
            
            if not return_series:
                return total_value * 0.05  # 5% default VaR
            
            # Simulate portfolio returns
            for _ in range(n_simulations):
                portfolio_return = 0.0
                for symbol, position_value in portfolio.items():
                    if symbol in return_series:
                        weight = position_value / total_value
                        # Random sample from historical returns
                        random_return = np.random.choice(return_series[symbol])
                        portfolio_return += weight * random_return
                
                portfolio_returns.append(portfolio_return)
            
            # Calculate VaR
            var_return = np.percentile(portfolio_returns, confidence_level * 100)
            var_amount = abs(var_return * total_value)
            
            return float(var_amount)
            
        except Exception as e:
            logger.error(f"Error calculating portfolio VaR: {e}")
            return sum(portfolio.values()) * 0.05
    
    def _calculate_portfolio_cvar(self, portfolio: Dict[str, float],
                                market_data: Dict[str, pd.DataFrame],
                                confidence_level: float = 0.05) -> float:
        """Calculate portfolio Conditional Value at Risk (Expected Shortfall)"""
        try:
            var = self._calculate_portfolio_var(portfolio, market_data, confidence_level)
            # CVaR is typically 1.3x to 1.5x VaR for normal distributions
            # Korean market has higher tail risk, so use 1.6x
            return var * 1.6
            
        except Exception as e:
            logger.error(f"Error calculating portfolio CVaR: {e}")
            return sum(portfolio.values()) * 0.08
    
    def _calculate_korean_risk_score(self, portfolio: Dict[str, float],
                                   market_data: Dict[str, pd.DataFrame],
                                   position_risks: Dict[str, Dict]) -> float:
        """Calculate Korean market-specific risk score (0-1 scale)"""
        try:
            total_value = sum(portfolio.values())
            if total_value == 0:
                return 0.0
            
            risk_score = 0.0
            
            # 1. Price limit risk
            price_limit_risk = 0.0
            for symbol, risks in position_risks.items():
                weight = portfolio[symbol] / total_value
                price_limit_risk += weight * risks.get('price_limit_risk', 0.0)
            risk_score += price_limit_risk * 0.2
            
            # 2. Liquidity risk
            liquidity_risk = 0.0
            for symbol, risks in position_risks.items():
                weight = portfolio[symbol] / total_value
                liquidity_risk += weight * risks.get('liquidity_risk', 0.0)
            risk_score += liquidity_risk * 0.15
            
            # 3. Market concentration risk
            kospi_weight = 0.0
            kosdaq_weight = 0.0
            for symbol, position_value in portfolio.items():
                weight = position_value / total_value
                market_type = position_risks.get(symbol, {}).get('market_type', 'KOSPI')
                if market_type == 'KOSPI':
                    kospi_weight += weight
                else:
                    kosdaq_weight += weight
            
            # Penalize extreme concentration in either market
            market_concentration_risk = max(abs(kospi_weight - 0.6), abs(kosdaq_weight - 0.4))
            risk_score += market_concentration_risk * 0.1
            
            # 4. Chaebol concentration risk
            chaebol_exposures = {}
            for chaebol, stocks in self.chaebol_groups.items():
                exposure = sum(portfolio.get(stock, 0) for stock in stocks) / total_value
                chaebol_exposures[chaebol] = exposure
            
            max_chaebol_exposure = max(chaebol_exposures.values()) if chaebol_exposures else 0
            chaebol_risk = max(0, max_chaebol_exposure - self.risk_params.max_chaebol_exposure)
            risk_score += chaebol_risk * 0.15
            
            # 5. Volatility risk
            portfolio_vol = self._calculate_portfolio_volatility(portfolio, market_data, position_risks)
            vol_risk = max(0, portfolio_vol - self.risk_params.max_portfolio_volatility)
            risk_score += vol_risk * 0.2
            
            # 6. Currency exposure risk (for export-heavy stocks)
            # This would require additional data about export ratios
            currency_risk = 0.1  # Placeholder
            risk_score += currency_risk * 0.1
            
            # 7. Regulatory risk (for regulated sectors)
            # This would require sector classification
            regulatory_risk = 0.05  # Placeholder
            risk_score += regulatory_risk * 0.1
            
            return min(risk_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating Korean risk score: {e}")
            return 0.5
    
    def _calculate_portfolio_beta(self, portfolio: Dict[str, float],
                                market_data: Dict[str, pd.DataFrame],
                                benchmark_returns: Optional[pd.Series]) -> float:
        """Calculate portfolio beta vs Korean market benchmark"""
        try:
            if benchmark_returns is None or len(benchmark_returns) == 0:
                return 1.0
            
            total_value = sum(portfolio.values())
            if total_value == 0:
                return 1.0
            
            # Calculate weighted beta
            portfolio_beta = 0.0
            
            for symbol, position_value in portfolio.items():
                weight = position_value / total_value
                
                if symbol in market_data and len(market_data[symbol]) > 60:
                    stock_returns = market_data[symbol]['close'].pct_change().dropna()
                    
                    # Align with benchmark returns
                    common_dates = stock_returns.index.intersection(benchmark_returns.index)
                    if len(common_dates) > 30:
                        aligned_stock_returns = stock_returns.loc[common_dates]
                        aligned_benchmark_returns = benchmark_returns.loc[common_dates]
                        
                        # Calculate beta
                        covariance = np.cov(aligned_stock_returns, aligned_benchmark_returns)[0, 1]
                        benchmark_variance = np.var(aligned_benchmark_returns)
                        
                        if benchmark_variance > 0:
                            stock_beta = covariance / benchmark_variance
                        else:
                            stock_beta = 1.0
                    else:
                        stock_beta = 1.0
                else:
                    stock_beta = 1.0
                
                portfolio_beta += weight * stock_beta
            
            return float(portfolio_beta)
            
        except Exception as e:
            logger.error(f"Error calculating portfolio beta: {e}")
            return 1.0
    
    def _calculate_portfolio_max_drawdown(self, portfolio: Dict[str, float],
                                        market_data: Dict[str, pd.DataFrame]) -> float:
        """Calculate maximum drawdown for the portfolio"""
        try:
            # This would require historical portfolio values
            # For now, estimate based on individual stock max drawdowns
            total_value = sum(portfolio.values())
            if total_value == 0:
                return 0.0
            
            weighted_max_dd = 0.0
            
            for symbol, position_value in portfolio.items():
                weight = position_value / total_value
                
                if symbol in market_data and len(market_data[symbol]) > 60:
                    prices = market_data[symbol]['close']
                    running_max = prices.expanding().max()
                    drawdown = (prices - running_max) / running_max
                    max_drawdown = drawdown.min()
                else:
                    max_drawdown = -0.2  # Default assumption
                
                weighted_max_dd += weight * abs(max_drawdown)
            
            return float(weighted_max_dd)
            
        except Exception as e:
            logger.error(f"Error calculating portfolio max drawdown: {e}")
            return 0.2
    
    def _calculate_tracking_error(self, portfolio: Dict[str, float],
                                market_data: Dict[str, pd.DataFrame],
                                benchmark_returns: Optional[pd.Series]) -> float:
        """Calculate tracking error vs benchmark"""
        try:
            if benchmark_returns is None:
                return 0.0
            
            # This would require historical portfolio returns
            # For now, estimate based on beta and correlation
            portfolio_beta = self._calculate_portfolio_beta(portfolio, market_data, benchmark_returns)
            
            # Estimate tracking error based on beta deviation and idiosyncratic risk
            beta_tracking_error = abs(portfolio_beta - 1.0) * benchmark_returns.std() * np.sqrt(252)
            idiosyncratic_risk = 0.05  # Estimated idiosyncratic risk
            
            tracking_error = np.sqrt(beta_tracking_error**2 + idiosyncratic_risk**2)
            
            return float(tracking_error)
            
        except Exception as e:
            logger.error(f"Error calculating tracking error: {e}")
            return 0.1
    
    def check_risk_limits(self, portfolio: Dict[str, float],
                         market_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Check portfolio against all risk limits"""
        try:
            violations = []
            warnings = []
            
            total_value = sum(portfolio.values())
            if total_value == 0:
                return {"violations": [], "warnings": [], "overall_status": "OK"}
            
            # Check position size limits
            for symbol, position_value in portfolio.items():
                position_weight = position_value / total_value
                
                if position_weight > self.risk_params.max_single_position:
                    violations.append({
                        "type": "position_size",
                        "symbol": symbol,
                        "current": position_weight,
                        "limit": self.risk_params.max_single_position,
                        "severity": "HIGH"
                    })
                elif position_weight > self.risk_params.max_single_position * 0.8:
                    warnings.append({
                        "type": "position_size",
                        "symbol": symbol,
                        "current": position_weight,
                        "limit": self.risk_params.max_single_position,
                        "severity": "MEDIUM"
                    })
            
            # Check chaebol concentration
            for chaebol, stocks in self.chaebol_groups.items():
                chaebol_exposure = sum(portfolio.get(stock, 0) for stock in stocks) / total_value
                
                if chaebol_exposure > self.risk_params.max_chaebol_exposure:
                    violations.append({
                        "type": "chaebol_concentration",
                        "chaebol": chaebol,
                        "current": chaebol_exposure,
                        "limit": self.risk_params.max_chaebol_exposure,
                        "severity": "HIGH"
                    })
            
            # Check liquidity limits
            price_limit_count = 0
            for symbol in portfolio.keys():
                if symbol in market_data:
                    stock_data = market_data[symbol]
                    if 'upper_limit_hit' in stock_data.columns or 'lower_limit_hit' in stock_data.columns:
                        recent_upper = stock_data.get('upper_limit_hit', pd.Series([0])).tail(1).iloc[0]
                        recent_lower = stock_data.get('lower_limit_hit', pd.Series([0])).tail(1).iloc[0]
                        if recent_upper == 1 or recent_lower == 1:
                            price_limit_count += 1
            
            if price_limit_count > self.risk_params.max_price_limit_stocks:
                violations.append({
                    "type": "price_limit_stocks",
                    "current": price_limit_count,
                    "limit": self.risk_params.max_price_limit_stocks,
                    "severity": "MEDIUM"
                })
            
            # Check portfolio volatility
            portfolio_vol = self._calculate_portfolio_volatility(
                portfolio, market_data, {}
            )
            
            if portfolio_vol > self.risk_params.max_portfolio_volatility:
                violations.append({
                    "type": "portfolio_volatility",
                    "current": portfolio_vol,
                    "limit": self.risk_params.max_portfolio_volatility,
                    "severity": "HIGH"
                })
            
            # Determine overall status
            if violations:
                overall_status = "VIOLATION"
            elif warnings:
                overall_status = "WARNING"
            else:
                overall_status = "OK"
            
            return {
                "violations": violations,
                "warnings": warnings,
                "overall_status": overall_status,
                "total_issues": len(violations) + len(warnings)
            }
            
        except Exception as e:
            logger.error(f"Error checking risk limits: {e}")
            return {"violations": [], "warnings": [], "overall_status": "ERROR"}
    
    def suggest_risk_adjustments(self, portfolio: Dict[str, float],
                               market_data: Dict[str, pd.DataFrame],
                               risk_limits: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest adjustments to bring portfolio within risk limits"""
        try:
            suggestions = []
            
            violations = risk_limits.get("violations", [])
            warnings = risk_limits.get("warnings", [])
            
            for violation in violations:
                if violation["type"] == "position_size":
                    symbol = violation["symbol"]
                    current_weight = violation["current"]
                    target_weight = violation["limit"]
                    
                    suggestions.append({
                        "action": "reduce_position",
                        "symbol": symbol,
                        "current_weight": current_weight,
                        "target_weight": target_weight,
                        "reduction_amount": current_weight - target_weight,
                        "priority": "HIGH"
                    })
                
                elif violation["type"] == "chaebol_concentration":
                    chaebol = violation["chaebol"]
                    current_exposure = violation["current"]
                    target_exposure = violation["limit"]
                    
                    # Find the largest positions in this chaebol to reduce
                    chaebol_stocks = self.chaebol_groups[chaebol]
                    total_value = sum(portfolio.values())
                    
                    for stock in chaebol_stocks:
                        if stock in portfolio:
                            stock_weight = portfolio[stock] / total_value
                            suggestions.append({
                                "action": "reduce_chaebol_exposure",
                                "symbol": stock,
                                "chaebol": chaebol,
                                "current_weight": stock_weight,
                                "suggested_reduction": stock_weight * 0.3,  # Reduce by 30%
                                "priority": "HIGH"
                            })
                
                elif violation["type"] == "portfolio_volatility":
                    # Suggest reducing positions in highest volatility stocks
                    high_vol_stocks = []
                    for symbol in portfolio.keys():
                        if symbol in market_data:
                            stock_data = market_data[symbol]
                            if len(stock_data) > 30:
                                returns = stock_data['close'].pct_change().dropna()
                                volatility = returns.std() * np.sqrt(252)
                                high_vol_stocks.append((symbol, volatility))
                    
                    # Sort by volatility and suggest reducing top volatility stocks
                    high_vol_stocks.sort(key=lambda x: x[1], reverse=True)
                    
                    for symbol, vol in high_vol_stocks[:3]:  # Top 3 most volatile
                        suggestions.append({
                            "action": "reduce_high_volatility",
                            "symbol": symbol,
                            "volatility": vol,
                            "suggested_reduction": 0.2,  # Reduce by 20%
                            "priority": "MEDIUM"
                        })
            
            # Add diversification suggestions
            if len(portfolio) < 5:
                suggestions.append({
                    "action": "increase_diversification",
                    "current_stocks": len(portfolio),
                    "suggested_minimum": 8,
                    "priority": "MEDIUM"
                })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating risk adjustment suggestions: {e}")
            return []
    
    def _determine_market_type(self, symbol: str) -> str:
        """Determine if stock is KOSPI or KOSDAQ"""
        try:
            if symbol.isdigit() and len(symbol) == 6:
                if symbol.startswith('0'):
                    return "KOSPI"
                else:
                    return "KOSDAQ"
            return "KOSPI"
        except:
            return "KOSPI"
    
    def update_market_regime(self, market_indicators: Dict[str, float]):
        """Update market regime assessment based on current indicators"""
        try:
            vix_level = market_indicators.get('vix', 20)
            trend_strength = market_indicators.get('trend_strength', 0)
            volume_trend = market_indicators.get('volume_trend', 1.0)
            
            if vix_level > 35:
                self.market_regime = MarketRegime.CRISIS
            elif vix_level > 25:
                self.market_regime = MarketRegime.HIGH_VOLATILITY
            elif trend_strength > 0.05:
                self.market_regime = MarketRegime.BULL_MARKET
            elif trend_strength < -0.05:
                self.market_regime = MarketRegime.BEAR_MARKET
            else:
                self.market_regime = MarketRegime.SIDEWAYS
                
            # Adjust risk parameters based on regime
            self._adjust_risk_parameters_for_regime()
            
        except Exception as e:
            logger.error(f"Error updating market regime: {e}")
    
    def _adjust_risk_parameters_for_regime(self):
        """Adjust risk parameters based on current market regime"""
        try:
            base_params = KoreanRiskParameters()
            
            if self.market_regime == MarketRegime.CRISIS:
                self.risk_params.max_portfolio_volatility = base_params.max_portfolio_volatility * 0.7
                self.risk_params.max_single_position = base_params.max_single_position * 0.8
                self.risk_params.max_daily_loss = base_params.max_daily_loss * 0.8
                
            elif self.market_regime == MarketRegime.HIGH_VOLATILITY:
                self.risk_params.max_portfolio_volatility = base_params.max_portfolio_volatility * 0.85
                self.risk_params.max_single_position = base_params.max_single_position * 0.9
                
            elif self.market_regime == MarketRegime.BULL_MARKET:
                self.risk_params.max_portfolio_volatility = base_params.max_portfolio_volatility * 1.1
                self.risk_params.max_single_position = base_params.max_single_position * 1.1
                
            elif self.market_regime == MarketRegime.BEAR_MARKET:
                self.risk_params.max_portfolio_volatility = base_params.max_portfolio_volatility * 0.9
                self.risk_params.max_drawdown = base_params.max_drawdown * 0.8
                
        except Exception as e:
            logger.error(f"Error adjusting risk parameters: {e}")
    
    def generate_risk_report(self, portfolio: Dict[str, float],
                           market_data: Dict[str, pd.DataFrame],
                           benchmark_returns: Optional[pd.Series] = None) -> Dict[str, Any]:
        """Generate comprehensive risk report"""
        try:
            # Calculate risk metrics
            risk_metrics = self.assess_portfolio_risk(portfolio, market_data, benchmark_returns)
            
            # Check risk limits
            risk_limits = self.check_risk_limits(portfolio, market_data)
            
            # Get suggestions if needed
            suggestions = []
            if risk_limits["overall_status"] != "OK":
                suggestions = self.suggest_risk_adjustments(portfolio, market_data, risk_limits)
            
            # Portfolio composition analysis
            total_value = sum(portfolio.values())
            kospi_exposure = 0.0
            kosdaq_exposure = 0.0
            
            for symbol, value in portfolio.items():
                market_type = self._determine_market_type(symbol)
                weight = value / total_value if total_value > 0 else 0
                if market_type == "KOSPI":
                    kospi_exposure += weight
                else:
                    kosdaq_exposure += weight
            
            return {
                "timestamp": datetime.now().isoformat(),
                "market_regime": self.market_regime.value,
                "portfolio_summary": {
                    "total_value": total_value,
                    "number_of_positions": len(portfolio),
                    "kospi_exposure": kospi_exposure,
                    "kosdaq_exposure": kosdaq_exposure
                },
                "risk_metrics": {
                    "portfolio_var": risk_metrics.portfolio_var,
                    "portfolio_cvar": risk_metrics.portfolio_cvar,
                    "volatility": risk_metrics.volatility,
                    "beta": risk_metrics.beta,
                    "tracking_error": risk_metrics.tracking_error,
                    "max_drawdown": risk_metrics.max_drawdown,
                    "korean_risk_score": risk_metrics.korean_risk_score
                },
                "risk_limits": risk_limits,
                "suggestions": suggestions,
                "overall_risk_level": self._determine_overall_risk_level(risk_metrics, risk_limits)
            }
            
        except Exception as e:
            logger.error(f"Error generating risk report: {e}")
            return {"error": str(e)}
    
    def _determine_overall_risk_level(self, risk_metrics: RiskMetrics,
                                    risk_limits: Dict[str, Any]) -> str:
        """Determine overall portfolio risk level"""
        try:
            risk_score = 0
            
            # Add points based on violations
            violations = risk_limits.get("violations", [])
            warnings = risk_limits.get("warnings", [])
            
            risk_score += len(violations) * 3
            risk_score += len(warnings) * 1
            
            # Add points based on metrics
            if risk_metrics.volatility > 0.25:
                risk_score += 2
            elif risk_metrics.volatility > 0.20:
                risk_score += 1
                
            if risk_metrics.korean_risk_score > 0.7:
                risk_score += 2
            elif risk_metrics.korean_risk_score > 0.5:
                risk_score += 1
                
            if risk_metrics.max_drawdown > 0.20:
                risk_score += 2
            elif risk_metrics.max_drawdown > 0.15:
                risk_score += 1
            
            # Determine risk level
            if risk_score >= 8:
                return RiskLevel.VERY_HIGH.value
            elif risk_score >= 6:
                return RiskLevel.HIGH.value  
            elif risk_score >= 4:
                return RiskLevel.MEDIUM.value
            elif risk_score >= 2:
                return RiskLevel.LOW.value
            else:
                return RiskLevel.VERY_LOW.value
                
        except Exception as e:
            logger.error(f"Error determining risk level: {e}")
            return RiskLevel.MEDIUM.value