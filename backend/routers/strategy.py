from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from database import get_db
from models.strategy import Strategy, Backtest
from schemas.strategy import StrategyCreate, StrategyResponse, BacktestCreate, BacktestResponse

router = APIRouter()

@router.get("/", response_model=List[StrategyResponse])
async def get_strategies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of strategies"""
    try:
        strategies = db.query(Strategy).filter(
            Strategy.is_active == True
        ).offset(skip).limit(limit).all()
        
        return strategies
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch strategies: {str(e)}")

@router.post("/", response_model=StrategyResponse)
async def create_strategy(
    strategy: StrategyCreate,
    db: Session = Depends(get_db)
):
    """Create a new strategy"""
    try:
        db_strategy = Strategy(
            name=strategy.name,
            description=strategy.description,
            market=strategy.market,
            universe=strategy.universe,
            entry_conditions=strategy.entry_conditions,
            exit_conditions=strategy.exit_conditions,
            position_sizing=strategy.position_sizing,
            max_positions=strategy.max_positions,
            rebalance_frequency=strategy.rebalance_frequency,
            stop_loss_pct=strategy.stop_loss_pct,
            take_profit_pct=strategy.take_profit_pct
        )
        
        db.add(db_strategy)
        db.commit()
        db.refresh(db_strategy)
        
        return db_strategy
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create strategy: {str(e)}")

@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: str,
    db: Session = Depends(get_db)
):
    """Get strategy by ID"""
    try:
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        return strategy
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch strategy: {str(e)}")

@router.get("/templates/", response_model=List[StrategyResponse])
async def get_strategy_templates(db: Session = Depends(get_db)):
    """Get predefined strategy templates"""
    try:
        templates = db.query(Strategy).filter(
            Strategy.is_template == True,
            Strategy.is_active == True
        ).all()
        
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch templates: {str(e)}")

@router.post("/templates/create-defaults")
async def create_default_templates(db: Session = Depends(get_db)):
    """Create default Korean market strategy templates"""
    try:
        # Golden Cross Strategy
        golden_cross = Strategy(
            name="골든 크로스 전략",
            description="5일 이동평균이 20일 이동평균을 상향 돌파할 때 매수",
            market="KOSPI",
            universe={"market": "KOSPI", "min_volume": 100000},
            entry_conditions={
                "conditions": [
                    {"indicator": "ma_5", "operator": "crosses_above", "value": "ma_20"},
                    {"indicator": "volume", "operator": "greater_than", "value": "volume_ma_20"}
                ],
                "logic": "AND"
            },
            exit_conditions={
                "conditions": [
                    {"indicator": "ma_5", "operator": "crosses_below", "value": "ma_20"}
                ],
                "logic": "OR"
            },
            position_sizing="equal_weight",
            max_positions=10,
            is_template=True
        )
        
        # RSI Strategy
        rsi_strategy = Strategy(
            name="RSI 역추세 전략",
            description="RSI 30 이하에서 매수, 70 이상에서 매도",
            market="KOSDAQ",
            universe={"market": "KOSDAQ", "min_market_cap": 1000000000},
            entry_conditions={
                "conditions": [
                    {"indicator": "rsi_14", "operator": "less_than", "value": 30},
                    {"indicator": "close", "operator": "greater_than", "value": "ma_20"}
                ],
                "logic": "AND"
            },
            exit_conditions={
                "conditions": [
                    {"indicator": "rsi_14", "operator": "greater_than", "value": 70}
                ],
                "logic": "OR"
            },
            position_sizing="equal_weight",
            max_positions=15,
            stop_loss_pct=0.05,
            take_profit_pct=0.15,
            is_template=True
        )
        
        db.add(golden_cross)
        db.add(rsi_strategy)
        db.commit()
        
        return {"message": "Default templates created successfully", "count": 2}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create templates: {str(e)}")