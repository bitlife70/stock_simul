"""
Memory Optimization Module
Advanced memory management for large Korean stock market datasets
"""

import gc
import psutil
import logging
import weakref
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Iterator, Tuple
from dataclasses import dataclass
from contextlib import contextmanager
import numpy as np
import pandas as pd

from core.performance_config import get_performance_config

logger = logging.getLogger(__name__)

@dataclass
class MemoryUsageStats:
    """Memory usage statistics"""
    total_memory_mb: float
    available_memory_mb: float
    used_memory_mb: float
    memory_percentage: float
    process_memory_mb: float
    gc_collections: Dict[int, int]
    large_objects_count: int
    cached_dataframes_mb: float

class MemoryOptimizer:
    """Advanced memory optimizer for Korean stock market data processing"""
    
    def __init__(self):
        self.config = get_performance_config()
        self.max_memory_mb = self.config.max_memory_usage_mb
        
        # Memory tracking
        self.dataframe_cache: Dict[str, weakref.ReferenceType] = {}
        self.large_objects: Dict[str, Any] = {}
        self.memory_checkpoints: List[Tuple[datetime, float]] = []
        
        # Pandas optimization settings
        self._optimize_pandas_settings()
        
        # GC optimization
        self._optimize_garbage_collection()
        
        logger.info(f"Memory Optimizer initialized with {self.max_memory_mb}MB limit")
    
    def _optimize_pandas_settings(self):
        """Optimize pandas for memory efficiency"""
        # Use categorical data types for string columns with limited unique values
        pd.options.mode.copy_on_write = True  # Reduce unnecessary copying
        
        # Set display options to prevent memory issues with large DataFrames
        pd.set_option('display.max_rows', 100)
        pd.set_option('display.max_columns', 20)
        
        logger.debug("Pandas optimized for memory efficiency")
    
    def _optimize_garbage_collection(self):
        """Optimize Python garbage collection"""
        # Adjust GC thresholds for better performance with large datasets
        current_thresholds = gc.get_threshold()
        new_thresholds = (
            self.config.gc_threshold,
            current_thresholds[1] * 2,
            current_thresholds[2] * 2
        )
        gc.set_threshold(*new_thresholds)
        
        logger.debug(f"GC thresholds optimized: {new_thresholds}")
    
    def get_memory_stats(self) -> MemoryUsageStats:
        """Get comprehensive memory usage statistics"""
        # System memory
        memory = psutil.virtual_memory()
        
        # Process memory
        process = psutil.Process()
        process_memory = process.memory_info()
        
        # GC statistics
        gc_stats = {}
        for generation in range(3):
            gc_stats[generation] = gc.get_count()[generation]
        
        # Calculate cached DataFrame memory
        cached_df_memory = 0
        for key, weak_ref in list(self.dataframe_cache.items()):
            df = weak_ref()
            if df is not None:
                cached_df_memory += self._estimate_dataframe_memory(df)
            else:
                # Clean up dead references
                del self.dataframe_cache[key]
        
        return MemoryUsageStats(
            total_memory_mb=memory.total / (1024 * 1024),
            available_memory_mb=memory.available / (1024 * 1024),
            used_memory_mb=memory.used / (1024 * 1024),
            memory_percentage=memory.percent,
            process_memory_mb=process_memory.rss / (1024 * 1024),
            gc_collections=gc_stats,
            large_objects_count=len(self.large_objects),
            cached_dataframes_mb=cached_df_memory / (1024 * 1024)
        )
    
    def check_memory_threshold(self) -> bool:
        """Check if memory usage exceeds threshold"""
        stats = self.get_memory_stats()
        
        # Record checkpoint
        self.memory_checkpoints.append((datetime.now(), stats.process_memory_mb))
        
        # Keep only recent checkpoints
        cutoff_time = datetime.now() - timedelta(hours=1)
        self.memory_checkpoints = [
            (time, memory) for time, memory in self.memory_checkpoints
            if time > cutoff_time
        ]
        
        if stats.process_memory_mb > self.max_memory_mb:
            logger.warning(f"Memory usage ({stats.process_memory_mb:.1f}MB) exceeds threshold ({self.max_memory_mb}MB)")
            return True
        
        return False
    
    def optimize_dataframe_memory(self, df: pd.DataFrame, symbol: str = None) -> pd.DataFrame:
        """Optimize DataFrame memory usage with Korean market specifics"""
        if df.empty:
            return df
        
        original_memory = self._estimate_dataframe_memory(df)
        optimized_df = df.copy()
        
        # Optimize data types
        for column in optimized_df.columns:
            col_data = optimized_df[column]
            
            # Handle numeric columns
            if pd.api.types.is_numeric_dtype(col_data):
                # For Korean Won prices, use appropriate integer types
                if column in ['open', 'high', 'low', 'close', 'open_price', 'high_price', 'low_price', 'close_price']:
                    # Korean stocks are typically priced in won (integers)
                    if col_data.min() >= 0 and col_data.max() < 2**31:
                        optimized_df[column] = col_data.astype('uint32')
                    else:
                        optimized_df[column] = col_data.astype('int64')
                
                # Volume columns
                elif column in ['volume', 'trading_volume']:
                    if col_data.max() < 2**32:
                        optimized_df[column] = col_data.astype('uint32')
                    else:
                        optimized_df[column] = col_data.astype('uint64')
                
                # Market cap and financial data
                elif column in ['market_cap', 'market_value']:
                    optimized_df[column] = col_data.astype('uint64')
                
                # Percentage and ratio columns
                elif column in ['change_pct', 'volume_ratio', 'returns']:
                    optimized_df[column] = col_data.astype('float32')
                
                # Other numeric columns - try to downcast
                else:
                    optimized_df[column] = pd.to_numeric(col_data, downcast='integer')
                    if optimized_df[column].dtype == col_data.dtype:
                        optimized_df[column] = pd.to_numeric(col_data, downcast='float')
            
            # Handle string columns
            elif pd.api.types.is_string_dtype(col_data) or pd.api.types.is_object_dtype(col_data):
                unique_ratio = col_data.nunique() / len(col_data)
                
                # Use categorical for columns with low cardinality
                if unique_ratio < 0.1:  # Less than 10% unique values
                    optimized_df[column] = col_data.astype('category')
                
                # For Korean symbol codes (6-digit strings), use categorical
                elif column == 'symbol' and symbol:
                    optimized_df[column] = col_data.astype('category')
        
        # Optimize index
        if isinstance(optimized_df.index, pd.MultiIndex):
            # For multi-index with symbol and date
            index_levels = []
            for i, level in enumerate(optimized_df.index.levels):
                if i == 0 and optimized_df.index.names[0] == 'symbol':
                    # Symbol level - use categorical
                    index_levels.append(level.astype('category'))
                elif pd.api.types.is_datetime64_any_dtype(level):
                    # Date level - already optimized
                    index_levels.append(level)
                else:
                    index_levels.append(level)
            
            # Rebuild multi-index if optimizations were made
            if any(not level.equals(orig_level) for level, orig_level in zip(index_levels, optimized_df.index.levels)):
                optimized_df.index = pd.MultiIndex.from_arrays(
                    [optimized_df.index.get_level_values(i) for i in range(optimized_df.index.nlevels)],
                    names=optimized_df.index.names
                )
        
        # Remove unused categories to save memory
        for column in optimized_df.select_dtypes(include=['category']):
            optimized_df[column] = optimized_df[column].cat.remove_unused_categories()
        
        optimized_memory = self._estimate_dataframe_memory(optimized_df)
        memory_saved = original_memory - optimized_memory
        
        if memory_saved > 0:
            logger.debug(f"DataFrame memory optimized: saved {memory_saved / (1024*1024):.2f}MB ({memory_saved/original_memory*100:.1f}%)")
        
        return optimized_df
    
    def create_memory_efficient_chunks(
        self, 
        symbols: List[str], 
        chunk_size: Optional[int] = None
    ) -> Iterator[List[str]]:
        """Create memory-efficient chunks for processing large symbol lists"""
        if chunk_size is None:
            # Calculate optimal chunk size based on available memory
            stats = self.get_memory_stats()
            available_mb = stats.available_memory_mb
            
            # Estimate memory per symbol (rough calculation)
            estimated_memory_per_symbol = 2  # MB per symbol for 1 year of daily data
            
            # Use conservative chunk size to avoid memory issues
            optimal_chunk_size = max(10, min(100, int(available_mb / (estimated_memory_per_symbol * 4))))
            chunk_size = optimal_chunk_size
        
        logger.debug(f"Processing {len(symbols)} symbols in chunks of {chunk_size}")
        
        for i in range(0, len(symbols), chunk_size):
            chunk = symbols[i:i + chunk_size]
            
            # Check memory before yielding chunk
            if self.check_memory_threshold():
                self.force_garbage_collection()
                
                # If still over threshold, reduce chunk size
                if self.check_memory_threshold():
                    chunk = chunk[:len(chunk)//2]
                    logger.warning(f"Reduced chunk size to {len(chunk)} due to memory pressure")
            
            yield chunk
    
    def cache_dataframe(self, key: str, df: pd.DataFrame) -> None:
        """Cache DataFrame with weak reference to prevent memory leaks"""
        # Optimize DataFrame before caching
        optimized_df = self.optimize_dataframe_memory(df, key)
        
        # Use weak reference to allow garbage collection
        self.dataframe_cache[key] = weakref.ref(optimized_df)
        
        logger.debug(f"Cached optimized DataFrame: {key}")
    
    def get_cached_dataframe(self, key: str) -> Optional[pd.DataFrame]:
        """Get cached DataFrame if still available"""
        if key in self.dataframe_cache:
            weak_ref = self.dataframe_cache[key]
            df = weak_ref()
            
            if df is not None:
                logger.debug(f"Retrieved cached DataFrame: {key}")
                return df
            else:
                # Clean up dead reference
                del self.dataframe_cache[key]
        
        return None
    
    def clear_dataframe_cache(self) -> int:
        """Clear DataFrame cache and return number of items cleared"""
        count = len(self.dataframe_cache)
        self.dataframe_cache.clear()
        logger.info(f"Cleared {count} cached DataFrames")
        return count
    
    @contextmanager
    def memory_monitoring_context(self, operation_name: str):
        """Context manager for monitoring memory usage during operations"""
        start_stats = self.get_memory_stats()
        start_time = datetime.now()
        
        logger.debug(f"Starting {operation_name} - Memory: {start_stats.process_memory_mb:.1f}MB")
        
        try:
            yield start_stats
        finally:
            end_stats = self.get_memory_stats()
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            memory_delta = end_stats.process_memory_mb - start_stats.process_memory_mb
            
            logger.info(
                f"Completed {operation_name} in {duration:.2f}s - "
                f"Memory: {end_stats.process_memory_mb:.1f}MB "
                f"(Δ{memory_delta:+.1f}MB)"
            )
            
            # Force GC if memory usage increased significantly
            if memory_delta > 100:  # More than 100MB increase
                self.force_garbage_collection()
    
    def force_garbage_collection(self) -> Dict[int, int]:
        """Force garbage collection and return collection counts"""
        before_stats = self.get_memory_stats()
        
        # Force collection for all generations
        collections = {}
        for generation in range(3):
            collections[generation] = gc.collect(generation)
        
        after_stats = self.get_memory_stats()
        memory_freed = before_stats.process_memory_mb - after_stats.process_memory_mb
        
        if memory_freed > 1:  # Only log if significant memory was freed
            logger.info(f"GC freed {memory_freed:.1f}MB memory")
        
        return collections
    
    def optimize_korean_market_data_processing(self, df: pd.DataFrame) -> pd.DataFrame:
        """Specialized optimization for Korean market data"""
        if df.empty:
            return df
        
        # Korean market specific optimizations
        optimized_df = df.copy()
        
        # Optimize Korean stock symbol column
        if 'symbol' in optimized_df.columns:
            # Korean stock codes are 6-digit strings, use categorical
            optimized_df['symbol'] = optimized_df['symbol'].astype('category')
        
        # Optimize market column (KOSPI/KOSDAQ/KONEX)
        if 'market' in optimized_df.columns:
            optimized_df['market'] = optimized_df['market'].astype('category')
        
        # Optimize sector columns with Korean sectors
        if 'sector' in optimized_df.columns:
            optimized_df['sector'] = optimized_df['sector'].astype('category')
        
        # Korean Won price optimization
        won_price_columns = ['open_price', 'high_price', 'low_price', 'close_price', 'adj_close']
        for col in won_price_columns:
            if col in optimized_df.columns:
                # Korean stocks are priced in won (integers), optimize accordingly  
                optimized_df[col] = optimized_df[col].astype('uint32')
        
        # Volume optimization
        if 'volume' in optimized_df.columns:
            optimized_df['volume'] = optimized_df['volume'].astype('uint64')
        
        # Market cap for chaebol companies (can be very large)
        if 'market_cap' in optimized_df.columns:
            optimized_df['market_cap'] = optimized_df['market_cap'].astype('uint64')
        
        return optimized_df
    
    def create_efficient_korean_dataset(
        self, 
        symbols: List[str], 
        date_range: Tuple[str, str],
        columns: List[str] = None
    ) -> pd.DataFrame:
        """Create memory-efficient dataset for Korean stock analysis"""
        
        with self.memory_monitoring_context("korean_dataset_creation"):
            # Default columns optimized for Korean market analysis
            if columns is None:
                columns = [
                    'open_price', 'high_price', 'low_price', 'close_price',
                    'volume', 'market_cap'
                ]
            
            # Process symbols in memory-efficient chunks
            dataframes = []
            
            for symbol_chunk in self.create_memory_efficient_chunks(symbols):
                # In production, this would fetch data from database
                # For now, create sample optimized structure
                chunk_data = self._create_sample_korean_data(symbol_chunk, date_range, columns)
                
                if not chunk_data.empty:
                    # Optimize chunk before combining
                    optimized_chunk = self.optimize_korean_market_data_processing(chunk_data)
                    dataframes.append(optimized_chunk)
                
                # Force GC between chunks if memory is high
                if self.check_memory_threshold():
                    self.force_garbage_collection()
            
            # Combine chunks efficiently
            if dataframes:
                combined_df = pd.concat(dataframes, ignore_index=False)
                
                # Final optimization
                final_df = self.optimize_dataframe_memory(combined_df)
                
                logger.info(f"Created efficient Korean dataset: {len(final_df)} rows, {final_df.memory_usage(deep=True).sum() / 1024**2:.2f}MB")
                
                return final_df
            else:
                return pd.DataFrame()
    
    def _estimate_dataframe_memory(self, df: pd.DataFrame) -> int:
        """Estimate DataFrame memory usage in bytes"""
        return df.memory_usage(deep=True).sum()
    
    def _create_sample_korean_data(
        self, 
        symbols: List[str], 
        date_range: Tuple[str, str], 
        columns: List[str]
    ) -> pd.DataFrame:
        """Create sample Korean market data (placeholder for actual data fetching)"""
        # This is a placeholder - in production, would fetch from database
        dates = pd.date_range(start=date_range[0], end=date_range[1], freq='D')
        
        data = []
        for symbol in symbols:
            for date in dates:
                if date.weekday() < 5:  # Korean market trading days
                    row = {
                        'symbol': symbol,
                        'date': date,
                        'open_price': 50000 + np.random.randint(-5000, 5000),
                        'high_price': 55000 + np.random.randint(-5000, 5000),
                        'low_price': 45000 + np.random.randint(-5000, 5000),
                        'close_price': 50000 + np.random.randint(-5000, 5000),
                        'volume': np.random.randint(100000, 10000000),
                        'market_cap': np.random.randint(100000000000, 10000000000000)
                    }
                    
                    # Only include requested columns
                    filtered_row = {k: v for k, v in row.items() if k in columns + ['symbol', 'date']}
                    data.append(filtered_row)
        
        if data:
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index(['symbol', 'date']).sort_index()
            return df
        else:
            return pd.DataFrame()
    
    def get_memory_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive memory optimization report"""
        stats = self.get_memory_stats()
        
        # Calculate memory trends
        memory_trend = "stable"
        if len(self.memory_checkpoints) >= 2:
            recent_memory = [mem for _, mem in self.memory_checkpoints[-10:]]
            if len(recent_memory) >= 2:
                trend_slope = (recent_memory[-1] - recent_memory[0]) / len(recent_memory)
                if trend_slope > 10:  # MB per checkpoint
                    memory_trend = "increasing"
                elif trend_slope < -10:
                    memory_trend = "decreasing"
        
        return {
            "memory_stats": {
                "current_usage_mb": stats.process_memory_mb,
                "memory_limit_mb": self.max_memory_mb,
                "usage_percentage": (stats.process_memory_mb / self.max_memory_mb) * 100,
                "system_memory_percentage": stats.memory_percentage,
                "available_memory_mb": stats.available_memory_mb
            },
            "optimization_stats": {
                "cached_dataframes": len(self.dataframe_cache),
                "cached_dataframes_mb": stats.cached_dataframes_mb,
                "large_objects_count": stats.large_objects_count,
                "gc_collections": stats.gc_collections
            },
            "performance_indicators": {
                "memory_trend": memory_trend,
                "checkpoints_recorded": len(self.memory_checkpoints),
                "optimization_active": True
            },
            "recommendations": self._generate_memory_recommendations(stats)
        }
    
    def _generate_memory_recommendations(self, stats: MemoryUsageStats) -> List[str]:
        """Generate memory optimization recommendations"""
        recommendations = []
        
        usage_percentage = (stats.process_memory_mb / self.max_memory_mb) * 100
        
        if usage_percentage > 80:
            recommendations.append("Memory usage is high - consider reducing dataset size or batch processing")
        
        if stats.cached_dataframes_mb > 500:
            recommendations.append("DataFrame cache is large - consider clearing old cached data")
        
        if len(self.memory_checkpoints) > 50 and usage_percentage > 60:
            recommendations.append("Frequent memory monitoring detected - enable aggressive GC")
        
        if stats.large_objects_count > 10:
            recommendations.append("Multiple large objects detected - review object lifecycle")
        
        if not recommendations:
            recommendations.append("Memory usage is optimal")
        
        return recommendations

# Global memory optimizer instance
memory_optimizer = MemoryOptimizer()

def get_memory_optimizer() -> MemoryOptimizer:
    """Get the global memory optimizer instance"""
    return memory_optimizer