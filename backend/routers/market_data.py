from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
import pandas as pd

from database import get_db
from services.data_service import DataService
from schemas.market_data import StockDataResponse, StockInfoResponse, TechnicalIndicatorResponse

router = APIRouter()

@router.get("/stocks", response_model=List[StockInfoResponse])
async def get_stock_list(
    market: Optional[str] = Query(None, description="Market filter: KOSPI, KOSDAQ, or ALL"),
    sector: Optional[str] = Query(None, description="Sector filter"),
    limit: int = Query(100, le=1000, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """한국 주식 종목 리스트 조회"""
    try:
        data_service = DataService(db)
        stocks = await data_service.get_stock_list(
            market=market,
            sector=sector,
            limit=limit
        )
        return stocks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stock list: {str(e)}")

@router.get("/stocks/{symbol}/price", response_model=List[StockDataResponse])
async def get_stock_price_data(
    symbol: str,
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """특정 종목의 주가 데이터 조회"""
    try:
        data_service = DataService(db)
        
        # Validate date range
        if start_date >= end_date:
            raise HTTPException(status_code=400, detail="Start date must be before end date")
        
        price_data = await data_service.get_stock_price_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )
        
        if not price_data:
            raise HTTPException(
                status_code=404, 
                detail=f"No price data found for symbol {symbol} in the specified date range"
            )
        
        return price_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch price data: {str(e)}")

@router.get("/stocks/{symbol}/indicators", response_model=List[TechnicalIndicatorResponse])
async def get_technical_indicators(
    symbol: str,
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    indicators: List[str] = Query(
        ["ma_20", "rsi_14", "macd"], 
        description="List of indicators to fetch"
    ),
    db: Session = Depends(get_db)
):
    """특정 종목의 기술적 지표 데이터 조회"""
    try:
        data_service = DataService(db)
        
        indicator_data = await data_service.get_technical_indicators(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            indicators=indicators
        )
        
        return indicator_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch indicators: {str(e)}")

@router.post("/update/{symbol}")
async def update_stock_data(
    symbol: str,
    force_update: bool = Query(False, description="Force update even if data is recent"),
    db: Session = Depends(get_db)
):
    """특정 종목의 데이터 업데이트"""
    try:
        data_service = DataService(db)
        
        result = await data_service.update_stock_data(
            symbol=symbol,
            force_update=force_update
        )
        
        return {
            "symbol": symbol,
            "status": "success",
            "message": f"Updated {result['records_updated']} records",
            "latest_date": result.get('latest_date'),
            "updated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update data: {str(e)}")

@router.post("/update-all")
async def update_all_market_data(
    market: str = Query("KOSPI", description="Market to update: KOSPI, KOSDAQ, or ALL"),
    db: Session = Depends(get_db)
):
    """전체 시장 데이터 업데이트 (비동기 작업)"""
    try:
        data_service = DataService(db)
        
        # This would typically be handled by a background task (Celery)
        task_id = await data_service.schedule_market_update(market=market)
        
        return {
            "status": "accepted",
            "message": f"Market data update scheduled for {market}",
            "task_id": task_id,
            "estimated_completion": "15-30 minutes"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule update: {str(e)}")

@router.get("/market-overview")
async def get_market_overview(
    market: str = Query("ALL", description="Market: KOSPI, KOSDAQ, or ALL"),
    db: Session = Depends(get_db)
):
    """시장 개요 정보 조회"""
    try:
        data_service = DataService(db)
        
        overview = await data_service.get_market_overview(market=market)
        
        return {
            "market": market,
            "total_stocks": overview.get("total_stocks", 0),
            "active_stocks": overview.get("active_stocks", 0),
            "latest_data_date": overview.get("latest_data_date"),
            "data_coverage": overview.get("data_coverage", {}),
            "top_sectors": overview.get("top_sectors", []),
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get market overview: {str(e)}")

@router.get("/search")
async def search_stocks(
    query: str = Query(..., min_length=1, description="Search query (symbol or name)"),
    limit: int = Query(20, le=100, description="Maximum results"),
    db: Session = Depends(get_db)
):
    """종목 검색"""
    try:
        data_service = DataService(db)
        
        results = await data_service.search_stocks(query=query, limit=limit)
        
        return {
            "query": query,
            "results": results,
            "total_found": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")