"""
Korean Strategy Validation Framework

Comprehensive validation system for trading strategies against Korean market benchmarks,
historical performance, and market-specific characteristics.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, date, timedelta
import logging
from dataclasses import dataclass
from enum import Enum
import warnings
from scipy import stats
from sklearn.metrics import mean_squared_error
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class ValidationResult(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"

class BenchmarkType(Enum):
    KOSPI = "kospi"
    KOSDAQ = "kosdaq"
    KOREAN_BOND = "korean_bond"
    SECTOR_ETF = "sector_etf"
    CUSTOM = "custom"

@dataclass
class ValidationMetrics:
    """Container for strategy validation metrics"""
    # Return metrics
    total_return: float = 0.0
    annual_return: float = 0.0
    excess_return: float = 0.0
    
    # Risk metrics
    volatility: float = 0.0
    max_drawdown: float = 0.0
    var_95: float = 0.0
    
    # Risk-adjusted metrics
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    information_ratio: float = 0.0
    
    # Korean market specific
    korean_alpha: float = 0.0
    korean_beta: float = 1.0
    downside_capture: float = 1.0
    upside_capture: float = 1.0
    
    # Trading metrics
    win_rate: float = 0.0
    profit_factor: float = 1.0
    avg_holding_period: float = 0.0
    turnover_rate: float = 0.0
    
    # Consistency metrics
    consistency_score: float = 0.0
    stability_score: float = 0.0
    market_timing_score: float = 0.0

@dataclass
class KoreanBenchmarks:
    """Korean market benchmark data"""
    kospi_returns: pd.Series = None
    kosdaq_returns: pd.Series = None  
    korean_bond_returns: pd.Series = None
    risk_free_rate: float = 0.032  # Korean 3-year treasury
    
    # Market crisis periods for stress testing
    crisis_periods: List[Tuple[str, str]] = None
    
    def __post_init__(self):
        if self.crisis_periods is None:
            self.crisis_periods = [
                ("1997-10-01", "1998-06-30"),  # Asian Financial Crisis
                ("2008-09-01", "2009-03-31"),  # Global Financial Crisis  
                ("2020-02-01", "2020-04-30"),  # COVID-19 Crisis
                ("2022-01-01", "2022-06-30")   # Interest Rate Hikes
            ]

class KoreanStrategyValidator:
    """Comprehensive strategy validation system for Korean markets"""
    
    def __init__(self, benchmarks: Optional[KoreanBenchmarks] = None):
        self.benchmarks = benchmarks or KoreanBenchmarks()
        
        # Korean market characteristics for validation
        self.korean_market_params = {
            "kospi_avg_return": 0.08,  # Historical 8% annual return
            "kosdaq_avg_return": 0.12,  # Historical 12% annual return  
            "kospi_volatility": 0.18,  # 18% annual volatility
            "kosdaq_volatility": 0.28,  # 28% annual volatility
            "correlation_kospi_kosdaq": 0.75,  # 75% correlation
            "max_acceptable_drawdown": 0.25,  # 25% max drawdown
            "min_sharpe_ratio": 0.5,  # Minimum acceptable Sharpe ratio
            "target_win_rate": 0.55,  # Target 55% win rate
        }
        
        # Sector performance benchmarks (simplified)
        self.sector_benchmarks = {
            "technology": 0.15,  # 15% annual return
            "finance": 0.06,     # 6% annual return
            "automotive": 0.10,  # 10% annual return
            "steel": 0.08,       # 8% annual return  
            "bio": 0.20,         # 20% annual return (high volatility)
            "retail": 0.09       # 9% annual return
        }
    
    def validate_strategy(self, strategy_returns: pd.Series,
                         trades: Optional[pd.DataFrame] = None,
                         benchmark_type: BenchmarkType = BenchmarkType.KOSPI,
                         custom_benchmark: Optional[pd.Series] = None) -> Dict[str, Any]:
        """Comprehensive strategy validation"""
        try:
            if len(strategy_returns) == 0:
                return {"error": "No returns data provided"}
            
            # Get appropriate benchmark
            benchmark_returns = self._get_benchmark_returns(benchmark_type, custom_benchmark)
            
            if benchmark_returns is None:
                logger.warning("No benchmark available, using risk-free rate")
                benchmark_returns = pd.Series(
                    [self.benchmarks.risk_free_rate / 252] * len(strategy_returns),
                    index=strategy_returns.index
                )
            
            # Calculate validation metrics
            metrics = self._calculate_validation_metrics(
                strategy_returns, benchmark_returns, trades
            )
            
            # Perform Korean market specific tests
            korean_tests = self._perform_korean_market_tests(
                strategy_returns, benchmark_returns, trades
            )
            
            # Crisis period analysis
            crisis_analysis = self._analyze_crisis_performance(
                strategy_returns, benchmark_returns
            )
            
            # Generate overall assessment
            overall_assessment = self._generate_overall_assessment(
                metrics, korean_tests, crisis_analysis
            )
            
            # Performance attribution
            attribution = self._calculate_performance_attribution(
                strategy_returns, benchmark_returns
            )
            
            return {
                "validation_timestamp": datetime.now().isoformat(),
                "strategy_period": {
                    "start_date": strategy_returns.index[0].strftime('%Y-%m-%d'),
                    "end_date": strategy_returns.index[-1].strftime('%Y-%m-%d'),
                    "total_days": len(strategy_returns)
                },
                "benchmark_type": benchmark_type.value,
                "metrics": self._metrics_to_dict(metrics),
                "korean_market_tests": korean_tests,
                "crisis_analysis": crisis_analysis,
                "performance_attribution": attribution,
                "overall_assessment": overall_assessment
            }
            
        except Exception as e:
            logger.error(f"Error validating strategy: {e}")
            return {"error": str(e)}
    
    def _get_benchmark_returns(self, benchmark_type: BenchmarkType,
                             custom_benchmark: Optional[pd.Series] = None) -> Optional[pd.Series]:
        """Get benchmark returns based on type"""
        try:
            if benchmark_type == BenchmarkType.CUSTOM and custom_benchmark is not None:
                return custom_benchmark
            elif benchmark_type == BenchmarkType.KOSPI:
                return self.benchmarks.kospi_returns
            elif benchmark_type == BenchmarkType.KOSDAQ:
                return self.benchmarks.kosdaq_returns
            elif benchmark_type == BenchmarkType.KOREAN_BOND:
                return self.benchmarks.korean_bond_returns
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting benchmark returns: {e}")
            return None
    
    def _calculate_validation_metrics(self, strategy_returns: pd.Series,
                                    benchmark_returns: pd.Series,
                                    trades: Optional[pd.DataFrame] = None) -> ValidationMetrics:
        """Calculate comprehensive validation metrics"""
        try:
            metrics = ValidationMetrics()
            
            # Align returns
            common_dates = strategy_returns.index.intersection(benchmark_returns.index)
            if len(common_dates) == 0:
                logger.warning("No common dates between strategy and benchmark")
                return metrics
            
            aligned_strategy = strategy_returns.loc[common_dates]
            aligned_benchmark = benchmark_returns.loc[common_dates]
            
            # Basic return metrics
            metrics.total_return = (1 + aligned_strategy).prod() - 1
            days = len(aligned_strategy)
            metrics.annual_return = (1 + metrics.total_return) ** (252 / days) - 1
            
            benchmark_total_return = (1 + aligned_benchmark).prod() - 1
            benchmark_annual_return = (1 + benchmark_total_return) ** (252 / days) - 1
            metrics.excess_return = metrics.annual_return - benchmark_annual_return
            
            # Risk metrics
            metrics.volatility = aligned_strategy.std() * np.sqrt(252)
            
            # Maximum drawdown
            cumulative = (1 + aligned_strategy).cumprod()
            rolling_max = cumulative.expanding().max()
            drawdown = (cumulative - rolling_max) / rolling_max
            metrics.max_drawdown = drawdown.min()
            
            # Value at Risk (95% confidence)
            metrics.var_95 = np.percentile(aligned_strategy, 5)
            
            # Risk-adjusted metrics
            excess_returns = aligned_strategy - self.benchmarks.risk_free_rate / 252
            if metrics.volatility > 0:
                metrics.sharpe_ratio = excess_returns.mean() / aligned_strategy.std() * np.sqrt(252)
            
            # Sortino ratio
            downside_returns = aligned_strategy[aligned_strategy < 0]
            if len(downside_returns) > 0:
                downside_std = downside_returns.std() * np.sqrt(252)
                if downside_std > 0:
                    metrics.sortino_ratio = excess_returns.mean() / downside_returns.std() * np.sqrt(252)
            
            # Calmar ratio
            if metrics.max_drawdown < 0:
                metrics.calmar_ratio = metrics.annual_return / abs(metrics.max_drawdown)
            
            # Information ratio
            active_returns = aligned_strategy - aligned_benchmark
            tracking_error = active_returns.std() * np.sqrt(252)
            if tracking_error > 0:
                metrics.information_ratio = active_returns.mean() / active_returns.std() * np.sqrt(252)
            
            # Korean market specific metrics
            if len(aligned_benchmark) > 1:
                covariance = np.cov(aligned_strategy, aligned_benchmark)[0, 1]
                benchmark_variance = aligned_benchmark.var()
                if benchmark_variance > 0:
                    metrics.korean_beta = covariance / benchmark_variance
                
                # Alpha calculation
                expected_return = self.benchmarks.risk_free_rate / 252 + \
                                metrics.korean_beta * (aligned_benchmark.mean() - self.benchmarks.risk_free_rate / 252)
                metrics.korean_alpha = aligned_strategy.mean() - expected_return
            
            # Upside/Downside capture
            up_benchmark = aligned_benchmark[aligned_benchmark > 0]
            up_strategy = aligned_strategy[aligned_benchmark > 0]
            if len(up_benchmark) > 0:
                metrics.upside_capture = up_strategy.mean() / up_benchmark.mean()
            
            down_benchmark = aligned_benchmark[aligned_benchmark < 0]
            down_strategy = aligned_strategy[aligned_benchmark < 0]
            if len(down_benchmark) > 0:
                metrics.downside_capture = abs(down_strategy.mean()) / abs(down_benchmark.mean())
            
            # Trading metrics (if trades data available)
            if trades is not None and len(trades) > 0:
                metrics = self._calculate_trading_metrics(metrics, trades, aligned_strategy)
            
            # Consistency and stability scores
            metrics.consistency_score = self._calculate_consistency_score(aligned_strategy)
            metrics.stability_score = self._calculate_stability_score(aligned_strategy)
            metrics.market_timing_score = self._calculate_market_timing_score(
                aligned_strategy, aligned_benchmark
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating validation metrics: {e}")
            return ValidationMetrics()
    
    def _calculate_trading_metrics(self, metrics: ValidationMetrics,
                                 trades: pd.DataFrame,
                                 strategy_returns: pd.Series) -> ValidationMetrics:
        """Calculate trading-specific metrics"""
        try:
            if 'pnl' in trades.columns:
                winning_trades = trades[trades['pnl'] > 0]
                losing_trades = trades[trades['pnl'] < 0]
                
                metrics.win_rate = len(winning_trades) / len(trades)
                
                if len(losing_trades) > 0:
                    gross_profit = winning_trades['pnl'].sum()
                    gross_loss = abs(losing_trades['pnl'].sum())
                    metrics.profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
            
            # Estimate holding period from trades
            if 'entry_date' in trades.columns and 'exit_date' in trades.columns:
                holding_periods = []
                for _, trade in trades.iterrows():
                    if pd.notna(trade['entry_date']) and pd.notna(trade['exit_date']):
                        entry = pd.to_datetime(trade['entry_date'])
                        exit_date = pd.to_datetime(trade['exit_date'])
                        holding_period = (exit_date - entry).days
                        holding_periods.append(holding_period)
                
                if holding_periods:
                    metrics.avg_holding_period = np.mean(holding_periods)
            
            # Estimate turnover rate
            if len(trades) > 0 and len(strategy_returns) > 0:
                annual_trades = len(trades) * (252 / len(strategy_returns))
                metrics.turnover_rate = annual_trades
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating trading metrics: {e}")
            return metrics
    
    def _calculate_consistency_score(self, returns: pd.Series) -> float:
        """Calculate consistency score (0-1)"""
        try:
            if len(returns) < 12:
                return 0.5
            
            # Calculate monthly returns
            monthly_returns = returns.resample('M').apply(lambda x: (1 + x).prod() - 1)
            
            if len(monthly_returns) < 3:
                return 0.5
            
            # Consistency based on percentage of positive months
            positive_months = len(monthly_returns[monthly_returns > 0])
            consistency = positive_months / len(monthly_returns)
            
            # Adjust for volatility of monthly returns
            monthly_volatility = monthly_returns.std()
            volatility_penalty = min(monthly_volatility * 2, 0.3)  # Cap penalty at 0.3
            
            final_score = max(0, consistency - volatility_penalty)
            return min(final_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating consistency score: {e}")
            return 0.5
    
    def _calculate_stability_score(self, returns: pd.Series) -> float:
        """Calculate stability score based on rolling performance"""
        try:
            if len(returns) < 60:  # Need at least 60 days
                return 0.5
            
            # Calculate rolling 30-day returns
            rolling_returns = returns.rolling(window=30).apply(lambda x: (1 + x).prod() - 1)
            rolling_returns = rolling_returns.dropna()
            
            if len(rolling_returns) < 10:
                return 0.5
            
            # Stability based on consistency of rolling returns
            positive_periods = len(rolling_returns[rolling_returns > 0])
            stability_base = positive_periods / len(rolling_returns)
            
            # Penalize for high volatility of rolling returns
            rolling_volatility = rolling_returns.std()
            volatility_penalty = min(rolling_volatility * 3, 0.4)
            
            stability_score = max(0, stability_base - volatility_penalty)
            return min(stability_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating stability score: {e}")
            return 0.5
    
    def _calculate_market_timing_score(self, strategy_returns: pd.Series,
                                     benchmark_returns: pd.Series) -> float:
        """Calculate market timing ability score"""
        try:
            if len(strategy_returns) < 30:
                return 0.5
            
            # Calculate correlation between strategy returns and lagged benchmark returns
            # Good market timing should show positive correlation with future benchmark moves
            
            # Align returns
            common_dates = strategy_returns.index.intersection(benchmark_returns.index)
            aligned_strategy = strategy_returns.loc[common_dates]
            aligned_benchmark = benchmark_returns.loc[common_dates]
            
            if len(aligned_strategy) < 30:
                return 0.5
            
            # Calculate timing score based on performance in up vs down markets
            up_market_days = aligned_benchmark > 0
            down_market_days = aligned_benchmark < 0
            
            if sum(up_market_days) == 0 or sum(down_market_days) == 0:
                return 0.5
            
            up_market_strategy = aligned_strategy[up_market_days].mean()
            down_market_strategy = aligned_strategy[down_market_days].mean()
            up_market_benchmark = aligned_benchmark[up_market_days].mean()
            down_market_benchmark = aligned_benchmark[down_market_days].mean()
            
            # Good timing: outperform in up markets, lose less in down markets
            up_market_ratio = up_market_strategy / up_market_benchmark if up_market_benchmark > 0 else 1
            down_market_ratio = abs(down_market_strategy) / abs(down_market_benchmark) if down_market_benchmark < 0 else 1
            
            # Score based on upside capture > 1 and downside capture < 1
            timing_score = (up_market_ratio + (2 - down_market_ratio)) / 3
            
            return max(0, min(timing_score, 1.0))
            
        except Exception as e:
            logger.error(f"Error calculating market timing score: {e}")
            return 0.5
    
    def _perform_korean_market_tests(self, strategy_returns: pd.Series,
                                   benchmark_returns: pd.Series,
                                   trades: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """Perform Korean market-specific validation tests"""
        try:
            tests = {}
            
            # Test 1: Performance vs Korean market characteristics
            annual_return = (1 + strategy_returns).prod() ** (252 / len(strategy_returns)) - 1
            volatility = strategy_returns.std() * np.sqrt(252)
            
            # Compare against Korean market norms
            market_type = "kosdaq" if annual_return > 0.15 else "kospi"
            expected_vol = self.korean_market_params[f"{market_type}_volatility"]
            expected_return = self.korean_market_params[f"{market_type}_avg_return"]
            
            tests["market_characteristics"] = {
                "inferred_market_type": market_type,
                "return_vs_market": annual_return / expected_return if expected_return > 0 else 1,  
                "volatility_vs_market": volatility / expected_vol if expected_vol > 0 else 1,
                "risk_adjusted_performance": (annual_return / volatility) / (expected_return / expected_vol) if expected_vol > 0 and volatility > 0 else 1,
                "pass": abs(volatility - expected_vol) < expected_vol * 0.5  # Within 50% of expected
            }
            
            # Test 2: Drawdown analysis
            cumulative = (1 + strategy_returns).cumprod()
            rolling_max = cumulative.expanding().max()
            drawdown = (cumulative - rolling_max) / rolling_max
            max_drawdown = abs(drawdown.min())
            
            tests["drawdown_analysis"] = {
                "max_drawdown": max_drawdown,
                "acceptable_drawdown": max_drawdown <= self.korean_market_params["max_acceptable_drawdown"],
                "drawdown_duration": self._calculate_max_drawdown_duration(drawdown),
                "recovery_factor": annual_return / max_drawdown if max_drawdown > 0 else 0,
                "pass": max_drawdown <= self.korean_market_params["max_acceptable_drawdown"]
            }
            
            # Test 3: Risk-adjusted returns
            risk_free_rate = self.benchmarks.risk_free_rate
            excess_returns = strategy_returns - risk_free_rate / 252
            sharpe_ratio = excess_returns.mean() / strategy_returns.std() * np.sqrt(252) if strategy_returns.std() > 0 else 0
            
            tests["risk_adjusted_returns"] = {
                "sharpe_ratio": sharpe_ratio,
                "min_acceptable_sharpe": self.korean_market_params["min_sharpe_ratio"],
                "sharpe_vs_market": sharpe_ratio / (expected_return / expected_vol) if expected_vol > 0 else 0,
                "pass": sharpe_ratio >= self.korean_market_params["min_sharpe_ratio"]
            }
            
            # Test 4: Consistency test
            monthly_returns = strategy_returns.resample('M').apply(lambda x: (1 + x).prod() - 1)
            positive_months = len(monthly_returns[monthly_returns > 0])
            win_rate_monthly = positive_months / len(monthly_returns) if len(monthly_returns) > 0 else 0
            
            tests["consistency_test"] = {
                "monthly_win_rate": win_rate_monthly,
                "target_win_rate": self.korean_market_params["target_win_rate"],
                "months_analyzed": len(monthly_returns),
                "pass": win_rate_monthly >= 0.45  # At least 45% positive months
            }
            
            # Test 5: Korean market correlation test
            if len(benchmark_returns) > 30:
                correlation = strategy_returns.corr(benchmark_returns)
                tests["market_correlation"] = {
                    "correlation_with_benchmark": correlation,
                    "appropriate_correlation": 0.3 <= abs(correlation) <= 0.8,  # Not too high, not too low
                    "pass": 0.3 <= abs(correlation) <= 0.8
                }
            
            # Overall Korean market test score
            passed_tests = sum(1 for test in tests.values() if test.get("pass", False))
            total_tests = len(tests)
            tests["overall_korean_score"] = passed_tests / total_tests if total_tests > 0 else 0
            
            return tests
            
        except Exception as e:
            logger.error(f"Error performing Korean market tests: {e}")
            return {"error": str(e)}
    
    def _calculate_max_drawdown_duration(self, drawdown_series: pd.Series) -> int:
        """Calculate maximum drawdown duration in days"""
        try:
            underwater = drawdown_series < 0
            if not underwater.any():
                return 0
            
            # Find continuous underwater periods
            underwater_periods = []
            start = None
            
            for i, is_underwater in enumerate(underwater):
                if is_underwater and start is None:
                    start = i
                elif not is_underwater and start is not None:
                    underwater_periods.append(i - start)
                    start = None
            
            # Handle case where drawdown continues to the end
            if start is not None:
                underwater_periods.append(len(underwater) - start)
            
            return max(underwater_periods) if underwater_periods else 0
            
        except Exception as e:
            logger.error(f"Error calculating drawdown duration: {e}")
            return 0
    
    def _analyze_crisis_performance(self, strategy_returns: pd.Series,
                                  benchmark_returns: pd.Series) -> Dict[str, Any]:
        """Analyze strategy performance during Korean market crisis periods"""
        try:
            crisis_analysis = {}
            
            for crisis_name, (start_date, end_date) in [
                ("Asian_Financial_Crisis", ("1997-10-01", "1998-06-30")),
                ("Global_Financial_Crisis", ("2008-09-01", "2009-03-31")),
                ("COVID_Crisis", ("2020-02-01", "2020-04-30")),
                ("Interest_Rate_Hikes", ("2022-01-01", "2022-06-30"))
            ]:
                try:
                    crisis_start = pd.to_datetime(start_date)
                    crisis_end = pd.to_datetime(end_date)
                    
                    # Check if strategy period overlaps with crisis
                    strategy_start = strategy_returns.index[0]
                    strategy_end = strategy_returns.index[-1]
                    
                    if strategy_end < crisis_start or strategy_start > crisis_end:
                        continue  # No overlap
                    
                    # Get overlapping period
                    overlap_start = max(crisis_start, strategy_start)
                    overlap_end = min(crisis_end, strategy_end)
                    
                    crisis_strategy = strategy_returns[overlap_start:overlap_end]
                    crisis_benchmark = benchmark_returns[overlap_start:overlap_end]
                    
                    if len(crisis_strategy) < 5:  # Need at least 5 days of data
                        continue
                    
                    # Calculate crisis performance metrics
                    strategy_crisis_return = (1 + crisis_strategy).prod() - 1
                    benchmark_crisis_return = (1 + crisis_benchmark).prod() - 1
                    
                    crisis_alpha = strategy_crisis_return - benchmark_crisis_return
                    crisis_volatility = crisis_strategy.std() * np.sqrt(252)
                    
                    # Maximum drawdown during crisis
                    crisis_cumulative = (1 + crisis_strategy).cumprod()
                    crisis_rolling_max = crisis_cumulative.expanding().max()
                    crisis_drawdown = (crisis_cumulative - crisis_rolling_max) / crisis_rolling_max
                    crisis_max_dd = crisis_drawdown.min()
                    
                    crisis_analysis[crisis_name] = {
                        "period": f"{overlap_start.strftime('%Y-%m-%d')} to {overlap_end.strftime('%Y-%m-%d')}",
                        "days_analyzed": len(crisis_strategy),
                        "strategy_return": strategy_crisis_return,
                        "benchmark_return": benchmark_crisis_return,
                        "alpha": crisis_alpha,
                        "volatility": crisis_volatility,
                        "max_drawdown": crisis_max_dd,
                        "outperformed_benchmark": strategy_crisis_return > benchmark_crisis_return,
                        "downside_protection": abs(crisis_max_dd) < abs(benchmark_crisis_return) if benchmark_crisis_return < 0 else True
                    }
                    
                except Exception as e:
                    logger.debug(f"Could not analyze {crisis_name}: {e}")
                    continue
            
            # Overall crisis performance score
            if crisis_analysis:
                outperformance_count = sum(1 for analysis in crisis_analysis.values() 
                                         if analysis.get("outperformed_benchmark", False))
                protection_count = sum(1 for analysis in crisis_analysis.values()
                                     if analysis.get("downside_protection", False))
                
                crisis_analysis["overall_crisis_score"] = {
                    "crises_analyzed": len(crisis_analysis) - 1,  # Subtract 1 for this summary
                    "outperformance_rate": outperformance_count / len(crisis_analysis) if crisis_analysis else 0,
                    "protection_rate": protection_count / len(crisis_analysis) if crisis_analysis else 0,
                    "overall_rating": "excellent" if (outperformance_count + protection_count) >= len(crisis_analysis) * 1.5 else
                                    "good" if (outperformance_count + protection_count) >= len(crisis_analysis) else
                                    "acceptable" if protection_count >= len(crisis_analysis) * 0.5 else "poor"
                }
            
            return crisis_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing crisis performance: {e}")
            return {"error": str(e)}
    
    def _calculate_performance_attribution(self, strategy_returns: pd.Series,
                                         benchmark_returns: pd.Series) -> Dict[str, Any]:
        """Calculate performance attribution analysis"""
        try:
            if len(strategy_returns) < 30 or len(benchmark_returns) < 30:
                return {"error": "Insufficient data for attribution analysis"}
            
            # Align returns
            common_dates = strategy_returns.index.intersection(benchmark_returns.index)
            aligned_strategy = strategy_returns.loc[common_dates]
            aligned_benchmark = benchmark_returns.loc[common_dates]
            
            if len(aligned_strategy) < 30:
                return {"error": "Insufficient overlapping data"}
            
            # Total return decomposition
            strategy_total = (1 + aligned_strategy).prod() - 1
            benchmark_total = (1 + aligned_benchmark).prod() - 1
            total_alpha = strategy_total - benchmark_total
            
            # Beta calculation
            covariance = np.cov(aligned_strategy, aligned_benchmark)[0, 1]
            benchmark_variance = aligned_benchmark.var()
            beta = covariance / benchmark_variance if benchmark_variance > 0 else 1.0
            
            # Jensen's Alpha
            risk_free_rate = self.benchmarks.risk_free_rate
            expected_return = risk_free_rate / 252 + beta * (aligned_benchmark.mean() - risk_free_rate / 252)
            jensen_alpha = aligned_strategy.mean() - expected_return
            
            # Market timing vs security selection
            # Simplified attribution - in practice would be more complex
            market_return_contribution = beta * benchmark_total
            selection_contribution = total_alpha - (beta - 1) * benchmark_total
            
            # Timing contribution (simplified)
            timing_contribution = total_alpha - selection_contribution
            
            return {
                "total_return": strategy_total,
                "benchmark_return": benchmark_total,
                "total_alpha": total_alpha,
                "beta": beta,
                "jensen_alpha": jensen_alpha * 252,  # Annualized
                "attribution": {
                    "market_return": market_return_contribution,
                    "security_selection": selection_contribution,
                    "market_timing": timing_contribution,
                    "interaction_effect": total_alpha - selection_contribution - timing_contribution
                },
                "risk_decomposition": {
                    "systematic_risk": beta**2 * aligned_benchmark.var() * 252,
                    "idiosyncratic_risk": (aligned_strategy.var() - beta**2 * aligned_benchmark.var()) * 252,
                    "total_risk": aligned_strategy.var() * 252
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance attribution: {e}")
            return {"error": str(e)}
    
    def _generate_overall_assessment(self, metrics: ValidationMetrics,
                                   korean_tests: Dict[str, Any],
                                   crisis_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall strategy assessment"""
        try:
            assessment_score = 0.0
            assessment_factors = []
            
            # Return performance (25% weight)
            if metrics.annual_return > 0.15:
                return_score = 1.0
            elif metrics.annual_return > 0.10:
                return_score = 0.8
            elif metrics.annual_return > 0.05:
                return_score = 0.6
            elif metrics.annual_return > 0:
                return_score = 0.4
            else:
                return_score = 0.0
            
            assessment_score += return_score * 0.25
            assessment_factors.append(f"Annual Return: {metrics.annual_return:.1%} (Score: {return_score:.1f})")
            
            # Risk-adjusted performance (25% weight)  
            if metrics.sharpe_ratio > 1.5:
                sharpe_score = 1.0
            elif metrics.sharpe_ratio > 1.0:
                sharpe_score = 0.8
            elif metrics.sharpe_ratio > 0.5:
                sharpe_score = 0.6
            elif metrics.sharpe_ratio > 0:
                sharpe_score = 0.4
            else:
                sharpe_score = 0.0
                
            assessment_score += sharpe_score * 0.25
            assessment_factors.append(f"Sharpe Ratio: {metrics.sharpe_ratio:.2f} (Score: {sharpe_score:.1f})")
            
            # Risk control (20% weight)
            max_dd_score = 1.0 if abs(metrics.max_drawdown) < 0.10 else \
                          0.8 if abs(metrics.max_drawdown) < 0.15 else \
                          0.6 if abs(metrics.max_drawdown) < 0.20 else \
                          0.4 if abs(metrics.max_drawdown) < 0.25 else 0.0
            
            assessment_score += max_dd_score * 0.20
            assessment_factors.append(f"Max Drawdown: {metrics.max_drawdown:.1%} (Score: {max_dd_score:.1f})")
            
            # Korean market tests (20% weight)
            korean_score = korean_tests.get("overall_korean_score", 0.5)
            assessment_score += korean_score * 0.20
            assessment_factors.append(f"Korean Market Tests: {korean_score:.1%} passed (Score: {korean_score:.1f})")
            
            # Crisis performance (10% weight)  
            crisis_overall = crisis_analysis.get("overall_crisis_score", {})
            crisis_rating = crisis_overall.get("overall_rating", "acceptable")
            crisis_score = {"excellent": 1.0, "good": 0.8, "acceptable": 0.6, "poor": 0.4}.get(crisis_rating, 0.4)
            
            assessment_score += crisis_score * 0.10
            assessment_factors.append(f"Crisis Performance: {crisis_rating} (Score: {crisis_score:.1f})")
            
            # Overall rating
            if assessment_score >= 0.9:
                overall_rating = ValidationResult.EXCELLENT
            elif assessment_score >= 0.75:
                overall_rating = ValidationResult.GOOD
            elif assessment_score >= 0.60:
                overall_rating = ValidationResult.ACCEPTABLE
            elif assessment_score >= 0.40:
                overall_rating = ValidationResult.POOR
            else:
                overall_rating = ValidationResult.UNACCEPTABLE
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                metrics, korean_tests, crisis_analysis, assessment_score
            )
            
            return {
                "overall_score": assessment_score,
                "overall_rating": overall_rating.value,
                "score_breakdown": assessment_factors,
                "key_strengths": self._identify_strengths(metrics, korean_tests),
                "key_weaknesses": self._identify_weaknesses(metrics, korean_tests),
                "recommendations": recommendations,
                "investment_suitability": self._assess_investment_suitability(overall_rating, metrics)
            }
            
        except Exception as e:
            logger.error(f"Error generating overall assessment: {e}")
            return {"error": str(e)}
    
    def _identify_strengths(self, metrics: ValidationMetrics,
                          korean_tests: Dict[str, Any]) -> List[str]:
        """Identify strategy strengths"""
        strengths = []
        
        if metrics.annual_return > 0.12:
            strengths.append(f"Strong annual return of {metrics.annual_return:.1%}")
        
        if metrics.sharpe_ratio > 1.0:
            strengths.append(f"Excellent risk-adjusted returns (Sharpe: {metrics.sharpe_ratio:.2f})")
        
        if abs(metrics.max_drawdown) < 0.15:
            strengths.append(f"Good downside protection (Max DD: {metrics.max_drawdown:.1%})")
        
        if metrics.win_rate > 0.60:
            strengths.append(f"High win rate of {metrics.win_rate:.1%}")
        
        if metrics.consistency_score > 0.7:
            strengths.append("Consistent performance across different periods")
        
        if korean_tests.get("overall_korean_score", 0) > 0.75:
            strengths.append("Well-adapted to Korean market characteristics")
        
        return strengths
    
    def _identify_weaknesses(self, metrics: ValidationMetrics,
                           korean_tests: Dict[str, Any]) -> List[str]:
        """Identify strategy weaknesses"""
        weaknesses = []
        
        if metrics.annual_return < 0.05:
            weaknesses.append(f"Low annual return of {metrics.annual_return:.1%}")
        
        if metrics.sharpe_ratio < 0.5:
            weaknesses.append(f"Poor risk-adjusted returns (Sharpe: {metrics.sharpe_ratio:.2f})")
        
        if abs(metrics.max_drawdown) > 0.20:
            weaknesses.append(f"High maximum drawdown of {metrics.max_drawdown:.1%}")
        
        if metrics.volatility > 0.25:
            weaknesses.append(f"High volatility of {metrics.volatility:.1%}")
        
        if metrics.win_rate < 0.45:
            weaknesses.append(f"Low win rate of {metrics.win_rate:.1%}")
        
        if metrics.consistency_score < 0.4:
            weaknesses.append("Inconsistent performance across periods")
        
        if korean_tests.get("overall_korean_score", 1) < 0.5:
            weaknesses.append("Poor adaptation to Korean market characteristics")
        
        return weaknesses
    
    def _generate_recommendations(self, metrics: ValidationMetrics,
                                korean_tests: Dict[str, Any],
                                crisis_analysis: Dict[str, Any],
                                overall_score: float) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        if abs(metrics.max_drawdown) > 0.15:
            recommendations.append("Implement stronger risk management and position sizing controls")
        
        if metrics.sharpe_ratio < 0.8:
            recommendations.append("Focus on improving risk-adjusted returns through better entry/exit timing")
        
        if metrics.consistency_score < 0.6:
            recommendations.append("Work on strategy consistency by refining signal generation")
        
        if korean_tests.get("market_characteristics", {}).get("pass", True) == False:
            recommendations.append("Adjust strategy parameters to better fit Korean market volatility patterns")
        
        if metrics.win_rate < 0.50:
            recommendations.append("Improve signal quality to increase win rate")
        
        if overall_score < 0.7:
            recommendations.append("Consider combining with other strategies or market timing overlay")
        
        # Crisis-specific recommendations
        crisis_overall = crisis_analysis.get("overall_crisis_score", {})
        if crisis_overall.get("protection_rate", 1) < 0.5:
            recommendations.append("Add defensive measures for crisis periods (cash allocation, hedging)")
        
        return recommendations
    
    def _assess_investment_suitability(self, rating: ValidationResult,
                                     metrics: ValidationMetrics) -> Dict[str, str]:
        """Assess investment suitability for different investor types"""
        suitability = {}
        
        # Conservative investors
        if rating in [ValidationResult.EXCELLENT, ValidationResult.GOOD] and \
           abs(metrics.max_drawdown) < 0.15 and metrics.volatility < 0.20:
            suitability["conservative"] = "Suitable - Good risk-adjusted returns with controlled downside"
        else:
            suitability["conservative"] = "Not suitable - Too risky or insufficient returns"
        
        # Moderate investors  
        if rating in [ValidationResult.EXCELLENT, ValidationResult.GOOD, ValidationResult.ACCEPTABLE] and \
           metrics.sharpe_ratio > 0.5:
            suitability["moderate"] = "Suitable - Acceptable risk-return profile"
        else:
            suitability["moderate"] = "Not suitable - Poor risk-adjusted performance"
        
        # Aggressive investors
        if rating != ValidationResult.UNACCEPTABLE and metrics.annual_return > 0.08:
            suitability["aggressive"] = "Suitable - Potential for good returns"
        else:
            suitability["aggressive"] = "Not suitable - Insufficient return potential"
        
        return suitability
    
    def _metrics_to_dict(self, metrics: ValidationMetrics) -> Dict[str, float]:
        """Convert ValidationMetrics to dictionary"""
        return {
            "total_return": metrics.total_return,
            "annual_return": metrics.annual_return,
            "excess_return": metrics.excess_return,
            "volatility": metrics.volatility,
            "max_drawdown": metrics.max_drawdown,
            "var_95": metrics.var_95,
            "sharpe_ratio": metrics.sharpe_ratio,
            "sortino_ratio": metrics.sortino_ratio,
            "calmar_ratio": metrics.calmar_ratio,
            "information_ratio": metrics.information_ratio,
            "korean_alpha": metrics.korean_alpha,
            "korean_beta": metrics.korean_beta,
            "downside_capture": metrics.downside_capture,
            "upside_capture": metrics.upside_capture,
            "win_rate": metrics.win_rate,
            "profit_factor": metrics.profit_factor,
            "avg_holding_period": metrics.avg_holding_period,
            "turnover_rate": metrics.turnover_rate,
            "consistency_score": metrics.consistency_score,
            "stability_score": metrics.stability_score,
            "market_timing_score": metrics.market_timing_score
        }