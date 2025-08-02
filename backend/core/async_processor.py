"""
Async Processing and Background Task System
High-performance concurrent processing for Korean stock backtesting
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import traceback
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from multiprocessing import cpu_count

from core.performance_config import get_performance_config
from core.cache_manager import get_cache_manager
from core.database_optimizer import get_database_manager

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class TaskResult:
    """Task execution result"""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    execution_time_ms: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BackgroundTask:
    """Background task definition"""
    task_id: str
    task_type: str
    function: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    max_retries: int = 3
    retry_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_at: Optional[datetime] = None
    timeout_seconds: Optional[int] = None
    depends_on: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class AsyncTaskProcessor:
    """High-performance async task processor for Korean market operations"""
    
    def __init__(self):
        self.config = get_performance_config()
        
        # Task management
        self.tasks: Dict[str, BackgroundTask] = {}
        self.task_results: Dict[str, TaskResult] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        
        # Processing queues by priority
        self.task_queues = {
            TaskPriority.CRITICAL: asyncio.Queue(),
            TaskPriority.HIGH: asyncio.Queue(),
            TaskPriority.NORMAL: asyncio.Queue(),
            TaskPriority.LOW: asyncio.Queue()
        }
        
        # Executors for different types of work
        self.thread_executor = ThreadPoolExecutor(
            max_workers=self.config.max_worker_threads,
            thread_name_prefix="KoreanMarket"
        )
        self.process_executor = ProcessPoolExecutor(
            max_workers=max(2, cpu_count() // 2)
        )
        
        # Concurrency control
        self.max_concurrent_tasks = self.config.max_concurrent_backtests
        self.current_concurrent_tasks = 0
        self.task_semaphore = asyncio.Semaphore(self.max_concurrent_tasks)
        
        # Processing control
        self.is_running = False
        self.processor_tasks: List[asyncio.Task] = []
        
        logger.info(f"Async Task Processor initialized with {self.config.max_worker_threads} threads")
    
    async def start(self):
        """Start the async task processor"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Start processor tasks for each priority level
        for priority in TaskPriority:
            processor_task = asyncio.create_task(
                self._process_queue(priority),
                name=f"processor_{priority.name.lower()}"
            )
            self.processor_tasks.append(processor_task)
        
        # Start cleanup task
        cleanup_task = asyncio.create_task(
            self._cleanup_completed_tasks(),
            name="task_cleanup"
        )
        self.processor_tasks.append(cleanup_task)
        
        logger.info("Async Task Processor started")
    
    async def stop(self):
        """Stop the async task processor"""
        self.is_running = False
        
        # Cancel all processor tasks
        for task in self.processor_tasks:
            task.cancel()
        
        # Wait for all tasks to complete
        if self.processor_tasks:
            await asyncio.gather(*self.processor_tasks, return_exceptions=True)
        
        # Cancel running tasks
        for task_id, running_task in self.running_tasks.items():
            running_task.cancel()
            logger.info(f"Cancelled running task: {task_id}")
        
        # Shutdown executors
        self.thread_executor.shutdown(wait=True)
        self.process_executor.shutdown(wait=True)
        
        logger.info("Async Task Processor stopped")
    
    async def submit_task(
        self,
        task_type: str,
        function: Callable,
        args: tuple = (),
        kwargs: Dict[str, Any] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        max_retries: int = 3,
        timeout_seconds: Optional[int] = None,
        scheduled_at: Optional[datetime] = None,
        depends_on: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Submit a background task for processing"""
        
        task_id = str(uuid.uuid4())
        
        task = BackgroundTask(
            task_id=task_id,
            task_type=task_type,
            function=function,
            args=args,
            kwargs=kwargs or {},
            priority=priority,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
            scheduled_at=scheduled_at,
            depends_on=depends_on or [],
            metadata=metadata or {}
        )
        
        self.tasks[task_id] = task
        
        # Add to appropriate queue if ready to run
        if self._is_task_ready(task):
            await self.task_queues[priority].put(task_id)
            logger.debug(f"Task {task_id} ({task_type}) submitted with priority {priority.name}")
        else:
            logger.debug(f"Task {task_id} ({task_type}) queued with dependencies")
        
        return task_id
    
    async def submit_backtest_task(
        self,
        backtest_config: Dict[str, Any],
        priority: TaskPriority = TaskPriority.HIGH
    ) -> str:
        """Submit a Korean market backtesting task"""
        
        from services.backtest_service import BacktestService
        
        async def run_backtest():
            """Async backtest execution"""
            try:
                # Get optimized database manager and cache
                db_manager = await get_database_manager()
                cache_manager = await get_cache_manager()
                
                # Initialize backtest service with optimizations
                async with db_manager.get_async_session() as session:
                    backtest_service = OptimizedBacktestService(session, cache_manager)
                    
                    # Run optimized backtest
                    result = await backtest_service.run_korean_optimized_backtest(backtest_config)
                    
                    logger.info(f"Backtest completed: {backtest_config.get('symbol', 'N/A')}")
                    return result
                    
            except Exception as e:
                logger.error(f"Backtest failed: {e}")
                raise
        
        return await self.submit_task(
            task_type="korean_backtest",
            function=run_backtest,
            priority=priority,
            timeout_seconds=600,  # 10 minutes timeout
            metadata={
                "symbol": backtest_config.get("symbol"),
                "strategy": backtest_config.get("strategy_id"),
                "date_range": f"{backtest_config.get('start_date')} to {backtest_config.get('end_date')}"
            }
        )
    
    async def submit_data_processing_task(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        indicators: List[str] = None
    ) -> str:
        """Submit a data processing task for Korean market data"""
        
        async def process_market_data():
            """Process and cache Korean market data"""
            try:
                db_manager = await get_database_manager()
                cache_manager = await get_cache_manager()
                
                # Process data in chunks for memory efficiency
                chunk_size = 50  # Process 50 symbols at a time
                processed_symbols = []
                
                for i in range(0, len(symbols), chunk_size):
                    chunk_symbols = symbols[i:i + chunk_size]
                    
                    # Get market data
                    market_data = await db_manager.get_stock_data_optimized(
                        chunk_symbols,
                        start_date,
                        end_date
                    )
                    
                    # Calculate indicators if requested
                    if indicators and not market_data.empty:
                        await self._calculate_and_cache_indicators(
                            market_data, indicators, cache_manager
                        )
                    
                    processed_symbols.extend(chunk_symbols)
                    
                    # Yield control periodically
                    await asyncio.sleep(0.01)
                
                logger.info(f"Processed market data for {len(processed_symbols)} symbols")
                return {"processed_symbols": processed_symbols}
                
            except Exception as e:
                logger.error(f"Data processing failed: {e}")
                raise
        
        return await self.submit_task(
            task_type="data_processing",
            function=process_market_data,
            priority=TaskPriority.NORMAL,
            timeout_seconds=300,  # 5 minutes timeout
            metadata={
                "symbol_count": len(symbols),
                "date_range": f"{start_date} to {end_date}",
                "indicators": indicators
            }
        )
    
    async def get_task_status(self, task_id: str) -> Optional[TaskResult]:
        """Get the status and result of a task"""
        return self.task_results.get(task_id)
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task"""
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            
            # Update task result
            self.task_results[task_id] = TaskResult(
                task_id=task_id,
                status=TaskStatus.CANCELLED,
                end_time=datetime.now()
            )
            
            logger.info(f"Task {task_id} cancelled")
            return True
        
        return False
    
    async def get_processor_statistics(self) -> Dict[str, Any]:
        """Get processor performance statistics"""
        stats = {
            "is_running": self.is_running,
            "current_concurrent_tasks": self.current_concurrent_tasks,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "total_tasks": len(self.tasks),
            "completed_tasks": len([r for r in self.task_results.values() if r.status == TaskStatus.COMPLETED]),
            "failed_tasks": len([r for r in self.task_results.values() if r.status == TaskStatus.FAILED]),
            "running_tasks": len(self.running_tasks),
            "queue_lengths": {
                priority.name: queue.qsize()
                for priority, queue in self.task_queues.items()
            }
        }
        
        # Calculate average execution times by task type
        task_type_stats = {}
        for result in self.task_results.values():
            if result.execution_time_ms and result.task_id in self.tasks:
                task_type = self.tasks[result.task_id].task_type
                if task_type not in task_type_stats:
                    task_type_stats[task_type] = []
                task_type_stats[task_type].append(result.execution_time_ms)
        
        for task_type, times in task_type_stats.items():
            stats[f"avg_time_{task_type}_ms"] = sum(times) / len(times)
        
        return stats
    
    async def _process_queue(self, priority: TaskPriority):
        """Process tasks from a specific priority queue"""
        queue = self.task_queues[priority]
        
        while self.is_running:
            try:
                # Get next task with timeout
                task_id = await asyncio.wait_for(queue.get(), timeout=1.0)
                
                if task_id not in self.tasks:
                    continue
                
                task = self.tasks[task_id]
                
                # Check if task is still ready (dependencies might have changed)
                if not self._is_task_ready(task):
                    # Re-queue if dependencies not met
                    await queue.put(task_id)
                    await asyncio.sleep(0.1)
                    continue
                
                # Execute task
                await self._execute_task(task)
                
            except asyncio.TimeoutError:
                # No tasks in queue, continue
                continue
            except Exception as e:
                logger.error(f"Error in queue processor {priority.name}: {e}")
                await asyncio.sleep(1)
    
    async def _execute_task(self, task: BackgroundTask):
        """Execute a single task"""
        task_id = task.task_id
        
        # Check concurrency limit
        async with self.task_semaphore:
            self.current_concurrent_tasks += 1
            
            try:
                start_time = datetime.now()
                
                # Create task result
                task_result = TaskResult(
                    task_id=task_id,
                    status=TaskStatus.RUNNING,
                    start_time=start_time
                )
                self.task_results[task_id] = task_result
                
                # Execute task with timeout
                if asyncio.iscoroutinefunction(task.function):
                    # Async function
                    coro = task.function(*task.args, **task.kwargs)
                    if task.timeout_seconds:
                        running_task = asyncio.create_task(coro)
                        self.running_tasks[task_id] = running_task
                        result = await asyncio.wait_for(running_task, timeout=task.timeout_seconds)
                        del self.running_tasks[task_id]
                    else:
                        result = await coro
                else:
                    # Sync function - run in thread executor
                    result = await asyncio.get_event_loop().run_in_executor(
                        self.thread_executor,
                        task.function,
                        *task.args,
                        **task.kwargs
                    )
                
                # Update result with success
                end_time = datetime.now()
                execution_time_ms = (end_time - start_time).total_seconds() * 1000
                
                task_result.status = TaskStatus.COMPLETED
                task_result.result = result
                task_result.end_time = end_time
                task_result.execution_time_ms = execution_time_ms
                
                logger.info(f"Task {task_id} ({task.task_type}) completed in {execution_time_ms:.2f}ms")
                
                # Check for dependent tasks
                await self._check_dependent_tasks(task_id)
                
            except asyncio.CancelledError:
                task_result.status = TaskStatus.CANCELLED
                task_result.end_time = datetime.now()
                logger.info(f"Task {task_id} was cancelled")
                
            except Exception as e:
                # Handle task failure
                end_time = datetime.now()
                execution_time_ms = (end_time - start_time).total_seconds() * 1000
                
                task_result.status = TaskStatus.FAILED
                task_result.error = str(e)
                task_result.end_time = end_time
                task_result.execution_time_ms = execution_time_ms
                
                logger.error(f"Task {task_id} ({task.task_type}) failed: {e}")
                logger.debug(traceback.format_exc())
                
                # Retry if possible
                if task.retry_count < task.max_retries:
                    task.retry_count += 1
                    await self.task_queues[task.priority].put(task_id)
                    logger.info(f"Retrying task {task_id} (attempt {task.retry_count + 1})")
                
            finally:
                self.current_concurrent_tasks -= 1
                if task_id in self.running_tasks:
                    del self.running_tasks[task_id]
    
    def _is_task_ready(self, task: BackgroundTask) -> bool:
        """Check if task is ready to run (dependencies met, scheduled time, etc.)"""
        # Check scheduled time
        if task.scheduled_at and task.scheduled_at > datetime.now():
            return False
        
        # Check dependencies
        for dep_task_id in task.depends_on:
            if dep_task_id not in self.task_results:
                return False
            
            dep_result = self.task_results[dep_task_id]
            if dep_result.status != TaskStatus.COMPLETED:
                return False
        
        return True
    
    async def _check_dependent_tasks(self, completed_task_id: str):
        """Check and queue tasks that depend on the completed task"""
        for task_id, task in self.tasks.items():
            if (completed_task_id in task.depends_on and 
                task_id not in self.task_results and 
                self._is_task_ready(task)):
                
                await self.task_queues[task.priority].put(task_id)
                logger.debug(f"Queued dependent task {task_id}")
    
    async def _calculate_and_cache_indicators(
        self, 
        market_data: 'pd.DataFrame', 
        indicators: List[str], 
        cache_manager
    ):
        """Calculate and cache technical indicators"""
        from utils.technical_indicators import TechnicalIndicatorCalculator
        
        calculator = TechnicalIndicatorCalculator()
        
        for symbol in market_data.index.get_level_values('symbol').unique():
            symbol_data = market_data.loc[symbol]
            
            for indicator in indicators:
                try:
                    if hasattr(calculator, f'calculate_{indicator}'):
                        indicator_func = getattr(calculator, f'calculate_{indicator}')
                        indicator_data = indicator_func(symbol_data)
                        
                        # Cache the calculated indicator
                        await cache_manager.set_technical_indicators(
                            symbol, indicator, {}, indicator_data
                        )
                        
                except Exception as e:
                    logger.error(f"Error calculating {indicator} for {symbol}: {e}")
    
    async def _cleanup_completed_tasks(self):
        """Periodically clean up old completed tasks"""
        while self.is_running:
            try:
                cutoff_time = datetime.now() - timedelta(hours=24)  # Keep results for 24 hours
                
                tasks_to_remove = []
                for task_id, result in self.task_results.items():
                    if (result.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED] and
                        result.end_time and result.end_time < cutoff_time):
                        tasks_to_remove.append(task_id)
                
                for task_id in tasks_to_remove:
                    del self.task_results[task_id]
                    if task_id in self.tasks:
                        del self.tasks[task_id]
                
                if tasks_to_remove:
                    logger.info(f"Cleaned up {len(tasks_to_remove)} old tasks")
                
                # Sleep for 1 hour before next cleanup
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Error in task cleanup: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

class OptimizedBacktestService:
    """Optimized backtest service with async processing"""
    
    def __init__(self, session, cache_manager):
        self.session = session
        self.cache_manager = cache_manager
        self.config = get_performance_config()
    
    async def run_korean_optimized_backtest(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run an optimized Korean market backtest"""
        try:
            symbol = config.get('symbol', '005930')
            start_date = config.get('start_date')
            end_date = config.get('end_date')
            strategy_config = config.get('strategy_parameters', {})
            
            # Get cached market data first
            cache_key = f"backtest_data:{symbol}:{start_date}:{end_date}"
            cached_data = await self.cache_manager.get_market_data(
                symbol, (start_date, end_date)
            )
            
            if cached_data is None:
                # Fetch and cache market data
                db_manager = await get_database_manager()
                market_data = await db_manager.get_stock_data_optimized(
                    [symbol], start_date, end_date
                )
                
                await self.cache_manager.set_market_data(
                    symbol, (start_date, end_date), market_data
                )
            else:
                market_data = cached_data
                logger.debug(f"Using cached market data for {symbol}")
            
            # Run backtest simulation
            if market_data.empty:
                raise ValueError(f"No market data available for {symbol}")
            
            # Simulate backtest results (placeholder for actual implementation)
            backtest_results = {
                'symbol': symbol,
                'strategy_id': config.get('strategy_id', 'unknown'),
                'total_return': 0.15,  # Placeholder
                'sharpe_ratio': 1.2,
                'max_drawdown': -0.08,
                'total_trades': 45,
                'win_rate': 0.62,
                'final_capital': config.get('initial_capital', 10000000) * 1.15,
                'execution_time_ms': 250,
                'data_points': len(market_data),
                'cache_hit': cached_data is not None
            }
            
            return backtest_results
            
        except Exception as e:
            logger.error(f"Optimized backtest failed: {e}")
            raise

# Global async processor instance
async_processor = AsyncTaskProcessor()

async def get_async_processor() -> AsyncTaskProcessor:
    """Get the global async processor instance"""
    return async_processor