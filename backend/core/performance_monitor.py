"""
Performance Monitoring and Alerting System
Real-time performance monitoring for Korean stock backtesting platform
"""

import asyncio
import logging
import time
import psutil
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import statistics
from pathlib import Path

from core.performance_config import get_performance_config
from core.memory_optimizer import get_memory_optimizer
from core.cache_manager import get_cache_manager
from core.database_optimizer import get_database_manager

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

@dataclass
class PerformanceMetric:
    """Performance metric data point"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)
    unit: str = ""

@dataclass
class PerformanceAlert:
    """Performance alert"""
    alert_id: str
    level: AlertLevel
    title: str
    message: str
    metric_name: str
    current_value: float
    threshold_value: float
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolved_at: Optional[datetime] = None

@dataclass
class SystemHealthStatus:
    """Overall system health status"""
    status: str  # healthy, degraded, unhealthy
    cpu_usage_percent: float
    memory_usage_percent: float
    disk_usage_percent: float
    active_connections: int
    response_time_avg_ms: float
    error_rate_percent: float
    cache_hit_rate_percent: float
    timestamp: datetime = field(default_factory=datetime.now)

class PerformanceMonitor:
    """Comprehensive performance monitoring system for Korean stock platform"""
    
    def __init__(self):
        self.config = get_performance_config()
        
        # Metrics storage
        self.metrics: Dict[str, List[PerformanceMetric]] = {}
        self.alerts: List[PerformanceAlert] = []
        self.health_history: List[SystemHealthStatus] = []
        
        # Response time tracking
        self.response_times: Dict[str, List[float]] = {}
        self.error_counts: Dict[str, int] = {}
        self.request_counts: Dict[str, int] = {}
        
        # Alert thresholds
        self.alert_thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "disk_usage": 90.0,
            "response_time_ms": self.config.alert_threshold_response_time * 1000,
            "error_rate": 0.05,  # 5%
            "cache_miss_rate": 0.50,  # 50%
            "database_connections": 40,
            "concurrent_backtests": self.config.max_concurrent_backtests
        }
        
        # Monitoring control
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        self.collection_interval = self.config.metrics_collection_interval
        
        # Alert callbacks
        self.alert_callbacks: List[Callable[[PerformanceAlert], None]] = []
        
        logger.info("Performance Monitor initialized")
        
        # Start monitoring if enabled
        if self.config.enable_performance_monitoring:
            asyncio.create_task(self.start_monitoring())
    
    async def start_monitoring(self):
        """Start performance monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info("Performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop performance monitoring"""
        self.is_monitoring = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Performance monitoring stopped")
    
    def record_metric(self, name: str, value: float, metric_type: MetricType, labels: Dict[str, str] = None, unit: str = ""):
        """Record a performance metric"""
        metric = PerformanceMetric(
            name=name,
            value=value,
            metric_type=metric_type,
            labels=labels or {},
            unit=unit
        )
        
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append(metric)
        
        # Keep only recent metrics (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.metrics[name] = [
            m for m in self.metrics[name] if m.timestamp > cutoff_time
        ]
        
        # Check for alerts
        self._check_metric_alerts(name, value)
    
    def record_response_time(self, endpoint: str, response_time_ms: float):
        """Record API response time"""
        if endpoint not in self.response_times:
            self.response_times[endpoint] = []
        
        self.response_times[endpoint].append(response_time_ms)
        
        # Keep only recent response times (last hour)
        if len(self.response_times[endpoint]) > 1000:
            self.response_times[endpoint] = self.response_times[endpoint][-1000:]
        
        # Record as metric
        self.record_metric(
            f"api_response_time",
            response_time_ms,
            MetricType.TIMER,
            labels={"endpoint": endpoint},
            unit="ms"
        )
    
    def record_request(self, endpoint: str, success: bool = True):
        """Record API request"""
        if endpoint not in self.request_counts:
            self.request_counts[endpoint] = 0
        
        self.request_counts[endpoint] += 1
        
        if not success:
            if endpoint not in self.error_counts:
                self.error_counts[endpoint] = 0
            self.error_counts[endpoint] += 1
        
        # Record metrics
        self.record_metric(
            "api_requests_total",
            1,
            MetricType.COUNTER,
            labels={"endpoint": endpoint, "status": "success" if success else "error"}
        )
    
    def record_backtest_performance(self, backtest_id: str, duration_ms: float, symbol: str, strategy: str):
        """Record backtest performance metrics"""
        self.record_metric("backtest_duration", duration_ms, MetricType.TIMER, 
                          labels={"symbol": symbol, "strategy": strategy}, unit="ms")
        
        self.record_metric("backtest_completed", 1, MetricType.COUNTER,
                          labels={"symbol": symbol, "strategy": strategy})
    
    def record_korean_market_metrics(self, market_type: str, data_points: int, processing_time_ms: float):
        """Record Korean market specific metrics"""
        self.record_metric("korean_market_data_points", data_points, MetricType.GAUGE,
                          labels={"market": market_type})
        
        self.record_metric("korean_market_processing_time", processing_time_ms, MetricType.TIMER,
                          labels={"market": market_type}, unit="ms")
    
    async def get_system_health(self) -> SystemHealthStatus:
        """Get current system health status"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Database connections
            db_manager = await get_database_manager()
            db_stats = await db_manager.get_performance_analytics()
            active_connections = db_stats.get('connection_pool', {}).get('checked_out', 0)
            
            # Average response time
            all_response_times = []
            for endpoint_times in self.response_times.values():
                all_response_times.extend(endpoint_times[-100:])  # Last 100 requests per endpoint
            
            avg_response_time = statistics.mean(all_response_times) if all_response_times else 0
            
            # Error rate
            total_requests = sum(self.request_counts.values()) or 1
            total_errors = sum(self.error_counts.values())
            error_rate_percent = (total_errors / total_requests) * 100
            
            # Cache hit rate
            cache_manager = await get_cache_manager()
            cache_stats = cache_manager.get_cache_statistics()
            memory_cache_stats = cache_stats.get('memory_cache', {})
            cache_hit_rate = memory_cache_stats.get('hit_rate', 0) * 100
            
            # Determine overall status
            status = "healthy"
            if (cpu_percent > 80 or memory_percent > 85 or 
                avg_response_time > 2000 or error_rate_percent > 5):
                status = "degraded"
            
            if (cpu_percent > 95 or memory_percent > 95 or 
                avg_response_time > 5000 or error_rate_percent > 15):
                status = "unhealthy"
            
            health_status = SystemHealthStatus(
                status=status,
                cpu_usage_percent=cpu_percent,
                memory_usage_percent=memory_percent,
                disk_usage_percent=disk_percent,
                active_connections=active_connections,
                response_time_avg_ms=avg_response_time,
                error_rate_percent=error_rate_percent,
                cache_hit_rate_percent=cache_hit_rate
            )
            
            # Store health history
            self.health_history.append(health_status)
            
            # Keep only recent history (last 24 hours worth)
            if len(self.health_history) > 1440:  # 24 hours * 60 minutes
                self.health_history = self.health_history[-1440:]
            
            return health_status
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return SystemHealthStatus(
                status="error",
                cpu_usage_percent=0,
                memory_usage_percent=0,
                disk_usage_percent=0,
                active_connections=0,
                response_time_avg_ms=0,
                error_rate_percent=0,
                cache_hit_rate_percent=0
            )
    
    def get_performance_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive performance dashboard data"""
        recent_metrics = {}
        
        # Get recent metrics (last hour)
        cutoff_time = datetime.now() - timedelta(hours=1)
        
        for metric_name, metric_list in self.metrics.items():
            recent_values = [
                m.value for m in metric_list 
                if m.timestamp > cutoff_time
            ]
            
            if recent_values:
                recent_metrics[metric_name] = {
                    "current": recent_values[-1],
                    "average": statistics.mean(recent_values),
                    "min": min(recent_values),
                    "max": max(recent_values),
                    "count": len(recent_values)
                }
        
        # Get recent health status
        current_health = self.health_history[-1] if self.health_history else None
        
        # Get active alerts
        active_alerts = [alert for alert in self.alerts if not alert.resolved]
        
        # Calculate system performance score (0-100)
        performance_score = self._calculate_performance_score()
        
        return {
            "system_health": asdict(current_health) if current_health else None,
            "performance_score": performance_score,
            "metrics_summary": recent_metrics,
            "active_alerts": [asdict(alert) for alert in active_alerts],
            "response_time_percentiles": self._calculate_response_time_percentiles(),
            "korean_market_metrics": self._get_korean_market_dashboard_data(),
            "cache_performance": self._get_cache_performance_data(),
            "database_performance": self._get_database_performance_data()
        }
    
    def add_alert_callback(self, callback: Callable[[PerformanceAlert], None]):
        """Add callback for alert notifications"""
        self.alert_callbacks.append(callback)
    
    def get_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter metrics and health data
        recent_health = [h for h in self.health_history if h.timestamp > cutoff_time]
        recent_alerts = [a for a in self.alerts if a.timestamp > cutoff_time]
        
        # Calculate key performance indicators
        if recent_health:
            avg_cpu = statistics.mean([h.cpu_usage_percent for h in recent_health])
            avg_memory = statistics.mean([h.memory_usage_percent for h in recent_health])
            avg_response_time = statistics.mean([h.response_time_avg_ms for h in recent_health])
            avg_error_rate = statistics.mean([h.error_rate_percent for h in recent_health])
        else:
            avg_cpu = avg_memory = avg_response_time = avg_error_rate = 0
        
        # Calculate uptime
        healthy_periods = len([h for h in recent_health if h.status == "healthy"])
        uptime_percentage = (healthy_periods / max(1, len(recent_health))) * 100
        
        return {
            "report_period_hours": hours,
            "generated_at": datetime.now().isoformat(),
            "key_metrics": {
                "uptime_percentage": uptime_percentage,
                "average_cpu_usage": avg_cpu,
                "average_memory_usage": avg_memory,
                "average_response_time_ms": avg_response_time,
                "average_error_rate": avg_error_rate
            },
            "alert_summary": {
                "total_alerts": len(recent_alerts),
                "critical_alerts": len([a for a in recent_alerts if a.level == AlertLevel.CRITICAL]),
                "warning_alerts": len([a for a in recent_alerts if a.level == AlertLevel.WARNING]),
                "resolved_alerts": len([a for a in recent_alerts if a.resolved])
            },
            "performance_trends": self._analyze_performance_trends(recent_health),
            "recommendations": self._generate_performance_recommendations(recent_health, recent_alerts)
        }
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Collect system health
                health_status = await self.get_system_health()
                
                # Record system metrics
                self.record_metric("cpu_usage", health_status.cpu_usage_percent, MetricType.GAUGE, unit="%")
                self.record_metric("memory_usage", health_status.memory_usage_percent, MetricType.GAUGE, unit="%")
                self.record_metric("disk_usage", health_status.disk_usage_percent, MetricType.GAUGE, unit="%")
                self.record_metric("active_connections", health_status.active_connections, MetricType.GAUGE)
                self.record_metric("response_time_avg", health_status.response_time_avg_ms, MetricType.GAUGE, unit="ms")
                self.record_metric("error_rate", health_status.error_rate_percent, MetricType.GAUGE, unit="%")
                self.record_metric("cache_hit_rate", health_status.cache_hit_rate_percent, MetricType.GAUGE, unit="%")
                
                # Memory optimizer metrics
                memory_optimizer = get_memory_optimizer()
                memory_stats = memory_optimizer.get_memory_stats()
                self.record_metric("process_memory", memory_stats.process_memory_mb, MetricType.GAUGE, unit="MB")
                self.record_metric("cached_dataframes", memory_stats.cached_dataframes_mb, MetricType.GAUGE, unit="MB")
                
                # Clean up old data periodically
                if len(self.health_history) % 100 == 0:
                    await self._cleanup_old_data()
                
                # Wait for next collection
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.collection_interval)
    
    def _check_metric_alerts(self, metric_name: str, value: float):
        """Check if metric value triggers any alerts"""
        threshold_key = metric_name.replace("_", "")
        
        if threshold_key in self.alert_thresholds:
            threshold = self.alert_thresholds[threshold_key]
            
            # Check if alert should be triggered
            should_alert = False
            level = AlertLevel.WARNING
            
            if metric_name in ["cpu_usage", "memory_usage", "disk_usage", "error_rate"]:
                if value > threshold:
                    should_alert = True
                    level = AlertLevel.CRITICAL if value > threshold * 1.2 else AlertLevel.WARNING
            
            elif metric_name == "response_time_avg":
                if value > threshold:
                    should_alert = True
                    level = AlertLevel.CRITICAL if value > threshold * 2 else AlertLevel.WARNING
            
            if should_alert:
                self._create_alert(
                    level=level,
                    title=f"High {metric_name.replace('_', ' ').title()}",
                    message=f"{metric_name} is {value:.2f}, exceeding threshold of {threshold}",
                    metric_name=metric_name,
                    current_value=value,
                    threshold_value=threshold
                )
    
    def _create_alert(self, level: AlertLevel, title: str, message: str, metric_name: str, current_value: float, threshold_value: float):
        """Create a new performance alert"""
        alert_id = f"alert_{int(time.time())}_{metric_name}"
        
        # Check if similar alert already exists
        existing_alert = next(
            (a for a in self.alerts 
             if a.metric_name == metric_name and not a.resolved and 
             (datetime.now() - a.timestamp).total_seconds() < 300),  # 5 minutes
            None
        )
        
        if existing_alert:
            return  # Don't create duplicate alerts
        
        alert = PerformanceAlert(
            alert_id=alert_id,
            level=level,
            title=title,
            message=message,
            metric_name=metric_name,
            current_value=current_value,
            threshold_value=threshold_value
        )
        
        self.alerts.append(alert)
        
        # Notify callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
        
        logger.warning(f"Performance alert: {title} - {message}")
    
    def _calculate_performance_score(self) -> float:
        """Calculate overall performance score (0-100)"""
        if not self.health_history:
            return 0.0
        
        recent_health = self.health_history[-10:]  # Last 10 readings
        
        scores = []
        for health in recent_health:
            # Individual component scores
            cpu_score = max(0, 100 - health.cpu_usage_percent)
            memory_score = max(0, 100 - health.memory_usage_percent)
            response_score = max(0, 100 - min(100, health.response_time_avg_ms / 50))  # 50ms = 0 score
            error_score = max(0, 100 - (health.error_rate_percent * 10))  # 10% error = 0 score
            cache_score = health.cache_hit_rate_percent
            
            # Weighted average
            overall_score = (
                cpu_score * 0.25 +
                memory_score * 0.25 +
                response_score * 0.25 +
                error_score * 0.15 +
                cache_score * 0.10
            )
            
            scores.append(overall_score)
        
        return statistics.mean(scores)
    
    def _calculate_response_time_percentiles(self) -> Dict[str, float]:
        """Calculate response time percentiles"""
        all_times = []
        for times in self.response_times.values():
            all_times.extend(times[-100:])  # Recent times only
        
        if not all_times:
            return {"p50": 0, "p95": 0, "p99": 0}
        
        sorted_times = sorted(all_times)
        n = len(sorted_times)
        
        return {
            "p50": sorted_times[int(n * 0.5)] if n > 0 else 0,
            "p95": sorted_times[int(n * 0.95)] if n > 0 else 0,
            "p99": sorted_times[int(n * 0.99)] if n > 0 else 0
        }
    
    def _get_korean_market_dashboard_data(self) -> Dict[str, Any]:
        """Get Korean market specific dashboard data"""
        korean_metrics = {}
        
        for metric_name, metric_list in self.metrics.items():
            if "korean" in metric_name.lower():
                recent_values = [m.value for m in metric_list[-10:]]
                if recent_values:
                    korean_metrics[metric_name] = {
                        "current": recent_values[-1],
                        "average": statistics.mean(recent_values)
                    }
        
        return korean_metrics
    
    def _get_cache_performance_data(self) -> Dict[str, Any]:
        """Get cache performance data"""
        cache_metrics = {}
        
        for metric_name in ["cache_hit_rate", "cached_dataframes"]:
            if metric_name in self.metrics:
                recent_values = [m.value for m in self.metrics[metric_name][-10:]]
                if recent_values:
                    cache_metrics[metric_name] = {
                        "current": recent_values[-1],
                        "trend": "up" if len(recent_values) > 1 and recent_values[-1] > recent_values[0] else "down"
                    }
        
        return cache_metrics
    
    def _get_database_performance_data(self) -> Dict[str, Any]:
        """Get database performance data"""
        db_metrics = {}
        
        for metric_name in ["active_connections", "query_time"]:
            if metric_name in self.metrics:
                recent_values = [m.value for m in self.metrics[metric_name][-10:]]
                if recent_values:
                    db_metrics[metric_name] = {
                        "current": recent_values[-1],
                        "average": statistics.mean(recent_values)
                    }
        
        return db_metrics
    
    def _analyze_performance_trends(self, health_data: List[SystemHealthStatus]) -> Dict[str, str]:
        """Analyze performance trends"""
        if len(health_data) < 2:
            return {"trend": "insufficient_data"}
        
        # CPU trend
        cpu_values = [h.cpu_usage_percent for h in health_data]
        cpu_trend = "stable"
        if len(cpu_values) >= 3:
            if cpu_values[-1] > cpu_values[0] * 1.2:
                cpu_trend = "increasing"
            elif cpu_values[-1] < cpu_values[0] * 0.8:
                cpu_trend = "decreasing"
        
        # Memory trend
        memory_values = [h.memory_usage_percent for h in health_data]
        memory_trend = "stable"
        if len(memory_values) >= 3:
            if memory_values[-1] > memory_values[0] * 1.2:
                memory_trend = "increasing"
            elif memory_values[-1] < memory_values[0] * 0.8:
                memory_trend = "decreasing"
        
        return {
            "cpu_trend": cpu_trend,
            "memory_trend": memory_trend,
            "overall_trend": "improving" if cpu_trend == "decreasing" and memory_trend == "decreasing" else "stable"
        }
    
    def _generate_performance_recommendations(self, health_data: List[SystemHealthStatus], alerts: List[PerformanceAlert]) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        if not health_data:
            return ["Insufficient monitoring data for recommendations"]
        
        avg_cpu = statistics.mean([h.cpu_usage_percent for h in health_data])
        avg_memory = statistics.mean([h.memory_usage_percent for h in health_data])
        avg_response_time = statistics.mean([h.response_time_avg_ms for h in health_data])
        
        if avg_cpu > 70:
            recommendations.append("High CPU usage detected - consider scaling horizontally or optimizing CPU-intensive operations")
        
        if avg_memory > 80:
            recommendations.append("High memory usage detected - review memory optimization strategies and consider increasing available memory")
        
        if avg_response_time > 1000:
            recommendations.append("High response times detected - review API performance and database query optimization")
        
        critical_alerts = [a for a in alerts if a.level == AlertLevel.CRITICAL]
        if len(critical_alerts) > 5:
            recommendations.append("Multiple critical alerts detected - immediate investigation required")
        
        if not recommendations:
            recommendations.append("System performance is within acceptable parameters")
        
        return recommendations
    
    async def _cleanup_old_data(self):
        """Clean up old monitoring data"""
        cutoff_time = datetime.now() - timedelta(hours=48)
        
        # Clean old alerts
        self.alerts = [a for a in self.alerts if a.timestamp > cutoff_time]
        
        # Clean old metrics
        for metric_name in list(self.metrics.keys()):
            self.metrics[metric_name] = [
                m for m in self.metrics[metric_name] if m.timestamp > cutoff_time
            ]
            
            # Remove empty metric lists
            if not self.metrics[metric_name]:
                del self.metrics[metric_name]
        
        logger.debug("Cleaned up old monitoring data")

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance"""
    return performance_monitor