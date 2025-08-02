from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

class StrategyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Strategy name")
    description: Optional[str] = Field(None, max_length=500, description="Strategy description")
    market: str = Field("KOSPI", description="Target market (KOSPI/KOSDAQ/ALL)")
    universe: Dict[str, Any] = Field(..., description="Stock universe selection criteria")
    entry_conditions: Dict[str, Any] = Field(..., description="Entry signal conditions")
    exit_conditions: Dict[str, Any] = Field(..., description="Exit signal conditions")
    position_sizing: str = Field("equal_weight", description="Position sizing method")
    max_positions: int = Field(10, ge=1, le=50, description="Maximum number of positions")
    rebalance_frequency: str = Field("monthly", description="Rebalancing frequency")
    stop_loss_pct: Optional[float] = Field(None, ge=0.01, le=0.5, description="Stop loss percentage")
    take_profit_pct: Optional[float] = Field(None, ge=0.05, le=2.0, description="Take profit percentage")
    max_drawdown_limit: Optional[float] = Field(None, ge=0.05, le=0.5, description="Maximum drawdown limit")

class StrategyCreate(StrategyBase):
    pass

class StrategyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    market: Optional[str] = None
    universe: Optional[Dict[str, Any]] = None
    entry_conditions: Optional[Dict[str, Any]] = None
    exit_conditions: Optional[Dict[str, Any]] = None
    position_sizing: Optional[str] = None
    max_positions: Optional[int] = Field(None, ge=1, le=50)
    rebalance_frequency: Optional[str] = None
    stop_loss_pct: Optional[float] = Field(None, ge=0.01, le=0.5)
    take_profit_pct: Optional[float] = Field(None, ge=0.05, le=2.0)
    max_drawdown_limit: Optional[float] = Field(None, ge=0.05, le=0.5)
    is_active: Optional[bool] = None

class StrategyResponse(StrategyBase):
    id: UUID = Field(..., description="Strategy ID")
    created_by: Optional[str] = Field(None, description="Creator")
    is_active: bool = Field(..., description="Active status")
    is_template: bool = Field(..., description="Template status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True

# Strategy condition schemas
class IndicatorCondition(BaseModel):
    indicator: str = Field(..., description="Technical indicator name")
    operator: str = Field(..., description="Comparison operator")
    value: float = Field(..., description="Comparison value")
    reference: Optional[str] = Field(None, description="Reference indicator (for crossovers)")

class StrategyConditions(BaseModel):
    conditions: List[IndicatorCondition] = Field(..., description="List of conditions")
    logic: str = Field("AND", description="Logic operator (AND/OR)")

# Universe selection schemas
class UniverseFilter(BaseModel):
    market: Optional[str] = Field(None, description="Market filter")
    sector: Optional[str] = Field(None, description="Sector filter")
    min_market_cap: Optional[float] = Field(None, description="Minimum market cap")
    max_market_cap: Optional[float] = Field(None, description="Maximum market cap")
    min_volume: Optional[int] = Field(None, description="Minimum daily volume")
    min_price: Optional[float] = Field(None, description="Minimum stock price")
    max_price: Optional[float] = Field(None, description="Maximum stock price")
    exclude_stocks: Optional[List[str]] = Field(None, description="Stocks to exclude")
    include_stocks: Optional[List[str]] = Field(None, description="Stocks to include")

# Template strategy schemas
class StrategyTemplate(BaseModel):
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    category: str = Field(..., description="Strategy category")
    difficulty: str = Field("beginner", description="Difficulty level")
    expected_return: Optional[float] = Field(None, description="Expected annual return")
    max_drawdown: Optional[float] = Field(None, description="Expected max drawdown")
    strategy_config: StrategyCreate = Field(..., description="Strategy configuration")

class StrategyTemplateResponse(BaseModel):
    templates: List[StrategyTemplate] = Field(..., description="Available templates")
    categories: List[str] = Field(..., description="Available categories")
    total_count: int = Field(..., description="Total number of templates")