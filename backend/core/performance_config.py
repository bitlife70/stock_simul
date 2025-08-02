"""
Performance Configuration Module
Centralized configuration for performance optimizations
"""

import os
from typing import Dict, Any
from dataclasses import dataclass
from enum import Enum

class CacheStrategy(Enum):
    MEMORY = "memory"
    REDIS = "redis"
    DISK = "disk"
    HYBRID = "hybrid"

class ProcessingMode(Enum):
    SYNC = "sync"
    ASYNC = "async"
    PARALLEL = "parallel"
    DISTRIBUTED = "distributed"

@dataclass
class PerformanceConfig:
    """Performance configuration settings"""
    
    # Caching Configuration
    cache_strategy: CacheStrategy = CacheStrategy.HYBRID
    memory_cache_size: int = 1000  # MB
    redis_max_memory: str = "2gb"
    cache_ttl_market_data: int = 300  # 5 minutes
    cache_ttl_indicators: int = 1800  # 30 minutes
    cache_ttl_backtest_results: int = 3600  # 1 hour
    
    # Database Optimization
    connection_pool_size: int = 20
    connection_pool_max_overflow: int = 30
    query_timeout: int = 30
    bulk_insert_batch_size: int = 1000
    
    # Processing Configuration
    processing_mode: ProcessingMode = ProcessingMode.ASYNC
    max_concurrent_backtests: int = 5
    max_worker_threads: int = 8
    chunk_size_large_datasets: int = 10000
    
    # Memory Management
    max_memory_usage_mb: int = 4000
    gc_threshold: int = 1000
    preload_common_indicators: bool = True
    
    # Korean Market Specific
    korean_market_hours: Dict[str, str] = None
    price_limit_cache_size: int = 2000
    chaebol_correlation_cache_ttl: int = 1800
    
    # Monitoring
    enable_performance_monitoring: bool = True
    metrics_collection_interval: int = 60
    alert_threshold_response_time: float = 2.0
    alert_threshold_memory_usage: float = 0.85
    
    def __post_init__(self):
        if self.korean_market_hours is None:
            self.korean_market_hours = {
                "market_open": "09:00",
                "market_close": "15:30",
                "lunch_break_start": "11:30",
                "lunch_break_end": "12:30",
                "pre_market_start": "08:00",
                "after_hours_end": "18:00"
            }

# Global performance configuration instance
perf_config = PerformanceConfig()

# Environment-based configuration overrides
if os.getenv("ENVIRONMENT") == "production":
    perf_config.memory_cache_size = 2000
    perf_config.max_concurrent_backtests = 10
    perf_config.max_worker_threads = 16
    perf_config.connection_pool_size = 50
elif os.getenv("ENVIRONMENT") == "development":
    perf_config.memory_cache_size = 500
    perf_config.max_concurrent_backtests = 2
    perf_config.enable_performance_monitoring = False

def get_performance_config() -> PerformanceConfig:
    """Get the current performance configuration"""
    return perf_config

def update_performance_config(**kwargs) -> None:
    """Update performance configuration dynamically"""
    global perf_config
    for key, value in kwargs.items():
        if hasattr(perf_config, key):
            setattr(perf_config, key, value)