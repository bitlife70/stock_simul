from sqlalchemy import Column, Integer, String, Float, DateTime, Index, Boolean
from sqlalchemy.dialects.postgresql import UUID
from database import Base
import uuid
from datetime import datetime

class StockData(Base):
    __tablename__ = "stock_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(10), nullable=False, index=True)  # 종목코드 (005930)
    name = Column(String(100), nullable=False)  # 종목명 (삼성전자)
    market = Column(String(10), nullable=False, index=True)  # KOSPI, KOSDAQ
    date = Column(DateTime, nullable=False, index=True)
    
    # OHLCV Data
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    
    # Additional Korean market data
    market_cap = Column(Float, nullable=True)  # 시가총액
    foreign_ratio = Column(Float, nullable=True)  # 외국인 보유비율
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Composite indexes for performance
    __table_args__ = (
        Index('idx_symbol_date', 'symbol', 'date'),
        Index('idx_market_date', 'market', 'date'),
        Index('idx_date_symbol', 'date', 'symbol'),
    )

class StockInfo(Base):
    __tablename__ = "stock_info"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    market = Column(String(10), nullable=False)  # KOSPI, KOSDAQ, KONEX
    sector = Column(String(50), nullable=True)  # 업종
    industry = Column(String(100), nullable=True)  # 산업
    
    # Market info
    listing_date = Column(DateTime, nullable=True)  # 상장일
    is_active = Column(Boolean, default=True)  # 거래 가능 여부
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TechnicalIndicator(Base):
    __tablename__ = "technical_indicators"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(10), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    
    # Moving Averages
    ma_5 = Column(Float, nullable=True)
    ma_10 = Column(Float, nullable=True)
    ma_20 = Column(Float, nullable=True)
    ma_60 = Column(Float, nullable=True)
    ma_120 = Column(Float, nullable=True)
    ma_200 = Column(Float, nullable=True)
    
    # Technical Indicators
    rsi_14 = Column(Float, nullable=True)
    rsi_9 = Column(Float, nullable=True)
    rsi_25 = Column(Float, nullable=True)
    
    # MACD
    macd = Column(Float, nullable=True)
    macd_signal = Column(Float, nullable=True)
    macd_histogram = Column(Float, nullable=True)
    
    # Bollinger Bands
    bb_upper = Column(Float, nullable=True)
    bb_middle = Column(Float, nullable=True)
    bb_lower = Column(Float, nullable=True)
    bb_width = Column(Float, nullable=True)
    
    # Volume Indicators
    volume_ma_10 = Column(Float, nullable=True)
    volume_ma_20 = Column(Float, nullable=True)
    obv = Column(Float, nullable=True)  # On-Balance Volume
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_ti_symbol_date', 'symbol', 'date'),
    )