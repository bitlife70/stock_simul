import asyncio
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import and_

from models.strategy import Strategy, Backtest, Trade, EquityCurve
from models.stock_data import StockData
from services.data_service import DataService
from utils.technical_indicators import TechnicalIndicatorCalculator

logger = logging.getLogger(__name__)

class BacktestService:
    def __init__(self, db: Session):
        self.db = db
        self.data_service = DataService(db)
        self.calculator = TechnicalIndicatorCalculator()
    
    async def run_backtest(self, backtest_id: str) -> None:
        """Run a complete backtest"""
        try:
            # Get backtest configuration
            backtest = self.db.query(Backtest).filter(Backtest.id == backtest_id).first()
            if not backtest:
                raise ValueError(f"Backtest {backtest_id} not found")
            
            strategy = self.db.query(Strategy).filter(Strategy.id == backtest.strategy_id).first()
            if not strategy:
                raise ValueError(f"Strategy {backtest.strategy_id} not found")
            
            # Update status
            backtest.status = "running"
            backtest.progress = 0.0
            self.db.commit()
            
            logger.info(f"Starting backtest {backtest_id} for strategy {strategy.name}")
            
            # Get stock universe
            universe = await self._get_stock_universe(strategy.universe)
            logger.info(f"Universe contains {len(universe)} stocks")
            
            # Initialize portfolio
            portfolio = Portfolio(
                initial_capital=backtest.initial_capital,
                max_positions=strategy.max_positions,
                commission=backtest.commission,
                slippage=backtest.slippage
            )
            
            # Get date range
            date_range = pd.date_range(
                start=backtest.start_date,
                end=backtest.end_date,
                freq='D'
            )
            
            total_days = len(date_range)
            equity_curve_data = []
            
            # Run backtest day by day
            for i, current_date in enumerate(date_range):
                try:
                    # Update progress
                    progress = i / total_days
                    backtest.progress = progress
                    if i % 10 == 0:  # Update every 10 days
                        self.db.commit()
                    
                    # Skip weekends (Korean market closed)
                    if current_date.weekday() >= 5:
                        continue
                    
                    # Get market data for current date
                    market_data = await self._get_market_data(universe, current_date.date())
                    if not market_data:
                        continue
                    
                    # Generate signals
                    signals = await self._generate_signals(strategy, market_data, current_date.date())
                    
                    # Execute trades
                    trades = portfolio.execute_signals(signals, current_date.date())
                    
                    # Save trades to database
                    for trade in trades:
                        db_trade = Trade(
                            backtest_id=backtest.id,
                            symbol=trade['symbol'],
                            side=trade['side'],
                            quantity=trade['quantity'],
                            price=trade['price'],
                            value=trade['value'],
                            commission=trade['commission'],
                            entry_date=trade['date'],
                            trade_reason=trade.get('reason', '')
                        )
                        self.db.add(db_trade)
                    
                    # Update portfolio value
                    portfolio.update_portfolio_value(market_data, current_date.date())
                    
                    # Record equity curve
                    equity_data = {
                        'backtest_id': backtest.id,
                        'date': current_date.date(),
                        'portfolio_value': portfolio.total_value,
                        'cash': portfolio.cash,
                        'positions_value': portfolio.positions_value,
                        'daily_return': portfolio.daily_return,
                        'cumulative_return': portfolio.cumulative_return,
                        'drawdown': portfolio.current_drawdown
                    }
                    equity_curve_data.append(equity_data)
                    
                except Exception as e:
                    logger.error(f"Error processing date {current_date}: {e}")
                    continue
            
            # Save equity curve data
            for equity_data in equity_curve_data:
                equity_curve = EquityCurve(**equity_data)
                self.db.add(equity_curve)
            
            # Calculate final metrics
            metrics = self._calculate_performance_metrics(portfolio, equity_curve_data)
            
            # Update backtest with results
            backtest.total_return = metrics['total_return']
            backtest.annual_return = metrics['annual_return']
            backtest.max_drawdown = metrics['max_drawdown']
            backtest.sharpe_ratio = metrics['sharpe_ratio']
            backtest.sortino_ratio = metrics['sortino_ratio']
            backtest.calmar_ratio = metrics['calmar_ratio']
            backtest.total_trades = metrics['total_trades']
            backtest.winning_trades = metrics['winning_trades']
            backtest.losing_trades = metrics['losing_trades']
            backtest.win_rate = metrics['win_rate']
            backtest.avg_win = metrics['avg_win']
            backtest.avg_loss = metrics['avg_loss']
            backtest.avg_holding_period = metrics['avg_holding_period']
            
            backtest.status = "completed"
            backtest.progress = 1.0
            backtest.completed_at = datetime.now()
            
            self.db.commit()
            logger.info(f"Backtest {backtest_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Backtest {backtest_id} failed: {e}")
            backtest.status = "failed"
            backtest.error_message = str(e)
            self.db.commit()
    
    async def _get_stock_universe(self, universe_config: Dict) -> List[str]:
        """Get list of stocks based on universe configuration"""
        try:
            market = universe_config.get('market', 'KOSPI')
            min_volume = universe_config.get('min_volume', 0)
            min_market_cap = universe_config.get('min_market_cap', 0)
            
            # Get stock list from data service
            stocks = await self.data_service.get_stock_list(market=market, limit=500)
            
            # Apply filters
            filtered_stocks = []
            for stock in stocks:
                # Basic filters - in production, would check volume and market cap
                if len(filtered_stocks) < 200:  # Limit for MVP
                    filtered_stocks.append(stock['symbol'])
            
            return filtered_stocks
            
        except Exception as e:
            logger.error(f"Error getting stock universe: {e}")
            return ['005930', '000660', '035420']  # Fallback to major stocks
    
    async def _get_market_data(self, universe: List[str], date: date) -> Dict[str, Dict]:
        """Get market data for all stocks in universe for a specific date"""
        market_data = {}
        
        for symbol in universe[:10]:  # Limit for MVP performance
            try:
                # Get price data (simplified - in production would use optimized queries)
                stock_data = self.db.query(StockData).filter(
                    and_(
                        StockData.symbol == symbol,
                        StockData.date <= date
                    )
                ).order_by(StockData.date.desc()).first()
                
                if stock_data:
                    market_data[symbol] = {
                        'date': stock_data.date.date(),
                        'open': stock_data.open_price,
                        'high': stock_data.high_price,
                        'low': stock_data.low_price,
                        'close': stock_data.close_price,
                        'volume': stock_data.volume
                    }
            except Exception as e:
                logger.debug(f"No data for {symbol} on {date}: {e}")
                continue
        
        return market_data
    
    async def _generate_signals(self, strategy: Strategy, market_data: Dict, date: date) -> Dict[str, str]:
        """Generate buy/sell signals based on strategy"""
        signals = {}
        
        try:
            entry_conditions = strategy.entry_conditions
            exit_conditions = strategy.exit_conditions
            
            for symbol, data in market_data.items():
                # Simplified signal generation for MVP
                # In production, would use full technical indicator calculation
                
                # Mock signal generation based on price movement
                if data['close'] > data['open'] * 1.02:  # 2% up
                    signals[symbol] = 'BUY'
                elif data['close'] < data['open'] * 0.98:  # 2% down
                    signals[symbol] = 'SELL'
            
        except Exception as e:
            logger.error(f"Error generating signals: {e}")
        
        return signals
    
    def _calculate_performance_metrics(self, portfolio, equity_curve_data: List[Dict]) -> Dict:
        """Calculate performance metrics"""
        try:
            if not equity_curve_data:
                return self._empty_metrics()
            
            df = pd.DataFrame(equity_curve_data)
            
            # Basic metrics
            initial_value = df['portfolio_value'].iloc[0]
            final_value = df['portfolio_value'].iloc[-1]
            total_return = (final_value - initial_value) / initial_value
            
            # Time-based metrics
            days = len(df)
            years = days / 365.25
            annual_return = (1 + total_return) ** (1/years) - 1 if years > 0 else 0
            
            # Risk metrics
            daily_returns = df['daily_return'].dropna()
            if len(daily_returns) > 1:
                volatility = daily_returns.std() * np.sqrt(252)  # Annualized
                sharpe_ratio = annual_return / volatility if volatility > 0 else 0
                
                # Downside returns for Sortino ratio
                downside_returns = daily_returns[daily_returns < 0]
                downside_volatility = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 1 else 0
                sortino_ratio = annual_return / downside_volatility if downside_volatility > 0 else 0
            else:
                sharpe_ratio = 0
                sortino_ratio = 0
            
            # Drawdown
            max_drawdown = df['drawdown'].min() if 'drawdown' in df.columns else 0
            calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
            
            # Trade statistics (simplified)
            total_trades = len([t for t in portfolio.trade_history if t.get('side') == 'BUY'])
            winning_trades = len([t for t in portfolio.trade_history if t.get('pnl', 0) > 0])
            losing_trades = total_trades - winning_trades
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            avg_win = np.mean([t['pnl'] for t in portfolio.trade_history if t.get('pnl', 0) > 0]) if winning_trades > 0 else 0
            avg_loss = np.mean([t['pnl'] for t in portfolio.trade_history if t.get('pnl', 0) < 0]) if losing_trades > 0 else 0
            
            return {
                'total_return': total_return,
                'annual_return': annual_return,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'sortino_ratio': sortino_ratio,
                'calmar_ratio': calmar_ratio,
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'avg_holding_period': 30.0  # Simplified
            }
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return self._empty_metrics()
    
    def _empty_metrics(self) -> Dict:
        """Return empty metrics structure"""
        return {
            'total_return': 0.0,
            'annual_return': 0.0,
            'max_drawdown': 0.0,
            'sharpe_ratio': 0.0,
            'sortino_ratio': 0.0,
            'calmar_ratio': 0.0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'avg_holding_period': 0.0
        }

class Portfolio:
    """Portfolio management for backtesting"""
    
    def __init__(self, initial_capital: float, max_positions: int, commission: float, slippage: float):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.max_positions = max_positions
        self.commission = commission
        self.slippage = slippage
        
        self.positions = {}  # symbol -> {'quantity': int, 'avg_price': float}
        self.total_value = initial_capital
        self.positions_value = 0
        self.trade_history = []
        
        self.daily_return = 0
        self.cumulative_return = 0
        self.peak_value = initial_capital
        self.current_drawdown = 0
    
    def execute_signals(self, signals: Dict[str, str], date: date) -> List[Dict]:
        """Execute trading signals"""
        trades = []
        
        for symbol, signal in signals.items():
            if signal == 'BUY' and len(self.positions) < self.max_positions:
                trade = self._execute_buy(symbol, date)
                if trade:
                    trades.append(trade)
            elif signal == 'SELL' and symbol in self.positions:
                trade = self._execute_sell(symbol, date)
                if trade:
                    trades.append(trade)
        
        return trades
    
    def _execute_buy(self, symbol: str, date: date, price: float = 100000) -> Optional[Dict]:
        """Execute buy order (simplified)"""
        try:
            # Simple position sizing - equal weight
            target_value = self.cash / max(1, self.max_positions - len(self.positions))
            quantity = int(target_value / price)
            
            if quantity > 0 and target_value <= self.cash:
                cost = quantity * price * (1 + self.commission + self.slippage)
                
                if cost <= self.cash:
                    self.cash -= cost
                    self.positions[symbol] = {
                        'quantity': quantity,
                        'avg_price': price
                    }
                    
                    trade = {
                        'symbol': symbol,
                        'side': 'BUY',
                        'quantity': quantity,
                        'price': price,
                        'value': quantity * price,
                        'commission': quantity * price * self.commission,
                        'date': date,
                        'reason': 'Signal buy'
                    }
                    self.trade_history.append(trade)
                    return trade
        
        except Exception as e:
            logger.error(f"Error executing buy for {symbol}: {e}")
        
        return None
    
    def _execute_sell(self, symbol: str, date: date, price: float = 100000) -> Optional[Dict]:
        """Execute sell order (simplified)"""
        try:
            if symbol in self.positions:
                position = self.positions[symbol]
                quantity = position['quantity']
                
                proceeds = quantity * price * (1 - self.commission - self.slippage)
                self.cash += proceeds
                
                # Calculate P&L
                cost_basis = quantity * position['avg_price']
                pnl = proceeds - cost_basis
                
                del self.positions[symbol]
                
                trade = {
                    'symbol': symbol,
                    'side': 'SELL',
                    'quantity': quantity,
                    'price': price,
                    'value': quantity * price,
                    'commission': quantity * price * self.commission,
                    'date': date,
                    'reason': 'Signal sell',
                    'pnl': pnl
                }
                self.trade_history.append(trade)
                return trade
        
        except Exception as e:
            logger.error(f"Error executing sell for {symbol}: {e}")
        
        return None
    
    def update_portfolio_value(self, market_data: Dict, date: date):
        """Update portfolio value based on current market prices"""
        try:
            positions_value = 0
            
            for symbol, position in self.positions.items():
                if symbol in market_data:
                    current_price = market_data[symbol]['close']
                    positions_value += position['quantity'] * current_price
            
            self.positions_value = positions_value
            old_total_value = self.total_value
            self.total_value = self.cash + positions_value
            
            # Calculate returns
            if old_total_value > 0:
                self.daily_return = (self.total_value - old_total_value) / old_total_value
            
            self.cumulative_return = (self.total_value - self.initial_capital) / self.initial_capital
            
            # Calculate drawdown
            if self.total_value > self.peak_value:
                self.peak_value = self.total_value
                self.current_drawdown = 0
            else:
                self.current_drawdown = (self.total_value - self.peak_value) / self.peak_value
        
        except Exception as e:
            logger.error(f"Error updating portfolio value: {e}")