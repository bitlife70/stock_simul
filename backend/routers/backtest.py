from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
import uuid

from database import get_db
from models.strategy import Strategy, Backtest, Trade, EquityCurve
from schemas.backtest import BacktestCreate, BacktestResponse, BacktestStatus
from services.backtest_service import BacktestService

router = APIRouter()

@router.post("/", response_model=BacktestResponse)
async def create_backtest(
    backtest_data: BacktestCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create and start a new backtest"""
    try:
        # Verify strategy exists
        strategy = db.query(Strategy).filter(Strategy.id == backtest_data.strategy_id).first()
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        # Create backtest record
        backtest = Backtest(
            strategy_id=backtest_data.strategy_id,
            start_date=backtest_data.start_date,
            end_date=backtest_data.end_date,
            initial_capital=backtest_data.initial_capital,
            commission=backtest_data.commission,
            slippage=backtest_data.slippage,
            status="pending"
        )
        
        db.add(backtest)
        db.commit()
        db.refresh(backtest)
        
        # Start backtest in background
        backtest_service = BacktestService(db)
        background_tasks.add_task(
            backtest_service.run_backtest, 
            backtest.id
        )
        
        return backtest
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create backtest: {str(e)}")

@router.get("/{backtest_id}", response_model=BacktestResponse)
async def get_backtest(
    backtest_id: str,
    db: Session = Depends(get_db)
):
    """Get backtest by ID"""
    try:
        backtest = db.query(Backtest).filter(Backtest.id == backtest_id).first()
        
        if not backtest:
            raise HTTPException(status_code=404, detail="Backtest not found")
        
        return backtest
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch backtest: {str(e)}")

@router.get("/{backtest_id}/status")
async def get_backtest_status(
    backtest_id: str,
    db: Session = Depends(get_db)
):
    """Get backtest status and progress"""
    try:
        backtest = db.query(Backtest).filter(Backtest.id == backtest_id).first()
        
        if not backtest:
            raise HTTPException(status_code=404, detail="Backtest not found")
        
        return {
            "id": str(backtest.id),
            "status": backtest.status,
            "progress": backtest.progress,
            "error_message": backtest.error_message,
            "created_at": backtest.created_at,
            "completed_at": backtest.completed_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get backtest status: {str(e)}")

@router.get("/strategy/{strategy_id}", response_model=List[BacktestResponse])
async def get_strategy_backtests(
    strategy_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get backtests for a specific strategy"""
    try:
        backtests = db.query(Backtest).filter(
            Backtest.strategy_id == strategy_id
        ).order_by(Backtest.created_at.desc()).limit(limit).all()
        
        return backtests
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch backtests: {str(e)}")

@router.get("/{backtest_id}/trades")
async def get_backtest_trades(
    backtest_id: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get trades for a backtest"""
    try:
        backtest = db.query(Backtest).filter(Backtest.id == backtest_id).first()
        if not backtest:
            raise HTTPException(status_code=404, detail="Backtest not found")
        
        trades = db.query(Trade).filter(
            Trade.backtest_id == backtest_id
        ).order_by(Trade.entry_date.desc()).limit(limit).all()
        
        return [
            {
                "id": str(trade.id),
                "symbol": trade.symbol,
                "side": trade.side,
                "quantity": trade.quantity,
                "price": trade.price,
                "value": trade.value,
                "commission": trade.commission,
                "entry_date": trade.entry_date,
                "exit_date": trade.exit_date,
                "holding_period": trade.holding_period,
                "pnl": trade.pnl,
                "pnl_pct": trade.pnl_pct,
                "trade_reason": trade.trade_reason
            }
            for trade in trades
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trades: {str(e)}")

@router.get("/{backtest_id}/equity-curve")
async def get_equity_curve(
    backtest_id: str,
    db: Session = Depends(get_db)
):
    """Get equity curve data for a backtest"""
    try:
        backtest = db.query(Backtest).filter(Backtest.id == backtest_id).first()
        if not backtest:
            raise HTTPException(status_code=404, detail="Backtest not found")
        
        equity_data = db.query(EquityCurve).filter(
            EquityCurve.backtest_id == backtest_id
        ).order_by(EquityCurve.date).all()
        
        return [
            {
                "date": curve.date.date(),
                "portfolio_value": curve.portfolio_value,
                "cash": curve.cash,
                "positions_value": curve.positions_value,
                "daily_return": curve.daily_return,
                "cumulative_return": curve.cumulative_return,
                "drawdown": curve.drawdown,
                "benchmark_value": curve.benchmark_value,
                "benchmark_return": curve.benchmark_return,
                "excess_return": curve.excess_return
            }
            for curve in equity_data
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch equity curve: {str(e)}")

@router.delete("/{backtest_id}")
async def delete_backtest(
    backtest_id: str,
    db: Session = Depends(get_db)
):
    """Delete a backtest"""
    try:
        backtest = db.query(Backtest).filter(Backtest.id == backtest_id).first()
        
        if not backtest:
            raise HTTPException(status_code=404, detail="Backtest not found")
        
        # Delete related data
        db.query(Trade).filter(Trade.backtest_id == backtest_id).delete()
        db.query(EquityCurve).filter(EquityCurve.backtest_id == backtest_id).delete()
        db.delete(backtest)
        db.commit()
        
        return {"message": "Backtest deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete backtest: {str(e)}")