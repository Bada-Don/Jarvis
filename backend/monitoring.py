"""
Monitoring Module for FunctionGemma Integration

This module provides comprehensive monitoring capabilities including:
- Logging for all operations
- Performance metrics collection
- Error tracking
- Real-time monitoring dashboard data

Requirements: 10.2 - Execution failure logging with context
"""

import os
import time
import logging
import json
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict, deque
from threading import Lock


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('functiongemma_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class OperationMetric:
    """Metrics for a single operation."""
    operation_id: str
    operation_type: str  # function_call, model_inference, etc.
    function_name: Optional[str]
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    parameters: Optional[Dict] = None
    result: Optional[Dict] = None
    
    def complete(self, success: bool, error_message: Optional[str] = None, result: Optional[Dict] = None):
        """Mark operation as complete."""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.success = success
        self.error_message = error_message
        self.result = result
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ErrorRecord:
    """Record of an error occurrence."""
    timestamp: float
    error_type: str
    error_message: str
    function_name: Optional[str]
    parameters: Optional[Dict]
    stack_trace: Optional[str]
    context: Optional[Dict]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


class PerformanceMonitor:
    """
    Monitor performance metrics for the FunctionGemma service.
    
    Tracks:
    - Operation durations
    - Success/failure rates
    - Throughput (operations per second)
    - Resource usage (CPU, memory)
    """
    
    def __init__(self, max_history: int = 1000):
        """
        Initialize performance monitor.
        
        Args:
            max_history: Maximum number of operations to keep in history
        """
        self.max_history = max_history
        self.operations: deque = deque(maxlen=max_history)
        self.operation_counts = defaultdict(int)
        self.operation_durations = defaultdict(list)
        self.success_counts = defaultdict(int)
        self.failure_counts = defaultdict(int)
        self.lock = Lock()
        
        logger.info("PerformanceMonitor initialized")
    
    def start_operation(
        self,
        operation_type: str,
        function_name: Optional[str] = None,
        parameters: Optional[Dict] = None
    ) -> str:
        """
        Start tracking an operation.
        
        Args:
            operation_type: Type of operation (function_call, model_inference, etc.)
            function_name: Name of function being called (if applicable)
            parameters: Operation parameters
        
        Returns:
            operation_id: Unique ID for this operation
        """
        operation_id = f"{operation_type}_{int(time.time() * 1000000)}"
        
        metric = OperationMetric(
            operation_id=operation_id,
            operation_type=operation_type,
            function_name=function_name,
            start_time=time.time(),
            parameters=parameters
        )
        
        with self.lock:
            self.operations.append(metric)
            self.operation_counts[operation_type] += 1
        
        logger.debug(f"Started operation: {operation_id} ({operation_type})")
        return operation_id
    
    def complete_operation(
        self,
        operation_id: str,
        success: bool,
        error_message: Optional[str] = None,
        result: Optional[Dict] = None
    ):
        """
        Mark an operation as complete.
        
        Args:
            operation_id: ID of the operation
            success: Whether operation succeeded
            error_message: Error message if failed
            result: Operation result
        """
        with self.lock:
            # Find the operation
            for metric in reversed(self.operations):
                if metric.operation_id == operation_id:
                    metric.complete(success, error_message, result)
                    
                    # Update statistics
                    if success:
                        self.success_counts[metric.operation_type] += 1
                    else:
                        self.failure_counts[metric.operation_type] += 1
                    
                    # Track duration
                    if metric.duration:
                        self.operation_durations[metric.operation_type].append(metric.duration)
                        
                        # Keep only recent durations (last 100)
                        if len(self.operation_durations[metric.operation_type]) > 100:
                            self.operation_durations[metric.operation_type].pop(0)
                    
                    logger.debug(
                        f"Completed operation: {operation_id} "
                        f"(success={success}, duration={metric.duration:.3f}s)"
                    )
                    break
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current performance metrics.
        
        Returns:
            Dict with performance metrics
        """
        with self.lock:
            metrics = {
                "total_operations": sum(self.operation_counts.values()),
                "operations_by_type": dict(self.operation_counts),
                "success_rate": self._calculate_success_rate(),
                "average_durations": self._calculate_average_durations(),
                "recent_operations": [
                    op.to_dict() for op in list(self.operations)[-10:]
                ],
                "throughput": self._calculate_throughput(),
            }
        
        return metrics
    
    def _calculate_success_rate(self) -> Dict[str, float]:
        """Calculate success rate by operation type."""
        rates = {}
        for op_type in self.operation_counts.keys():
            total = self.success_counts[op_type] + self.failure_counts[op_type]
            if total > 0:
                rates[op_type] = self.success_counts[op_type] / total
            else:
                rates[op_type] = 0.0
        return rates
    
    def _calculate_average_durations(self) -> Dict[str, float]:
        """Calculate average duration by operation type."""
        averages = {}
        for op_type, durations in self.operation_durations.items():
            if durations:
                averages[op_type] = sum(durations) / len(durations)
            else:
                averages[op_type] = 0.0
        return averages
    
    def _calculate_throughput(self) -> Dict[str, float]:
        """Calculate operations per second by type."""
        # Calculate throughput over last minute
        one_minute_ago = time.time() - 60
        
        recent_ops = defaultdict(int)
        for op in self.operations:
            if op.start_time >= one_minute_ago:
                recent_ops[op.operation_type] += 1
        
        # Convert to per-second rate
        throughput = {
            op_type: count / 60.0
            for op_type, count in recent_ops.items()
        }
        
        return throughput


class ErrorTracker:
    """
    Track errors and failures in the system.
    
    Provides:
    - Error logging with context
    - Error frequency tracking
    - Error pattern detection
    """
    
    def __init__(self, max_errors: int = 500):
        """
        Initialize error tracker.
        
        Args:
            max_errors: Maximum number of errors to keep in history
        """
        self.max_errors = max_errors
        self.errors: deque = deque(maxlen=max_errors)
        self.error_counts = defaultdict(int)
        self.lock = Lock()
        
        logger.info("ErrorTracker initialized")
    
    def log_error(
        self,
        error_type: str,
        error_message: str,
        function_name: Optional[str] = None,
        parameters: Optional[Dict] = None,
        stack_trace: Optional[str] = None,
        context: Optional[Dict] = None
    ):
        """
        Log an error with full context.
        
        Args:
            error_type: Type of error (parsing, execution, validation, etc.)
            error_message: Error message
            function_name: Function where error occurred
            parameters: Function parameters
            stack_trace: Stack trace if available
            context: Additional context
        """
        error_record = ErrorRecord(
            timestamp=time.time(),
            error_type=error_type,
            error_message=error_message,
            function_name=function_name,
            parameters=parameters,
            stack_trace=stack_trace,
            context=context
        )
        
        with self.lock:
            self.errors.append(error_record)
            self.error_counts[error_type] += 1
        
        # Log to file with full context
        logger.error(
            f"Error tracked: {error_type}\n"
            f"  Message: {error_message}\n"
            f"  Function: {function_name}\n"
            f"  Parameters: {parameters}\n"
            f"  Context: {context}"
        )
    
    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get summary of errors.
        
        Returns:
            Dict with error statistics
        """
        with self.lock:
            return {
                "total_errors": len(self.errors),
                "errors_by_type": dict(self.error_counts),
                "recent_errors": [
                    error.to_dict() for error in list(self.errors)[-10:]
                ],
                "error_rate": self._calculate_error_rate()
            }
    
    def _calculate_error_rate(self) -> float:
        """Calculate errors per minute over last hour."""
        one_hour_ago = time.time() - 3600
        
        recent_errors = sum(
            1 for error in self.errors
            if error.timestamp >= one_hour_ago
        )
        
        return recent_errors / 60.0  # Errors per minute


class ResourceMonitor:
    """
    Monitor system resource usage.
    
    Tracks:
    - CPU usage
    - Memory usage
    - Disk usage
    - Network usage (if applicable)
    """
    
    def __init__(self):
        """Initialize resource monitor."""
        self.process = psutil.Process()
        logger.info("ResourceMonitor initialized")
    
    def get_resource_usage(self) -> Dict[str, Any]:
        """
        Get current resource usage.
        
        Returns:
            Dict with resource usage metrics
        """
        # Process-specific metrics
        process_memory = self.process.memory_info()
        process_cpu = self.process.cpu_percent(interval=0.1)
        
        # System-wide metrics
        system_memory = psutil.virtual_memory()
        system_cpu = psutil.cpu_percent(interval=0.1)
        disk = psutil.disk_usage('/')
        
        return {
            "process": {
                "memory_mb": process_memory.rss / 1024 / 1024,
                "memory_percent": self.process.memory_percent(),
                "cpu_percent": process_cpu,
                "threads": self.process.num_threads()
            },
            "system": {
                "memory_total_mb": system_memory.total / 1024 / 1024,
                "memory_available_mb": system_memory.available / 1024 / 1024,
                "memory_percent": system_memory.percent,
                "cpu_percent": system_cpu,
                "disk_total_gb": disk.total / 1024 / 1024 / 1024,
                "disk_used_gb": disk.used / 1024 / 1024 / 1024,
                "disk_percent": disk.percent
            }
        }


class MonitoringDashboard:
    """
    Centralized monitoring dashboard that aggregates all metrics.
    
    Provides a single interface for accessing:
    - Performance metrics
    - Error tracking
    - Resource usage
    - System health
    """
    
    def __init__(self):
        """Initialize monitoring dashboard."""
        self.performance_monitor = PerformanceMonitor()
        self.error_tracker = ErrorTracker()
        self.resource_monitor = ResourceMonitor()
        self.start_time = time.time()
        
        logger.info("MonitoringDashboard initialized")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get complete dashboard data.
        
        Returns:
            Dict with all monitoring data
        """
        uptime = time.time() - self.start_time
        
        return {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": uptime,
            "uptime_formatted": self._format_uptime(uptime),
            "performance": self.performance_monitor.get_metrics(),
            "errors": self.error_tracker.get_error_summary(),
            "resources": self.resource_monitor.get_resource_usage(),
            "health": self._calculate_health_status()
        }
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}h {minutes}m {secs}s"
    
    def _calculate_health_status(self) -> Dict[str, Any]:
        """
        Calculate overall system health.
        
        Returns:
            Dict with health status and indicators
        """
        # Get metrics
        perf_metrics = self.performance_monitor.get_metrics()
        error_summary = self.error_tracker.get_error_summary()
        resources = self.resource_monitor.get_resource_usage()
        
        # Calculate health indicators
        success_rates = perf_metrics.get("success_rate", {})
        avg_success_rate = (
            sum(success_rates.values()) / len(success_rates)
            if success_rates else 1.0
        )
        
        error_rate = error_summary.get("error_rate", 0)
        memory_percent = resources["system"]["memory_percent"]
        cpu_percent = resources["system"]["cpu_percent"]
        
        # Determine overall health
        health_score = 100.0
        issues = []
        
        # Success rate check
        if avg_success_rate < 0.9:
            health_score -= 20
            issues.append(f"Low success rate: {avg_success_rate:.1%}")
        
        # Error rate check
        if error_rate > 1.0:  # More than 1 error per minute
            health_score -= 15
            issues.append(f"High error rate: {error_rate:.2f}/min")
        
        # Memory check
        if memory_percent > 90:
            health_score -= 25
            issues.append(f"High memory usage: {memory_percent:.1f}%")
        elif memory_percent > 80:
            health_score -= 10
            issues.append(f"Elevated memory usage: {memory_percent:.1f}%")
        
        # CPU check
        if cpu_percent > 90:
            health_score -= 20
            issues.append(f"High CPU usage: {cpu_percent:.1f}%")
        elif cpu_percent > 80:
            health_score -= 10
            issues.append(f"Elevated CPU usage: {cpu_percent:.1f}%")
        
        # Determine status
        if health_score >= 90:
            status = "healthy"
        elif health_score >= 70:
            status = "degraded"
        elif health_score >= 50:
            status = "warning"
        else:
            status = "critical"
        
        return {
            "status": status,
            "health_score": max(0, health_score),
            "issues": issues,
            "indicators": {
                "success_rate": avg_success_rate,
                "error_rate": error_rate,
                "memory_percent": memory_percent,
                "cpu_percent": cpu_percent
            }
        }
    
    def export_metrics(self, filepath: str):
        """
        Export metrics to JSON file.
        
        Args:
            filepath: Path to export file
        """
        data = self.get_dashboard_data()
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Metrics exported to: {filepath}")


# Global monitoring instance
_monitoring_dashboard = None


def get_monitoring_dashboard() -> MonitoringDashboard:
    """Get the global monitoring dashboard instance."""
    global _monitoring_dashboard
    if _monitoring_dashboard is None:
        _monitoring_dashboard = MonitoringDashboard()
    return _monitoring_dashboard
