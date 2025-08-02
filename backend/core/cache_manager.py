"""
Advanced Multi-Level Cache Manager
Implements hybrid caching strategy for Korean stock market data
"""

import asyncio
import hashlib
import json
import pickle
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import asyncio

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

import pandas as pd
from core.performance_config import get_performance_config

logger = logging.getLogger(__name__)

@dataclass
class CacheStats:
    """Cache performance statistics"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    memory_usage_mb: float = 0.0
    average_access_time_ms: float = 0.0

class MemoryCache:
    """High-performance in-memory cache with LRU eviction"""
    
    def __init__(self, max_size_mb: int = 1000):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.cache: Dict[str, Dict] = {}
        self.access_times: Dict[str, datetime] = {}
        self.stats = CacheStats()
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get item from memory cache"""
        start_time = datetime.now()
        
        async with self._lock:
            if key in self.cache:
                self.access_times[key] = datetime.now()
                self.stats.hits += 1
                result = self.cache[key]['data']
            else:
                self.stats.misses += 1
                result = None
        
        # Update average access time
        access_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        self.stats.average_access_time_ms = (
            (self.stats.average_access_time_ms * (self.stats.hits + self.stats.misses - 1) + access_time_ms) /
            (self.stats.hits + self.stats.misses)
        )
        
        return result
    
    async def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        """Set item in memory cache with TTL"""
        async with self._lock:
            # Calculate memory usage
            serialized_size = len(pickle.dumps(value))
            
            # Evict if necessary
            await self._evict_if_needed(serialized_size)
            
            # Store item
            expiry_time = datetime.now() + timedelta(seconds=ttl_seconds)
            self.cache[key] = {
                'data': value,
                'expiry': expiry_time,
                'size': serialized_size
            }
            self.access_times[key] = datetime.now()
            
            # Update memory usage
            self._update_memory_usage()
    
    async def delete(self, key: str) -> bool:
        """Delete item from memory cache"""
        async with self._lock:
            if key in self.cache:
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]
                self._update_memory_usage()
                return True
            return False
    
    async def clear_expired(self) -> int:
        """Clear expired items and return count"""
        now = datetime.now()
        expired_keys = []
        
        async with self._lock:
            for key, item in self.cache.items():
                if item['expiry'] < now:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]
            
            if expired_keys:
                self._update_memory_usage()
        
        return len(expired_keys)
    
    async def _evict_if_needed(self, new_item_size: int) -> None:
        """Evict LRU items if memory limit would be exceeded"""
        current_size = sum(item['size'] for item in self.cache.values())
        
        while current_size + new_item_size > self.max_size_bytes and self.cache:
            # Find LRU item
            lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            
            # Remove LRU item
            if lru_key in self.cache:
                current_size -= self.cache[lru_key]['size']
                del self.cache[lru_key]
                del self.access_times[lru_key]
                self.stats.evictions += 1
    
    def _update_memory_usage(self) -> None:
        """Update memory usage statistics"""
        total_size = sum(item['size'] for item in self.cache.values())
        self.stats.memory_usage_mb = total_size / (1024 * 1024)

class KoreanMarketCacheManager:
    """Advanced cache manager optimized for Korean market data"""
    
    def __init__(self):
        self.config = get_performance_config()
        self.memory_cache = MemoryCache(self.config.memory_cache_size)
        self.redis_client: Optional[redis.Redis] = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._initialize_redis()
        
        # Korean market specific caches
        self.price_limit_cache = {}  # 상한가/하한가 cache
        self.chaebol_correlation_cache = {}  # 재벌 그룹 연관성 cache
        self.technical_indicator_cache = {}  # 기술적 지표 cache
        
        logger.info("Korean Market Cache Manager initialized")
    
    def _initialize_redis(self) -> None:
        """Initialize Redis connection if available"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available, using memory cache only")
            return
        
        try:
            self.redis_client = redis.from_url(
                "redis://localhost:6379/0",
                encoding="utf-8",
                decode_responses=False,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            logger.info("Redis cache initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            self.redis_client = None
    
    async def get_market_data(self, symbol: str, date_range: tuple, indicators: List[str] = None) -> Optional[pd.DataFrame]:
        """Get cached market data with indicators"""
        cache_key = self._generate_market_data_key(symbol, date_range, indicators)
        
        # Try memory cache first
        data = await self.memory_cache.get(cache_key)
        if data is not None:
            logger.debug(f"Market data cache hit (memory): {symbol}")
            return data
        
        # Try Redis cache
        if self.redis_client:
            try:
                cached_data = await self.redis_client.get(cache_key)
                if cached_data:
                    data = pickle.loads(cached_data)
                    # Store in memory cache for faster access
                    await self.memory_cache.set(cache_key, data, self.config.cache_ttl_market_data)
                    logger.debug(f"Market data cache hit (Redis): {symbol}")
                    return data
            except Exception as e:
                logger.error(f"Redis get error: {e}")
        
        logger.debug(f"Market data cache miss: {symbol}")
        return None
    
    async def set_market_data(self, symbol: str, date_range: tuple, data: pd.DataFrame, indicators: List[str] = None) -> None:
        """Cache market data with indicators"""
        cache_key = self._generate_market_data_key(symbol, date_range, indicators)
        
        # Store in memory cache
        await self.memory_cache.set(cache_key, data, self.config.cache_ttl_market_data)
        
        # Store in Redis cache
        if self.redis_client:
            try:
                serialized_data = pickle.dumps(data)
                await self.redis_client.setex(
                    cache_key, 
                    self.config.cache_ttl_market_data, 
                    serialized_data
                )
                logger.debug(f"Market data cached: {symbol}")
            except Exception as e:
                logger.error(f"Redis set error: {e}")
    
    async def get_technical_indicators(self, symbol: str, indicator_name: str, parameters: Dict) -> Optional[pd.Series]:
        """Get cached technical indicators"""
        cache_key = self._generate_indicator_key(symbol, indicator_name, parameters)
        
        # Check technical indicator cache
        if cache_key in self.technical_indicator_cache:
            cache_entry = self.technical_indicator_cache[cache_key]
            if cache_entry['expiry'] > datetime.now():
                logger.debug(f"Technical indicator cache hit: {indicator_name} for {symbol}")
                return cache_entry['data']
        
        return None
    
    async def set_technical_indicators(self, symbol: str, indicator_name: str, parameters: Dict, data: pd.Series) -> None:
        """Cache technical indicators"""
        cache_key = self._generate_indicator_key(symbol, indicator_name, parameters)
        
        self.technical_indicator_cache[cache_key] = {
            'data': data,
            'expiry': datetime.now() + timedelta(seconds=self.config.cache_ttl_indicators)
        }
        
        logger.debug(f"Technical indicator cached: {indicator_name} for {symbol}")
    
    async def get_korean_price_limits(self, symbol: str, date: str) -> Optional[Dict]:
        """Get cached Korean price limit data (상한가/하한가)"""
        cache_key = f"price_limits:{symbol}:{date}"
        
        if cache_key in self.price_limit_cache:
            cache_entry = self.price_limit_cache[cache_key]
            if cache_entry['expiry'] > datetime.now():
                return cache_entry['data']
        
        return None
    
    async def set_korean_price_limits(self, symbol: str, date: str, limits: Dict) -> None:
        """Cache Korean price limit data"""
        cache_key = f"price_limits:{symbol}:{date}"
        
        self.price_limit_cache[cache_key] = {
            'data': limits,
            'expiry': datetime.now() + timedelta(seconds=self.config.cache_ttl_market_data)
        }
        
        # Maintain cache size limit
        if len(self.price_limit_cache) > self.config.price_limit_cache_size:
            # Remove oldest entries
            oldest_keys = sorted(
                self.price_limit_cache.keys(),
                key=lambda k: self.price_limit_cache[k]['expiry']
            )[:100]
            
            for key in oldest_keys:
                del self.price_limit_cache[key]
    
    async def get_chaebol_correlations(self, symbol: str) -> Optional[Dict]:
        """Get cached chaebol group correlation data"""
        cache_key = f"chaebol_corr:{symbol}"
        
        if cache_key in self.chaebol_correlation_cache:
            cache_entry = self.chaebol_correlation_cache[cache_key]
            if cache_entry['expiry'] > datetime.now():
                return cache_entry['data']
        
        return None
    
    async def set_chaebol_correlations(self, symbol: str, correlations: Dict) -> None:
        """Cache chaebol group correlation data"""
        cache_key = f"chaebol_corr:{symbol}"
        
        self.chaebol_correlation_cache[cache_key] = {
            'data': correlations,
            'expiry': datetime.now() + timedelta(seconds=self.config.chaebol_correlation_cache_ttl)
        }
    
    async def invalidate_symbol_cache(self, symbol: str) -> None:
        """Invalidate all cached data for a symbol"""
        # Memory cache - remove keys containing symbol
        keys_to_remove = [key for key in self.memory_cache.cache.keys() if symbol in key]
        for key in keys_to_remove:
            await self.memory_cache.delete(key)
        
        # Technical indicators cache
        keys_to_remove = [key for key in self.technical_indicator_cache.keys() if symbol in key]
        for key in keys_to_remove:
            del self.technical_indicator_cache[key]
        
        # Price limits cache
        keys_to_remove = [key for key in self.price_limit_cache.keys() if symbol in key]
        for key in keys_to_remove:
            del self.price_limit_cache[key]
        
        # Chaebol correlations cache
        keys_to_remove = [key for key in self.chaebol_correlation_cache.keys() if symbol in key]
        for key in keys_to_remove:
            del self.chaebol_correlation_cache[key]
        
        logger.info(f"Cache invalidated for symbol: {symbol}")
    
    async def cleanup_expired_caches(self) -> Dict[str, int]:
        """Clean up expired cache entries"""
        cleanup_stats = {
            'memory_cache': await self.memory_cache.clear_expired(),
            'technical_indicators': 0,
            'price_limits': 0,
            'chaebol_correlations': 0
        }
        
        # Clean technical indicators cache
        now = datetime.now()
        expired_keys = [
            key for key, entry in self.technical_indicator_cache.items()
            if entry['expiry'] < now
        ]
        for key in expired_keys:
            del self.technical_indicator_cache[key]
        cleanup_stats['technical_indicators'] = len(expired_keys)
        
        # Clean price limits cache
        expired_keys = [
            key for key, entry in self.price_limit_cache.items()
            if entry['expiry'] < now
        ]
        for key in expired_keys:
            del self.price_limit_cache[key]
        cleanup_stats['price_limits'] = len(expired_keys)
        
        # Clean chaebol correlations cache
        expired_keys = [
            key for key, entry in self.chaebol_correlation_cache.items()
            if entry['expiry'] < now
        ]
        for key in expired_keys:
            del self.chaebol_correlation_cache[key]
        cleanup_stats['chaebol_correlations'] = len(expired_keys)
        
        return cleanup_stats
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        return {
            'memory_cache': {
                'hits': self.memory_cache.stats.hits,
                'misses': self.memory_cache.stats.misses,
                'hit_rate': self.memory_cache.stats.hits / max(1, self.memory_cache.stats.hits + self.memory_cache.stats.misses),
                'evictions': self.memory_cache.stats.evictions,
                'memory_usage_mb': self.memory_cache.stats.memory_usage_mb,
                'average_access_time_ms': self.memory_cache.stats.average_access_time_ms,
                'total_items': len(self.memory_cache.cache)
            },
            'technical_indicators_cache': {
                'total_items': len(self.technical_indicator_cache)
            },
            'price_limits_cache': {
                'total_items': len(self.price_limit_cache)
            },
            'chaebol_correlations_cache': {
                'total_items': len(self.chaebol_correlation_cache)
            }
        }
    
    def _generate_market_data_key(self, symbol: str, date_range: tuple, indicators: List[str] = None) -> str:
        """Generate cache key for market data"""
        key_parts = [
            f"market_data",
            symbol,
            f"{date_range[0]}_{date_range[1]}"
        ]
        
        if indicators:
            indicators_str = "_".join(sorted(indicators))
            key_parts.append(indicators_str)
        
        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _generate_indicator_key(self, symbol: str, indicator_name: str, parameters: Dict) -> str:
        """Generate cache key for technical indicators"""
        params_str = json.dumps(parameters, sort_keys=True)
        key_string = f"indicator:{symbol}:{indicator_name}:{params_str}"
        return hashlib.md5(key_string.encode()).hexdigest()

# Global cache manager instance
cache_manager = KoreanMarketCacheManager()

async def get_cache_manager() -> KoreanMarketCacheManager:
    """Get the global cache manager instance"""
    return cache_manager