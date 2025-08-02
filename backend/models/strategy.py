from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from database import Base
import uuid
from datetime import datetime

class Strategy(Base):
    __tablename__ = "strategies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Strategy configuration
    market = Column(String(10), nullable=False, default="KOSPI")  # KOSPI, KOSDAQ, ALL
    universe = Column(JSONB, nullable=False)  # 종목 선택 조건
    
    # Entry conditions
    entry_conditions = Column(JSONB, nullable=False)  # 매수 조건
    exit_conditions = Column(JSONB, nullable=False)   # 매도 조건
    
    # Portfolio settings
    position_sizing = Column(String(20), default="equal_weight")  # equal_weight, risk_based, etc.
    max_positions = Column(Integer, default=10)
    rebalance_frequency = Column(String(20), default="monthly")  # daily, weekly, monthly
    
    # Risk management
    stop_loss_pct = Column(Float, nullable=True)  # 손절 비율
    take_profit_pct = Column(Float, nullable=True)  # 익절 비율
    max_drawdown_limit = Column(Float, nullable=True)  # 최대 낙폭 제한
    
    # Metadata
    created_by = Column(String(100), nullable=True)  # 사용자 ID (추후 인증 시스템 연동)
    is_active = Column(Boolean, default=True)
    is_template = Column(Boolean, default=False)  # 템플릿 전략 여부
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    backtests = relationship("Backtest", back_populates="strategy")

class Backtest(Base):
    __tablename__ = "backtests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    strategy_id = Column(UUID(as_uuid=True), ForeignKey("strategies.id"), nullable=False)
    
    # Test configuration
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    initial_capital = Column(Float, nullable=False, default=10_000_000)
    commission = Column(Float, nullable=False, default=0.003)  # 0.3%
    slippage = Column(Float, nullable=False, default=0.001)   # 0.1%
    
    # Results summary
    total_return = Column(Float, nullable=True)  # 총 수익률
    annual_return = Column(Float, nullable=True)  # 연간 수익률
    max_drawdown = Column(Float, nullable=True)   # 최대 낙폭
    sharpe_ratio = Column(Float, nullable=True)   # 샤프 비율
    sortino_ratio = Column(Float, nullable=True)  # 소티노 비율
    calmar_ratio = Column(Float, nullable=True)   # 칼마 비율
    
    # Trade statistics
    total_trades = Column(Integer, nullable=True)
    winning_trades = Column(Integer, nullable=True)
    losing_trades = Column(Integer, nullable=True)
    win_rate = Column(Float, nullable=True)
    avg_win = Column(Float, nullable=True)
    avg_loss = Column(Float, nullable=True)
    avg_holding_period = Column(Float, nullable=True)  # 평균 보유 기간 (일)
    
    # Status
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Progress tracking
    progress = Column(Float, default=0.0)  # 0.0 - 1.0
    
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    strategy = relationship("Strategy", back_populates="backtests")
    trades = relationship("Trade", back_populates="backtest")
    equity_curves = relationship("EquityCurve", back_populates="backtest")

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    backtest_id = Column(UUID(as_uuid=True), ForeignKey("backtests.id"), nullable=False)
    
    # Trade details
    symbol = Column(String(10), nullable=False)
    side = Column(String(4), nullable=False)  # BUY, SELL
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    value = Column(Float, nullable=False)  # quantity * price
    commission = Column(Float, nullable=False)
    
    # Timing
    entry_date = Column(DateTime, nullable=True)
    exit_date = Column(DateTime, nullable=True)
    holding_period = Column(Integer, nullable=True)  # 보유 기간 (일)
    
    # Performance (for closed trades)
    pnl = Column(Float, nullable=True)  # 손익
    pnl_pct = Column(Float, nullable=True)  # 손익률
    
    # Metadata
    trade_reason = Column(String(100), nullable=True)  # 거래 사유
    is_closed = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    backtest = relationship("Backtest", back_populates="trades")

class EquityCurve(Base):
    __tablename__ = "equity_curves"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    backtest_id = Column(UUID(as_uuid=True), ForeignKey("backtests.id"), nullable=False)
    
    date = Column(DateTime, nullable=False)
    portfolio_value = Column(Float, nullable=False)  # 포트폴리오 총 가치
    cash = Column(Float, nullable=False)  # 현금
    positions_value = Column(Float, nullable=False)  # 보유 주식 가치
    
    # Performance metrics
    daily_return = Column(Float, nullable=True)  # 일간 수익률
    cumulative_return = Column(Float, nullable=True)  # 누적 수익률
    drawdown = Column(Float, nullable=True)  # 낙폭
    
    # Benchmark comparison
    benchmark_value = Column(Float, nullable=True)  # 벤치마크 (KOSPI/KOSDAQ)
    benchmark_return = Column(Float, nullable=True)  # 벤치마크 수익률
    excess_return = Column(Float, nullable=True)  # 초과 수익률
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    backtest = relationship("Backtest", back_populates="equity_curves")