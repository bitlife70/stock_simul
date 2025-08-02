#!/usr/bin/env python3
"""
Korean Stock Data Manager - 배치 다운로드 및 로컬 DB 관리 시스템
실제 한국 주식시장 전체 종목을 일일 배치로 다운로드하여 로컬 SQLite DB에 저장
"""

import sqlite3
import pandas as pd
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging
import asyncio
import time
from typing import List, Dict, Optional
import hashlib

# 외부 라이브러리 (필요시 설치: pip install FinanceDataReader pykrx yfinance)
try:
    import FinanceDataReader as fdr
    import pykrx.stock as stock
    EXTERNAL_APIS_AVAILABLE = True
except ImportError:
    EXTERNAL_APIS_AVAILABLE = False
    print("⚠️  FinanceDataReader, pykrx not installed. Using fallback data.")

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KoreanStockDataManager:
    """한국 주식 데이터 관리자 - 배치 다운로드 및 로컬 DB 관리"""
    
    def __init__(self, db_path: str = "korean_stocks.db"):
        self.db_path = db_path
        self.data_dir = Path("stock_data")
        self.data_dir.mkdir(exist_ok=True)
        self.init_database()
        
    def init_database(self):
        """SQLite 데이터베이스 초기화"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 종목 기본정보 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stocks (
                    symbol TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    name_kr TEXT NOT NULL,
                    market TEXT NOT NULL,
                    sector TEXT,
                    industry TEXT,
                    market_cap BIGINT,
                    current_price INTEGER,
                    change_rate REAL,
                    volume BIGINT,
                    trading_value BIGINT,
                    listed_date TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 업데이트 이력 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS update_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    update_type TEXT NOT NULL,
                    total_stocks INTEGER,
                    success_count INTEGER,
                    error_count INTEGER,
                    data_hash TEXT,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    status TEXT DEFAULT 'running'
                )
            """)
            
            # 인덱스 생성
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_stocks_market ON stocks(market)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_stocks_sector ON stocks(sector)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_stocks_name_kr ON stocks(name_kr)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_stocks_market_cap ON stocks(market_cap DESC)")
            
            conn.commit()
            logger.info(f"✅ Database initialized: {self.db_path}")

    async def download_all_korean_stocks(self) -> Dict:
        """모든 한국 주식 데이터를 배치 다운로드"""
        start_time = datetime.now()
        logger.info("🚀 Started downloading all Korean stock data...")
        
        # 업데이트 기록 시작
        update_id = self._start_update_record("daily_batch")
        
        try:
            all_stocks = []
            
            if EXTERNAL_APIS_AVAILABLE:
                # 1. KOSPI 종목 다운로드
                logger.info("📊 Downloading KOSPI stocks...")
                kospi_stocks = await self._download_kospi_stocks()
                all_stocks.extend(kospi_stocks)
                
                # 2. KOSDAQ 종목 다운로드  
                logger.info("📈 Downloading KOSDAQ stocks...")
                kosdaq_stocks = await self._download_kosdaq_stocks()
                all_stocks.extend(kosdaq_stocks)
                
                # 3. ETF 다운로드 (옵션)
                logger.info("🎯 Downloading major ETFs...")
                etf_stocks = await self._download_etf_stocks()
                all_stocks.extend(etf_stocks)
                
            else:
                # Fallback: 확장된 하드코딩 데이터 사용
                logger.info("📋 Using extended fallback stock data...")
                all_stocks = self._get_extended_fallback_data()
            
            # 4. 데이터베이스에 저장
            success_count = await self._save_stocks_to_db(all_stocks)
            
            # 5. 업데이트 완료 기록
            end_time = datetime.now()
            data_hash = self._calculate_data_hash(all_stocks)
            self._complete_update_record(update_id, len(all_stocks), success_count, 0, data_hash, end_time)
            
            duration = (end_time - start_time).total_seconds()
            
            result = {
                "status": "success",
                "total_stocks": len(all_stocks),
                "success_count": success_count,
                "duration_seconds": duration,
                "timestamp": end_time.isoformat(),
                "data_hash": data_hash
            }
            
            logger.info(f"✅ Download completed: {len(all_stocks)} stocks in {duration:.1f}s")
            return result
            
        except Exception as e:
            # 에러 기록
            self._complete_update_record(update_id, 0, 0, 1, None, datetime.now(), "error")
            logger.error(f"❌ Download failed: {str(e)}")
            raise

    async def _download_kospi_stocks(self) -> List[Dict]:
        """KOSPI 전체 종목 다운로드"""
        stocks = []
        
        try:
            # pykrx로 KOSPI 종목 리스트 가져오기
            today = datetime.now().strftime('%Y%m%d')
            kospi_list = stock.get_market_ticker_list(today, market="KOSPI")
            
            logger.info(f"📊 Found {len(kospi_list)} KOSPI stocks")
            
            # 배치 처리로 종목 정보 수집
            batch_size = 50
            for i in range(0, len(kospi_list), batch_size):
                batch = kospi_list[i:i + batch_size]
                batch_stocks = await self._process_stock_batch(batch, "KOSPI", today)
                stocks.extend(batch_stocks)
                
                # API 레이트 리미트 방지
                await asyncio.sleep(0.1)
                
                if i % 200 == 0:
                    logger.info(f"📊 KOSPI progress: {i + len(batch)}/{len(kospi_list)}")
            
        except Exception as e:
            logger.error(f"❌ KOSPI download error: {str(e)}")
            # Fallback to known major KOSPI stocks
            stocks = self._get_major_kospi_fallback()
        
        return stocks

    async def _download_kosdaq_stocks(self) -> List[Dict]:
        """KOSDAQ 전체 종목 다운로드"""
        stocks = []
        
        try:
            # pykrx로 KOSDAQ 종목 리스트 가져오기
            today = datetime.now().strftime('%Y%m%d')
            kosdaq_list = stock.get_market_ticker_list(today, market="KOSDAQ")
            
            logger.info(f"📈 Found {len(kosdaq_list)} KOSDAQ stocks")
            
            # 배치 처리로 종목 정보 수집
            batch_size = 50
            for i in range(0, len(kosdaq_list), batch_size):
                batch = kosdaq_list[i:i + batch_size]
                batch_stocks = await self._process_stock_batch(batch, "KOSDAQ", today)
                stocks.extend(batch_stocks)
                
                # API 레이트 리미트 방지
                await asyncio.sleep(0.1)
                
                if i % 200 == 0:
                    logger.info(f"📈 KOSDAQ progress: {i + len(batch)}/{len(kosdaq_list)}")
            
        except Exception as e:
            logger.error(f"❌ KOSDAQ download error: {str(e)}")
            # Fallback to known major KOSDAQ stocks
            stocks = self._get_major_kosdaq_fallback()
        
        return stocks

    async def _download_etf_stocks(self) -> List[Dict]:
        """주요 ETF 다운로드 (현재는 스킵 - API 이슈로 인해)"""
        stocks = []
        
        try:
            # ETF는 현재 API 이슈로 인해 스킵
            logger.info("🎯 Skipping ETF download due to API compatibility issues")
            
            # 수동으로 주요 ETF 추가 (fallback 데이터)
            major_etfs_data = [
                {"symbol": "069500", "name": "KODEX 200", "name_kr": "KODEX 200", "market": "ETF", "sector": "ETF", "market_cap": 10000000, "current_price": 30000},
                {"symbol": "114800", "name": "KODEX 인버스", "name_kr": "KODEX 인버스", "market": "ETF", "sector": "ETF", "market_cap": 1000000, "current_price": 5000},
                {"symbol": "122630", "name": "KODEX 레버리지", "name_kr": "KODEX 레버리지", "market": "ETF", "sector": "ETF", "market_cap": 800000, "current_price": 15000},
            ]
            
            for etf_data in major_etfs_data:
                stock_data = {
                    **etf_data,
                    "industry": "ETF",
                    "change_rate": 0.0,
                    "volume": 1000000,
                    "trading_value": etf_data["current_price"] * 1000000,
                    "listed_date": ""
                }
                stocks.append(stock_data)
            
        except Exception as e:
            logger.error(f"❌ ETF download error: {str(e)}")
        
        return stocks

    async def _process_stock_batch(self, tickers: List[str], market: str, date: str) -> List[Dict]:
        """종목 배치 처리"""
        stocks = []
        
        for ticker in tickers:
            try:
                # pykrx로 종목 기본 정보 가져오기
                stock_info = stock.get_market_ticker_name(ticker)
                
                # 시가총액 및 가격 정보
                try:
                    market_data = stock.get_market_cap_by_ticker(date, ticker)
                    if not market_data.empty:
                        price_data = market_data.iloc[0]
                        current_price = int(price_data['종가']) if pd.notna(price_data['종가']) else 0
                        market_cap = int(price_data['시가총액']) if pd.notna(price_data['시가총액']) else 0
                        volume = int(price_data['거래량']) if pd.notna(price_data['거래량']) else 0
                    else:
                        current_price = market_cap = volume = 0
                except Exception as e:
                    logger.warning(f"⚠️  Failed to get market data for {ticker}: {str(e)}")
                    current_price = market_cap = volume = 0
                
                # 업종 정보 (KOSPI만 지원)
                sector = ""
                try:
                    if market == "KOSPI":
                        sector_info = stock.get_market_ticker_and_name(date, market="KOSPI")
                        # 업종 매핑 (간단화)
                        sector = self._map_sector_by_ticker(ticker)
                except:
                    pass
                
                stock_data = {
                    "symbol": ticker,
                    "name": stock_info,
                    "name_kr": stock_info,
                    "market": market,
                    "sector": sector or self._map_sector_by_ticker(ticker),
                    "industry": "",
                    "market_cap": market_cap,
                    "current_price": current_price,
                    "change_rate": 0.0,  # 별도 API 호출 필요
                    "volume": volume,
                    "trading_value": current_price * volume if current_price and volume else 0,
                    "listed_date": ""
                }
                
                stocks.append(stock_data)
                
            except Exception as e:
                logger.warning(f"⚠️  Failed to process {ticker}: {str(e)}")
                continue
        
        return stocks

    def _map_sector_by_ticker(self, ticker: str) -> str:
        """종목코드 기반 업종 매핑 (간단화)"""
        sector_map = {
            # 대표 종목들의 업종 매핑
            "005930": "반도체", "000660": "반도체", "035420": "인터넷",
            "035720": "인터넷", "005380": "자동차", "051910": "화학",
            "068270": "바이오", "207940": "바이오", "006400": "배터리",
            "055550": "금융", "105560": "금융", "003670": "철강",
            "017670": "통신", "030200": "통신", "036570": "게임",
            "112040": "게임", "293490": "게임", "041510": "엔터테인먼트",
        }
        
        return sector_map.get(ticker, "기타")

    async def _save_stocks_to_db(self, stocks: List[Dict]) -> int:
        """종목 데이터를 데이터베이스에 저장"""
        success_count = 0
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 기존 데이터 삭제 (전체 교체)
            cursor.execute("DELETE FROM stocks")
            
            # 새 데이터 삽입
            for stock in stocks:
                try:
                    cursor.execute("""
                        INSERT INTO stocks (
                            symbol, name, name_kr, market, sector, industry,
                            market_cap, current_price, change_rate, volume,
                            trading_value, listed_date, last_updated
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        stock["symbol"], stock["name"], stock["name_kr"],
                        stock["market"], stock["sector"], stock["industry"],
                        stock["market_cap"], stock["current_price"], stock["change_rate"],
                        stock["volume"], stock["trading_value"], stock["listed_date"],
                        datetime.now().isoformat()
                    ))
                    success_count += 1
                except Exception as e:
                    logger.warning(f"⚠️  Failed to save {stock['symbol']}: {str(e)}")
            
            conn.commit()
        
        logger.info(f"💾 Saved {success_count} stocks to database")
        return success_count

    def _get_extended_fallback_data(self) -> List[Dict]:
        """확장된 폴백 데이터 (외부 API 없을 때)"""
        # 기존 74개에서 200개로 확장된 대표 종목 리스트
        from korean_stocks_data import get_all_korean_stocks
        return get_all_korean_stocks()

    def _get_major_kospi_fallback(self) -> List[Dict]:
        """KOSPI 주요 종목 폴백 데이터"""
        from korean_stocks_data import KOSPI_STOCKS
        return [{"market": "KOSPI", **stock} for stock in KOSPI_STOCKS]

    def _get_major_kosdaq_fallback(self) -> List[Dict]:
        """KOSDAQ 주요 종목 폴백 데이터"""
        from korean_stocks_data import KOSDAQ_STOCKS
        return [{"market": "KOSDAQ", **stock} for stock in KOSDAQ_STOCKS]

    def _start_update_record(self, update_type: str) -> int:
        """업데이트 기록 시작"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO update_history (update_type, started_at, status)
                VALUES (?, ?, 'running')
            """, (update_type, datetime.now().isoformat()))
            conn.commit()
            return cursor.lastrowid

    def _complete_update_record(self, update_id: int, total: int, success: int, 
                              errors: int, data_hash: str, completed_at: datetime, 
                              status: str = "completed"):
        """업데이트 기록 완료"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE update_history 
                SET total_stocks = ?, success_count = ?, error_count = ?,
                    data_hash = ?, completed_at = ?, status = ?
                WHERE id = ?
            """, (total, success, errors, data_hash, completed_at.isoformat(), status, update_id))
            conn.commit()

    def _calculate_data_hash(self, stocks: List[Dict]) -> str:
        """데이터 해시 계산 (변경사항 감지용)"""
        try:
            # DataFrame이나 기타 JSON 직렬화 불가능한 객체 제거
            clean_stocks = []
            for stock in stocks:
                clean_stock = {}
                for key, value in stock.items():
                    if isinstance(value, (str, int, float, bool)) or value is None:
                        clean_stock[key] = value
                    else:
                        # DataFrame이나 기타 복잡한 객체는 문자열로 변환
                        clean_stock[key] = str(value)
                clean_stocks.append(clean_stock)
            
            data_str = json.dumps(clean_stocks, sort_keys=True, ensure_ascii=False, default=str)
            return hashlib.md5(data_str.encode()).hexdigest()
        except Exception as e:
            logger.warning(f"⚠️  Hash calculation failed: {str(e)}")
            return hashlib.md5(f"fallback_{len(stocks)}_{datetime.now().isoformat()}".encode()).hexdigest()

    def get_all_stocks(self, limit: Optional[int] = None) -> List[Dict]:
        """로컬 DB에서 모든 종목 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM stocks ORDER BY market_cap DESC"
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query)
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def search_stocks(self, query: str, limit: int = 50) -> List[Dict]:
        """고속 종목 검색"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            search_query = f"%{query}%"
            cursor.execute("""
                SELECT * FROM stocks 
                WHERE symbol LIKE ? OR name_kr LIKE ? OR name LIKE ? OR sector LIKE ?
                ORDER BY 
                    CASE 
                        WHEN symbol = ? THEN 1
                        WHEN name_kr = ? THEN 2
                        WHEN symbol LIKE ? THEN 3
                        WHEN name_kr LIKE ? THEN 4
                        ELSE 5
                    END,
                    market_cap DESC
                LIMIT ?
            """, (search_query, search_query, search_query, search_query,
                  query, query, f"{query}%", f"{query}%", limit))
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_stats(self) -> Dict:
        """데이터베이스 통계"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM stocks")
            total_stocks = cursor.fetchone()[0]
            
            cursor.execute("SELECT market, COUNT(*) FROM stocks GROUP BY market")
            market_counts = dict(cursor.fetchall())
            
            cursor.execute("SELECT * FROM update_history ORDER BY completed_at DESC LIMIT 1")
            last_update = cursor.fetchone()
            
            return {
                "total_stocks": total_stocks,
                "market_breakdown": market_counts,
                "last_update": last_update[7] if last_update else None,
                "database_path": self.db_path
            }

    def should_update(self) -> bool:
        """업데이트 필요 여부 판단"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT completed_at FROM update_history 
                WHERE status = 'completed' 
                ORDER BY completed_at DESC LIMIT 1
            """)
            result = cursor.fetchone()
            
            if not result:
                return True  # 첫 업데이트
            
            last_update = datetime.fromisoformat(result[0])
            return (datetime.now() - last_update).days >= 1  # 하루 지났으면 업데이트

# 전역 인스턴스
stock_manager = KoreanStockDataManager()

async def daily_batch_update():
    """일일 배치 업데이트 실행"""
    if stock_manager.should_update():
        logger.info("🔄 Starting daily batch update...")
        result = await stock_manager.download_all_korean_stocks()
        logger.info(f"✅ Daily update completed: {result}")
        return result
    else:
        logger.info("⏭️  Skip update - data is current")
        return {"status": "skipped", "reason": "data_is_current"}

if __name__ == "__main__":
    import asyncio
    
    async def main():
        print("🚀 Korean Stock Data Manager")
        print("=" * 50)
        
        # 통계 출력
        stats = stock_manager.get_stats()
        print(f"📊 Current Stats:")
        print(f"  Total Stocks: {stats['total_stocks']}")
        print(f"  Markets: {stats['market_breakdown']}")
        print(f"  Last Update: {stats['last_update']}")
        print()
        
        # 업데이트 실행
        if len(sys.argv) > 1 and sys.argv[1] == "update":
            result = await daily_batch_update()
            print(f"🔄 Update Result: {result}")
        
        # 검색 테스트
        print("🔍 Search Test:")
        results = stock_manager.search_stocks("삼성", 5)
        for stock in results:
            print(f"  {stock['symbol']}: {stock['name_kr']} ({stock['market']})")
    
    import sys
    asyncio.run(main())