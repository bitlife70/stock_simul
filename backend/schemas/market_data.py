from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

class StockInfoResponse(BaseModel):
    symbol: str = Field(..., description="Stock symbol (e.g., 005930)")
    name: str = Field(..., description="Stock name (e.g., 삼성전자)")
    market: str = Field(..., description="Market (KOSPI/KOSDAQ)")
    sector: Optional[str] = Field(None, description="Sector")
    industry: Optional[str] = Field(None, description="Industry")
    
    class Config:
        from_attributes = True

class StockDataResponse(BaseModel):
    date: date = Field(..., description="Trading date")
    symbol: str = Field(..., description="Stock symbol")
    name: str = Field(..., description="Stock name")
    open: float = Field(..., description="Opening price")
    high: float = Field(..., description="Highest price")
    low: float = Field(..., description="Lowest price")
    close: float = Field(..., description="Closing price")
    volume: int = Field(..., description="Trading volume")
    
    class Config:
        from_attributes = True

class TechnicalIndicatorResponse(BaseModel):
    date: date = Field(..., description="Date")
    symbol: str = Field(..., description="Stock symbol")
    
    # Moving Averages
    ma_5: Optional[float] = Field(None, description="5-day moving average")
    ma_10: Optional[float] = Field(None, description="10-day moving average")
    ma_20: Optional[float] = Field(None, description="20-day moving average")
    ma_60: Optional[float] = Field(None, description="60-day moving average")
    ma_120: Optional[float] = Field(None, description="120-day moving average")
    ma_200: Optional[float] = Field(None, description="200-day moving average")
    
    # RSI
    rsi_9: Optional[float] = Field(None, description="9-period RSI")
    rsi_14: Optional[float] = Field(None, description="14-period RSI")
    rsi_25: Optional[float] = Field(None, description="25-period RSI")
    
    # MACD
    macd: Optional[float] = Field(None, description="MACD line")
    macd_signal: Optional[float] = Field(None, description="MACD signal line")
    macd_histogram: Optional[float] = Field(None, description="MACD histogram")
    
    # Bollinger Bands
    bb_upper: Optional[float] = Field(None, description="Bollinger Band upper")
    bb_middle: Optional[float] = Field(None, description="Bollinger Band middle")
    bb_lower: Optional[float] = Field(None, description="Bollinger Band lower")
    bb_width: Optional[float] = Field(None, description="Bollinger Band width")
    
    # Volume Indicators
    volume_ma_10: Optional[float] = Field(None, description="10-day volume MA")
    volume_ma_20: Optional[float] = Field(None, description="20-day volume MA")
    obv: Optional[float] = Field(None, description="On-Balance Volume")
    
    class Config:
        from_attributes = True

class MarketOverviewResponse(BaseModel):
    market: str = Field(..., description="Market name")
    total_stocks: int = Field(..., description="Total number of stocks")
    active_stocks: int = Field(..., description="Number of active stocks")
    latest_data_date: Optional[date] = Field(None, description="Latest data date")
    data_coverage: dict = Field(..., description="Data coverage statistics")
    top_sectors: List[dict] = Field(..., description="Top sectors by stock count")
    generated_at: datetime = Field(..., description="Response generation time")

class StockSearchResponse(BaseModel):
    query: str = Field(..., description="Search query")
    results: List[StockInfoResponse] = Field(..., description="Search results")
    total_found: int = Field(..., description="Total results found")