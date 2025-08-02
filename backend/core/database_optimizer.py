"""
Database Optimization Module
Optimized database operations for Korean stock market time-series data
"""

import asyncio
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from contextlib import asynccontextmanager
from dataclasses import dataclass
import numpy as np
import pandas as pd

from sqlalchemy import create_engine, text, Index, func, and_, or_
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool, QueuePool
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.dialects.postgresql import insert as postgresql_insert

from core.performance_config import get_performance_config
from models.stock_data import StockData
from models.strategy import Backtest, Trade, EquityCurve

logger = logging.getLogger(__name__)

@dataclass
class QueryPerformanceMetrics:
    """Query performance tracking"""
    query_type: str
    execution_time_ms: float
    rows_affected: int
    cache_hit: bool = False

class OptimizedDatabaseManager:
    """High-performance database manager for Korean market data"""
    
    def __init__(self):
        self.config = get_performance_config()
        self.sync_engine = None
        self.async_engine = None
        self.async_session_factory = None
        self.sync_session_factory = None
        
        # Performance tracking
        self.query_metrics: List[QueryPerformanceMetrics] = []
        self.connection_pool_stats = {
            'active_connections': 0,
            'total_connections': 0,
            'pool_hits': 0,
            'pool_misses': 0
        }
        
        self._initialize_engines()
        self._create_optimized_indexes()
        
    def _initialize_engines(self):
        """Initialize optimized database engines"""
        database_url = "sqlite:///./stock_backtesting_optimized.db"
        
        # Sync engine with connection pooling
        self.sync_engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=self.config.connection_pool_size,
            max_overflow=self.config.connection_pool_max_overflow,
            pool_pre_ping=True,
            pool_recycle=3600,  # Recycle connections every hour
            echo=False  # Set to True for SQL debugging
        )
        
        # Async engine for concurrent operations
        async_database_url = database_url.replace("sqlite://", "sqlite+aiosqlite://")
        self.async_engine = create_async_engine(
            async_database_url,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
            echo=False
        )
        
        # Session factories
        self.sync_session_factory = sessionmaker(
            bind=self.sync_engine,
            expire_on_commit=False
        )
        
        self.async_session_factory = async_sessionmaker(
            bind=self.async_engine,
            expire_on_commit=False,
            class_=AsyncSession
        )
        
        logger.info("Database engines initialized with connection pooling")
    
    def _create_optimized_indexes(self):
        """Create optimized indexes for time-series queries"""
        try:
            with self.sync_engine.connect() as conn:
                # Optimized indexes for Korean market data
                indexes = [
                    "CREATE INDEX IF NOT EXISTS idx_stock_data_symbol_date ON stock_data(symbol, date DESC)",
                    "CREATE INDEX IF NOT EXISTS idx_stock_data_date_volume ON stock_data(date, volume DESC)",
                    "CREATE INDEX IF NOT EXISTS idx_stock_data_market_cap ON stock_data(symbol, market_cap DESC)",
                    "CREATE INDEX IF NOT EXISTS idx_trades_backtest_symbol ON trades(backtest_id, symbol, entry_date)",
                    "CREATE INDEX IF NOT EXISTS idx_equity_curve_backtest_date ON equity_curve(backtest_id, date)",
                    "CREATE INDEX IF NOT EXISTS idx_backtest_status_created ON backtests(status, created_at DESC)",
                    
                    # Korean market specific indexes
                    "CREATE INDEX IF NOT EXISTS idx_stock_data_korean_symbols ON stock_data(symbol) WHERE symbol LIKE '%'",
                    "CREATE INDEX IF NOT EXISTS idx_stock_data_kospi_volume ON stock_data(symbol, volume) WHERE symbol < '900000'",
                    "CREATE INDEX IF NOT EXISTS idx_stock_data_kosdaq_volume ON stock_data(symbol, volume) WHERE symbol >= '900000'",
                ]
                
                for index_sql in indexes:
                    conn.execute(text(index_sql))
                conn.commit()
                
            logger.info("Optimized database indexes created")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    @asynccontextmanager
    async def get_async_session(self):
        """Get async database session with proper cleanup"""
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    @asynccontextmanager
    def get_sync_session(self):
        """Get sync database session with proper cleanup"""
        session = self.sync_session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    async def bulk_insert_stock_data(self, stock_data_list: List[Dict]) -> int:
        """Optimized bulk insert for stock data"""
        if not stock_data_list:
            return 0
        
        start_time = datetime.now()
        
        try:
            async with self.get_async_session() as session:
                # Batch insert in chunks
                batch_size = self.config.bulk_insert_batch_size
                total_inserted = 0
                
                for i in range(0, len(stock_data_list), batch_size):
                    batch = stock_data_list[i:i + batch_size]
                    
                    # Use bulk insert for better performance
                    stmt = sqlite_insert(StockData).values(batch)
                    # Handle conflicts (upsert)
                    stmt = stmt.on_conflict_do_update(
                        index_elements=['symbol', 'date'],
                        set_={
                            'open_price': stmt.excluded.open_price,
                            'high_price': stmt.excluded.high_price,
                            'low_price': stmt.excluded.low_price,
                            'close_price': stmt.excluded.close_price,
                            'volume': stmt.excluded.volume,
                            'market_cap': stmt.excluded.market_cap,
                            'updated_at': func.now()
                        }
                    )
                    
                    result = await session.execute(stmt)
                    total_inserted += len(batch)
                    
                    # Commit in batches to avoid memory issues
                    await session.commit()
                
                # Record performance metrics
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                self.query_metrics.append(QueryPerformanceMetrics(
                    query_type="bulk_insert_stock_data",
                    execution_time_ms=execution_time,
                    rows_affected=total_inserted
                ))
                
                logger.info(f"Bulk inserted {total_inserted} stock data records in {execution_time:.2f}ms")
                return total_inserted
                
        except Exception as e:
            logger.error(f"Bulk insert failed: {e}")
            raise
    
    async def get_stock_data_optimized(
        self, 
        symbols: List[str], 
        start_date: date, 
        end_date: date,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """Optimized stock data retrieval with caching"""
        start_time = datetime.now()
        
        try:
            async with self.get_async_session() as session:
                # Optimized query with proper indexing
                query = session.query(StockData).filter(
                    and_(
                        StockData.symbol.in_(symbols),
                        StockData.date >= start_date,
                        StockData.date <= end_date
                    )
                ).order_by(StockData.symbol, StockData.date.desc())
                
                if limit:
                    query = query.limit(limit)
                
                # Execute query
                result = await session.execute(query)
                rows = result.fetchall()
                
                # Convert to DataFrame for analysis
                if rows:
                    data = []
                    for row in rows:
                        data.append({
                            'symbol': row.symbol,
                            'date': row.date,
                            'open': row.open_price,
                            'high': row.high_price,
                            'low': row.low_price,
                            'close': row.close_price,
                            'volume': row.volume,
                            'market_cap': row.market_cap
                        })
                    
                    df = pd.DataFrame(data)
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.set_index(['symbol', 'date']).sort_index()
                else:
                    df = pd.DataFrame()
                
                # Record performance metrics
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                self.query_metrics.append(QueryPerformanceMetrics(
                    query_type="get_stock_data_optimized",
                    execution_time_ms=execution_time,
                    rows_affected=len(rows) if rows else 0
                ))
                
                logger.debug(f"Retrieved {len(rows) if rows else 0} stock data records in {execution_time:.2f}ms")
                return df
                
        except Exception as e:
            logger.error(f"Stock data retrieval failed: {e}")
            raise
    
    async def get_korean_market_data_batch(
        self, 
        symbols: List[str], 
        date: date,
        include_indicators: bool = False
    ) -> Dict[str, Dict]:
        """Optimized batch retrieval for Korean market data"""
        start_time = datetime.now()
        
        try:
            async with self.get_async_session() as session:
                # Optimized query for single date, multiple symbols
                query = text("""
                    SELECT symbol, date, open_price, high_price, low_price, 
                           close_price, volume, market_cap
                    FROM stock_data 
                    WHERE symbol IN :symbols 
                    AND date = :date
                    ORDER BY symbol
                """)
                
                result = await session.execute(
                    query, 
                    {"symbols": tuple(symbols), "date": date}
                )
                rows = result.fetchall()
                
                # Structure data for backtesting
                market_data = {}
                for row in rows:
                    symbol = row.symbol
                    market_data[symbol] = {
                        'date': row.date,
                        'open': row.open_price,
                        'high': row.high_price,
                        'low': row.low_price,
                        'close': row.close_price,
                        'volume': row.volume,
                        'market_cap': row.market_cap
                    }
                    
                    # Add Korean market specific calculations
                    if include_indicators:
                        market_data[symbol].update(
                            await self._calculate_korean_indicators(symbol, row)
                        )
                
                # Record performance metrics
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                self.query_metrics.append(QueryPerformanceMetrics(
                    query_type="get_korean_market_data_batch",
                    execution_time_ms=execution_time,
                    rows_affected=len(rows)
                ))
                
                logger.debug(f"Retrieved Korean market data for {len(market_data)} symbols in {execution_time:.2f}ms")
                return market_data
                
        except Exception as e:
            logger.error(f"Korean market data batch retrieval failed: {e}")
            return {}
    
    async def _calculate_korean_indicators(self, symbol: str, row) -> Dict:
        """Calculate Korean market specific indicators"""
        indicators = {}
        
        try:
            # Price limit calculations (상한가/하한가)
            prev_close = row.close_price  # Simplified - would get from previous day
            upper_limit = prev_close * 1.30  # 30% limit for most stocks
            lower_limit = prev_close * 0.70  # -30% limit
            
            if symbol.startswith('2'):  # ETF different limits
                upper_limit = prev_close * 1.10
                lower_limit = prev_close * 0.90
            
            indicators.update({
                'upper_price_limit': upper_limit,
                'lower_price_limit': lower_limit,
                'distance_to_upper_limit': (upper_limit - row.close_price) / row.close_price,
                'distance_to_lower_limit': (row.close_price - lower_limit) / row.close_price,
                'is_near_upper_limit': abs(row.close_price - upper_limit) / row.close_price < 0.02,
                'is_near_lower_limit': abs(row.close_price - lower_limit) / row.close_price < 0.02
            })
            
            # Market classification
            if symbol < '900000':
                indicators['market'] = 'KOSPI'
                indicators['market_tier'] = 'large_cap' if row.market_cap > 1000000000000 else 'mid_cap'
            else:
                indicators['market'] = 'KOSDAQ'
                indicators['market_tier'] = 'growth' if row.market_cap > 100000000000 else 'small_cap'
            
            # Volume analysis optimized for Korean patterns
            avg_volume = row.volume  # Simplified - would calculate 20-day average
            indicators.update({
                'volume_ratio': row.volume / max(avg_volume, 1),
                'is_volume_surge': row.volume > avg_volume * 3,
                'volume_tier': 'high' if row.volume > avg_volume * 2 else 'normal'
            })
            
        except Exception as e:
            logger.debug(f"Error calculating Korean indicators for {symbol}: {e}")
        
        return indicators
    
    async def save_backtest_results_optimized(
        self, 
        backtest_id: str, 
        trades: List[Dict], 
        equity_curve: List[Dict]
    ) -> bool:
        """Optimized saving of backtest results"""
        start_time = datetime.now()
        
        try:
            async with self.get_async_session() as session:
                # Bulk insert trades
                if trades:
                    trade_batch_size = min(500, len(trades))
                    for i in range(0, len(trades), trade_batch_size):
                        batch = trades[i:i + trade_batch_size]
                        trade_objects = [Trade(**trade_data) for trade_data in batch]
                        session.add_all(trade_objects)
                        await session.flush()
                
                # Bulk insert equity curve
                if equity_curve:
                    equity_batch_size = min(1000, len(equity_curve))
                    for i in range(0, len(equity_curve), equity_batch_size):
                        batch = equity_curve[i:i + equity_batch_size]
                        equity_objects = [EquityCurve(**eq_data) for eq_data in batch]
                        session.add_all(equity_objects)
                        await session.flush()
                
                await session.commit()
                
                # Record performance metrics
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                self.query_metrics.append(QueryPerformanceMetrics(
                    query_type="save_backtest_results",
                    execution_time_ms=execution_time,
                    rows_affected=len(trades) + len(equity_curve)
                ))
                
                logger.info(f"Saved backtest results ({len(trades)} trades, {len(equity_curve)} equity points) in {execution_time:.2f}ms")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save backtest results: {e}")
            return False
    
    async def get_performance_analytics(self) -> Dict[str, Any]:
        """Get database performance analytics"""
        # Calculate average query times by type
        query_stats = {}
        for metric in self.query_metrics[-1000:]:  # Last 1000 queries
            if metric.query_type not in query_stats:
                query_stats[metric.query_type] = {
                    'count': 0,
                    'total_time': 0,
                    'total_rows': 0
                }
            
            stats = query_stats[metric.query_type]
            stats['count'] += 1
            stats['total_time'] += metric.execution_time_ms
            stats['total_rows'] += metric.rows_affected
        
        # Calculate averages
        for query_type, stats in query_stats.items():
            stats['avg_time_ms'] = stats['total_time'] / stats['count']
            stats['avg_rows'] = stats['total_rows'] / stats['count']
        
        # Get connection pool stats
        try:
            pool = self.sync_engine.pool
            pool_stats = {
                'pool_size': pool.size(),
                'checked_in': pool.checkedin(),
                'checked_out': pool.checkedout(),
                'overflow': pool.overflow(),
                'invalid': pool.invalid()
            }
        except:
            pool_stats = {"error": "Unable to get pool stats"}
        
        return {
            'query_performance': query_stats,
            'connection_pool': pool_stats,
            'total_queries': len(self.query_metrics),
            'average_query_time_ms': np.mean([m.execution_time_ms for m in self.query_metrics[-100:]]) if self.query_metrics else 0
        }
    
    async def optimize_database_maintenance(self) -> Dict[str, Any]:
        """Perform database optimization maintenance"""
        maintenance_results = {}
        
        try:
            async with self.get_async_session() as session:
                # Analyze tables for optimization
                maintenance_results['analyze'] = await session.execute(text("ANALYZE"))
                
                # Vacuum database (SQLite specific)
                maintenance_results['vacuum'] = await session.execute(text("VACUUM"))
                
                # Update statistics
                maintenance_results['updated_stats'] = await session.execute(
                    text("UPDATE sqlite_stat1 SET stat = stat WHERE 1=0")
                )
                
                await session.commit()
                
            logger.info("Database maintenance completed")
            
        except Exception as e:
            logger.error(f"Database maintenance failed: {e}")
            maintenance_results['error'] = str(e)
        
        return maintenance_results

# Global database manager instance
db_manager = OptimizedDatabaseManager()

async def get_database_manager() -> OptimizedDatabaseManager:
    """Get the global database manager instance"""
    return db_manager