import asyncio
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_

# Korean stock data libraries
import FinanceDataReader as fdr
from pykrx import stock
import logging

from models.stock_data import StockData, StockInfo, TechnicalIndicator
from utils.technical_indicators import TechnicalIndicatorCalculator

logger = logging.getLogger(__name__)

class DataService:
    def __init__(self, db: Session):
        self.db = db
        self.calculator = TechnicalIndicatorCalculator()
    
    async def get_stock_list(self, market: Optional[str] = None, sector: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get list of Korean stocks"""
        try:
            query = self.db.query(StockInfo).filter(StockInfo.is_active == True)
            
            if market and market != "ALL":
                query = query.filter(StockInfo.market == market)
            
            if sector:
                query = query.filter(StockInfo.sector == sector)
            
            stocks = query.limit(limit).all()
            
            return [
                {
                    "symbol": stock.symbol,
                    "name": stock.name,
                    "market": stock.market,
                    "sector": stock.sector,
                    "industry": stock.industry
                }
                for stock in stocks
            ]
        except Exception as e:
            logger.error(f"Error fetching stock list: {e}")
            # Fallback to live data if database is empty
            return await self._fetch_live_stock_list(market, limit)
    
    async def _fetch_live_stock_list(self, market: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Fetch stock list from live sources"""
        try:
            stocks = []
            
            if not market or market in ["KOSPI", "ALL"]:
                kospi_stocks = stock.get_market_ticker_list(market="KOSPI")
                for symbol in kospi_stocks[:limit//2 if market == "ALL" else limit]:
                    try:
                        name = stock.get_market_ticker_name(symbol)
                        stocks.append({
                            "symbol": symbol,
                            "name": name,
                            "market": "KOSPI",
                            "sector": None,
                            "industry": None
                        })
                    except:
                        continue
            
            if not market or market in ["KOSDAQ", "ALL"]:
                kosdaq_stocks = stock.get_market_ticker_list(market="KOSDAQ")
                for symbol in kosdaq_stocks[:limit//2 if market == "ALL" else limit]:
                    try:
                        name = stock.get_market_ticker_name(symbol)
                        stocks.append({
                            "symbol": symbol,
                            "name": name,
                            "market": "KOSDAQ",
                            "sector": None,
                            "industry": None
                        })
                    except:
                        continue
            
            return stocks[:limit]
        except Exception as e:
            logger.error(f"Error fetching live stock list: {e}")
            # Return sample data as fallback
            return [
                {"symbol": "005930", "name": "삼성전자", "market": "KOSPI", "sector": "기술주", "industry": "반도체"},
                {"symbol": "000660", "name": "SK하이닉스", "market": "KOSPI", "sector": "기술주", "industry": "반도체"},
                {"symbol": "035420", "name": "NAVER", "market": "KOSPI", "sector": "기술주", "industry": "인터넷"},
                {"symbol": "051910", "name": "LG화학", "market": "KOSPI", "sector": "화학", "industry": "화학"},
                {"Symbol": "068270", "name": "셀트리온", "market": "KOSPI", "sector": "바이오", "industry": "바이오의약품"}
            ]
    
    async def get_stock_price_data(
        self, 
        symbol: str, 
        start_date: date, 
        end_date: date
    ) -> List[Dict]:
        """Get stock price data for a symbol"""
        try:
            # First check database
            db_data = self.db.query(StockData).filter(
                and_(
                    StockData.symbol == symbol,
                    StockData.date >= start_date,
                    StockData.date <= end_date
                )
            ).order_by(StockData.date).all()
            
            if db_data:
                return [
                    {
                        "date": data.date.date(),
                        "open": data.open_price,
                        "high": data.high_price,
                        "low": data.low_price,
                        "close": data.close_price,
                        "volume": data.volume,
                        "symbol": data.symbol,
                        "name": data.name
                    }
                    for data in db_data
                ]
            
            # Fallback to live data
            return await self._fetch_live_price_data(symbol, start_date, end_date)
            
        except Exception as e:
            logger.error(f"Error fetching price data for {symbol}: {e}")
            return []
    
    async def _fetch_live_price_data(self, symbol: str, start_date: date, end_date: date) -> List[Dict]:
        """Fetch price data from live sources"""
        try:
            # Use FinanceDataReader first
            df = fdr.DataReader(symbol, start_date, end_date)
            
            if df.empty:
                # Fallback to pykrx
                df = stock.get_market_ohlcv_by_date(
                    start_date.strftime("%Y%m%d"), 
                    end_date.strftime("%Y%m%d"), 
                    symbol
                )
            
            if df.empty:
                return []
            
            # Get stock name
            try:
                stock_name = stock.get_market_ticker_name(symbol)
            except:
                stock_name = symbol
            
            # Convert to list of dictionaries
            result = []
            for date_idx, row in df.iterrows():
                result.append({
                    "date": date_idx.date() if hasattr(date_idx, 'date') else date_idx,
                    "open": float(row.get('Open', row.get('시가', 0))),
                    "high": float(row.get('High', row.get('고가', 0))),
                    "low": float(row.get('Low', row.get('저가', 0))),
                    "close": float(row.get('Close', row.get('종가', 0))),
                    "volume": int(row.get('Volume', row.get('거래량', 0))),
                    "symbol": symbol,
                    "name": stock_name
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching live price data for {symbol}: {e}")
            return []
    
    async def get_technical_indicators(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        indicators: List[str]
    ) -> List[Dict]:
        """Get technical indicators for a symbol"""
        try:
            # First get price data
            price_data = await self.get_stock_price_data(symbol, start_date, end_date)
            
            if not price_data:
                return []
            
            # Convert to DataFrame for calculation
            df = pd.DataFrame(price_data)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # Calculate indicators with symbol for Korean market optimizations
            indicator_data = self.calculator.calculate_all_indicators(df, symbol)
            
            # Filter requested indicators and return
            result = []
            for date_idx, row in indicator_data.iterrows():
                indicator_dict = {
                    "date": date_idx.date(),
                    "symbol": symbol
                }
                
                for indicator in indicators:
                    if indicator in row:
                        indicator_dict[indicator] = float(row[indicator]) if pd.notna(row[indicator]) else None
                
                result.append(indicator_dict)
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating indicators for {symbol}: {e}")
            return []
    
    async def update_stock_data(self, symbol: str, force_update: bool = False) -> Dict[str, Any]:
        """Update stock data for a specific symbol"""
        try:
            # Get latest data date from database
            latest_data = self.db.query(StockData).filter(
                StockData.symbol == symbol
            ).order_by(desc(StockData.date)).first()
            
            if latest_data and not force_update:
                # Check if data is recent (within last 2 days)
                days_diff = (datetime.now().date() - latest_data.date.date()).days
                if days_diff < 2:
                    return {
                        "symbol": symbol,
                        "records_updated": 0,
                        "message": "Data is already up to date",
                        "latest_date": latest_data.date.date()
                    }
            
            # Determine date range for update
            start_date = latest_data.date.date() + timedelta(days=1) if latest_data else date.today() - timedelta(days=365*2)
            end_date = date.today()
            
            # Fetch new data
            new_data = await self._fetch_live_price_data(symbol, start_date, end_date)
            
            if not new_data:
                return {
                    "symbol": symbol,
                    "records_updated": 0,
                    "message": "No new data available"
                }
            
            # Save to database
            records_updated = 0
            for data_point in new_data:
                # Check if record already exists
                existing = self.db.query(StockData).filter(
                    and_(
                        StockData.symbol == symbol,
                        StockData.date == data_point["date"]
                    )
                ).first()
                
                if not existing:
                    stock_data = StockData(
                        symbol=symbol,
                        name=data_point["name"],
                        market="KOSPI" if symbol in stock.get_market_ticker_list("KOSPI") else "KOSDAQ",
                        date=data_point["date"],
                        open_price=data_point["open"],
                        high_price=data_point["high"],
                        low_price=data_point["low"],
                        close_price=data_point["close"],
                        volume=data_point["volume"]
                    )
                    self.db.add(stock_data)
                    records_updated += 1
            
            self.db.commit()
            
            return {
                "symbol": symbol,
                "records_updated": records_updated,
                "latest_date": end_date,
                "message": f"Successfully updated {records_updated} records"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating stock data for {symbol}: {e}")
            raise e
    
    async def schedule_market_update(self, market: str = "KOSPI") -> str:
        """Schedule market-wide data update (returns task ID)"""
        # In a real implementation, this would use Celery or similar
        # For now, return a mock task ID
        task_id = f"market_update_{market}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Log the scheduled task
        logger.info(f"Scheduled market update for {market} with task ID: {task_id}")
        
        return task_id
    
    async def get_market_overview(self, market: str = "ALL") -> Dict[str, Any]:
        """Get market overview statistics"""
        try:
            query = self.db.query(StockInfo)
            
            if market != "ALL":
                query = query.filter(StockInfo.market == market)
            
            total_stocks = query.count()
            active_stocks = query.filter(StockInfo.is_active == True).count()
            
            # Get latest data date
            latest_data_query = self.db.query(func.max(StockData.date))
            if market != "ALL":
                # Join with StockInfo to filter by market
                latest_data_query = latest_data_query.join(
                    StockInfo, StockData.symbol == StockInfo.symbol
                ).filter(StockInfo.market == market)
            
            latest_date = latest_data_query.scalar()
            
            # Get sector distribution
            sector_query = self.db.query(
                StockInfo.sector,
                func.count(StockInfo.symbol).label('count')
            ).filter(StockInfo.is_active == True)
            
            if market != "ALL":
                sector_query = sector_query.filter(StockInfo.market == market)
            
            sectors = sector_query.group_by(StockInfo.sector).order_by(desc('count')).limit(10).all()
            
            return {
                "total_stocks": total_stocks,
                "active_stocks": active_stocks,
                "latest_data_date": latest_date.date() if latest_date else None,
                "data_coverage": {
                    "has_data": active_stocks > 0,
                    "coverage_ratio": active_stocks / max(total_stocks, 1)
                },
                "top_sectors": [
                    {"sector": sector.sector, "count": sector.count}
                    for sector in sectors
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting market overview: {e}")
            # Return default values
            return {
                "total_stocks": 0,
                "active_stocks": 0,
                "latest_data_date": None,
                "data_coverage": {"has_data": False, "coverage_ratio": 0},
                "top_sectors": []
            }
    
    async def search_stocks(self, query: str, limit: int = 20) -> List[Dict]:
        """Search stocks by symbol or name"""
        try:
            # Search in database first
            db_results = self.db.query(StockInfo).filter(
                or_(
                    StockInfo.symbol.ilike(f"%{query}%"),
                    StockInfo.name.ilike(f"%{query}%")
                )
            ).filter(StockInfo.is_active == True).limit(limit).all()
            
            if db_results:
                return [
                    {
                        "symbol": stock.symbol,
                        "name": stock.name,
                        "market": stock.market,
                        "sector": stock.sector,
                        "industry": stock.industry
                    }
                    for stock in db_results
                ]
            
            # Fallback to basic search
            # This is a simplified version - in production, would use fuzzy matching
            return [
                {"symbol": "005930", "name": "삼성전자", "market": "KOSPI", "sector": "기술주", "industry": "반도체"}
            ] if query.lower() in ["005930", "삼성전자", "samsung"] else []
            
        except Exception as e:
            logger.error(f"Error searching stocks: {e}")
            return []