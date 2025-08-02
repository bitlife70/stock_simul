from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal

class BacktestBase(BaseModel):
    strategy_id: UUID = Field(..., description="Strategy ID")
    start_date: date = Field(..., description="Backtest start date")
    end_date: date = Field(..., description="Backtest end date")
    initial_capital: float = Field(10_000_000, ge=1_000_000, le=1_000_000_000, description="Initial capital in KRW")
    commission: float = Field(0.003, ge=0.0, le=0.01, description="Commission rate")
    slippage: float = Field(0.001, ge=0.0, le=0.01, description="Slippage rate")

class BacktestCreate(BacktestBase):
    pass

class BacktestResponse(BacktestBase):
    id: UUID = Field(..., description="Backtest ID")
    
    # Results summary
    total_return: Optional[float] = Field(None, description="Total return percentage")
    annual_return: Optional[float] = Field(None, description="Annualized return percentage")
    max_drawdown: Optional[float] = Field(None, description="Maximum drawdown percentage")
    sharpe_ratio: Optional[float] = Field(None, description="Sharpe ratio")
    sortino_ratio: Optional[float] = Field(None, description="Sortino ratio")
    calmar_ratio: Optional[float] = Field(None, description="Calmar ratio")
    
    # Trade statistics
    total_trades: Optional[int] = Field(None, description="Total number of trades")
    winning_trades: Optional[int] = Field(None, description="Number of winning trades")
    losing_trades: Optional[int] = Field(None, description="Number of losing trades")
    win_rate: Optional[float] = Field(None, description="Win rate percentage")
    avg_win: Optional[float] = Field(None, description="Average winning trade percentage")
    avg_loss: Optional[float] = Field(None, description="Average losing trade percentage")
    avg_holding_period: Optional[float] = Field(None, description="Average holding period in days")
    
    # Status
    status: str = Field(..., description="Backtest status")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    progress: float = Field(0.0, description="Progress percentage (0.0-1.0)")
    
    created_at: datetime = Field(..., description="Creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    
    class Config:
        from_attributes = True

class BacktestStatus(BaseModel):
    id: UUID = Field(..., description="Backtest ID")
    status: str = Field(..., description="Current status")
    progress: float = Field(..., description="Progress percentage")
    error_message: Optional[str] = Field(None, description="Error message")
    created_at: datetime = Field(..., description="Creation time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")

class TradeResponse(BaseModel):
    id: UUID = Field(..., description="Trade ID")
    backtest_id: UUID = Field(..., description="Backtest ID")
    symbol: str = Field(..., description="Stock symbol")
    side: str = Field(..., description="Trade side (BUY/SELL)")
    quantity: int = Field(..., description="Number of shares")
    price: float = Field(..., description="Execution price")
    value: float = Field(..., description="Trade value")
    commission: float = Field(..., description="Commission paid")
    
    entry_date: Optional[date] = Field(None, description="Entry date")
    exit_date: Optional[date] = Field(None, description="Exit date")
    holding_period: Optional[int] = Field(None, description="Holding period in days")
    
    pnl: Optional[float] = Field(None, description="Profit/Loss in KRW")
    pnl_pct: Optional[float] = Field(None, description="Profit/Loss percentage")
    trade_reason: Optional[str] = Field(None, description="Reason for trade")
    is_closed: bool = Field(..., description="Whether trade is closed")
    
    created_at: datetime = Field(..., description="Trade timestamp")
    
    class Config:
        from_attributes = True

class EquityCurveResponse(BaseModel):
    date: date = Field(..., description="Date")
    portfolio_value: float = Field(..., description="Total portfolio value")
    cash: float = Field(..., description="Cash amount")
    positions_value: float = Field(..., description="Value of stock positions")
    
    daily_return: Optional[float] = Field(None, description="Daily return percentage")
    cumulative_return: Optional[float] = Field(None, description="Cumulative return percentage")
    drawdown: Optional[float] = Field(None, description="Drawdown percentage")
    
    benchmark_value: Optional[float] = Field(None, description="Benchmark portfolio value")
    benchmark_return: Optional[float] = Field(None, description="Benchmark return percentage")
    excess_return: Optional[float] = Field(None, description="Excess return vs benchmark")

class BacktestSummary(BaseModel):
    id: UUID = Field(..., description="Backtest ID")
    strategy_name: str = Field(..., description="Strategy name")
    period: str = Field(..., description="Test period")
    status: str = Field(..., description="Status")
    
    # Key metrics
    total_return: Optional[float] = Field(None, description="Total return")
    annual_return: Optional[float] = Field(None, description="Annual return")
    max_drawdown: Optional[float] = Field(None, description="Max drawdown")
    sharpe_ratio: Optional[float] = Field(None, description="Sharpe ratio")
    
    created_at: datetime = Field(..., description="Creation time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")

class BacktestComparison(BaseModel):
    backtests: List[BacktestSummary] = Field(..., description="Backtests to compare")
    comparison_metrics: dict = Field(..., description="Comparison statistics")
    winner: Optional[UUID] = Field(None, description="Best performing backtest ID")