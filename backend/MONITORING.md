# Monitoring System

## Overview

The FunctionGemma integration includes a comprehensive monitoring system that tracks:

- **Performance Metrics**: Operation durations, throughput, success rates
- **Error Tracking**: Detailed error logs with context and stack traces
- **Resource Usage**: CPU, memory, disk usage
- **System Health**: Overall health score and status indicators

## Features

### 1. Performance Monitoring

Tracks all operations with detailed metrics:

- Operation type and function name
- Start time, end time, duration
- Success/failure status
- Parameters and results
- Throughput (operations per second)
- Average durations by operation type

### 2. Error Tracking

Comprehensive error logging with:

- Error type and message
- Function name and parameters
- Stack traces
- Additional context
- Error frequency tracking
- Error rate calculation

### 3. Resource Monitoring

System resource usage tracking:

- **Process-level**: CPU, memory, threads
- **System-level**: Total memory, available memory, disk usage
- Real-time updates
- Historical tracking

### 4. Health Status

Automated health assessment based on:

- Success rate (target: >90%)
- Error rate (target: <1 error/min)
- Memory usage (warning: >80%, critical: >90%)
- CPU usage (warning: >80%, critical: >90%)

Health statuses:
- **Healthy**: Score ≥90, all systems normal
- **Degraded**: Score 70-89, minor issues
- **Warning**: Score 50-69, attention needed
- **Critical**: Score <50, immediate action required

## Usage

### Accessing the Dashboard

Start the service and navigate to:

```
http://localhost:5000/monitoring
```

The dashboard provides:
- Real-time metrics
- Auto-refresh every 5 seconds
- Recent operations list
- Recent errors list
- Health status and issues

### API Endpoints

#### Get Dashboard Data

```bash
curl http://localhost:5000/monitoring/dashboard
```

Returns complete monitoring data in JSON format.

#### Export Metrics

```bash
curl http://localhost:5000/monitoring/export -O
```

Downloads metrics as a JSON file.

### Programmatic Access

```python
from monitoring import get_monitoring_dashboard

# Get dashboard instance
dashboard = get_monitoring_dashboard()

# Get current metrics
data = dashboard.get_dashboard_data()

# Access specific monitors
perf_metrics = dashboard.performance_monitor.get_metrics()
error_summary = dashboard.error_tracker.get_error_summary()
resources = dashboard.resource_monitor.get_resource_usage()

# Export metrics to file
dashboard.export_metrics('metrics.json')
```

## Integration

### Automatic Integration

Monitoring is automatically integrated into:

- **Function Executor**: All function calls are tracked
- **Error Handler**: All errors are logged with context
- **Service Startup**: Monitoring starts automatically

### Manual Integration

To add monitoring to custom code:

```python
from monitoring import get_monitoring_dashboard

dashboard = get_monitoring_dashboard()

# Start tracking an operation
operation_id = dashboard.performance_monitor.start_operation(
    operation_type="custom_operation",
    function_name="my_function",
    parameters={"param1": "value1"}
)

try:
    # Your code here
    result = do_something()
    
    # Mark as successful
    dashboard.performance_monitor.complete_operation(
        operation_id,
        success=True,
        result=result
    )
    
except Exception as e:
    # Log error
    dashboard.error_tracker.log_error(
        error_type="custom_error",
        error_message=str(e),
        function_name="my_function",
        parameters={"param1": "value1"},
        stack_trace=traceback.format_exc()
    )
    
    # Mark as failed
    dashboard.performance_monitor.complete_operation(
        operation_id,
        success=False,
        error_message=str(e)
    )
```

## Monitoring Data Structure

### Dashboard Data

```json
{
  "timestamp": "2025-12-27T20:00:00",
  "uptime_seconds": 3600,
  "uptime_formatted": "1h 0m 0s",
  "performance": {
    "total_operations": 150,
    "operations_by_type": {
      "function_call": 120,
      "model_inference": 30
    },
    "success_rate": {
      "function_call": 0.95,
      "model_inference": 0.90
    },
    "average_durations": {
      "function_call": 0.125,
      "model_inference": 1.5
    },
    "throughput": {
      "function_call": 2.0,
      "model_inference": 0.5
    },
    "recent_operations": [...]
  },
  "errors": {
    "total_errors": 10,
    "errors_by_type": {
      "parameter_validation": 5,
      "execution_error": 3,
      "type_error": 2
    },
    "error_rate": 0.16,
    "recent_errors": [...]
  },
  "resources": {
    "process": {
      "memory_mb": 2048,
      "memory_percent": 15.5,
      "cpu_percent": 25.0,
      "threads": 8
    },
    "system": {
      "memory_total_mb": 16384,
      "memory_available_mb": 8192,
      "memory_percent": 50.0,
      "cpu_percent": 35.0,
      "disk_total_gb": 500,
      "disk_used_gb": 250,
      "disk_percent": 50.0
    }
  },
  "health": {
    "status": "healthy",
    "health_score": 95.0,
    "issues": [],
    "indicators": {
      "success_rate": 0.93,
      "error_rate": 0.16,
      "memory_percent": 50.0,
      "cpu_percent": 35.0
    }
  }
}
```

## Logging

### Log Files

Logs are written to:
- `backend/functiongemma_service.log` - All service logs

### Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages (non-critical issues)
- **ERROR**: Error messages (failures)

### Configuring Logging

```python
import logging

# Set log level
logging.getLogger('monitoring').setLevel(logging.DEBUG)

# Add custom handler
handler = logging.FileHandler('custom.log')
logging.getLogger('monitoring').addHandler(handler)
```

## Performance Considerations

### Memory Usage

The monitoring system uses minimal memory:
- ~10MB for monitoring data structures
- Configurable history limits (default: 1000 operations, 500 errors)
- Automatic cleanup of old data

### CPU Overhead

Monitoring adds minimal CPU overhead:
- <1% CPU for tracking operations
- <0.1ms per operation
- Async resource monitoring

### Optimization

To reduce overhead:

```python
# Reduce history size
dashboard = MonitoringDashboard()
dashboard.performance_monitor = PerformanceMonitor(max_history=100)
dashboard.error_tracker = ErrorTracker(max_errors=50)

# Disable auto-refresh in dashboard
# (uncheck "Auto-refresh" in web UI)
```

## Alerts and Notifications

### Health Issues

The system automatically detects:
- Low success rate (<90%)
- High error rate (>1 error/min)
- High memory usage (>80%)
- High CPU usage (>80%)

Issues are displayed in:
- Dashboard UI (Health Issues section)
- Dashboard data JSON (health.issues array)
- Service logs (WARNING level)

### Custom Alerts

To implement custom alerts:

```python
from monitoring import get_monitoring_dashboard

dashboard = get_monitoring_dashboard()

# Check health periodically
data = dashboard.get_dashboard_data()
health = data['health']

if health['status'] in ['warning', 'critical']:
    # Send alert (email, Slack, etc.)
    send_alert(f"Health status: {health['status']}")
    
    # Log issues
    for issue in health['issues']:
        logger.warning(f"Health issue: {issue}")
```

## Troubleshooting

### Dashboard Not Loading

**Problem**: Dashboard page doesn't load

**Solutions**:
1. Check service is running: `curl http://localhost:5000/health`
2. Verify port is correct (default: 5000)
3. Check firewall settings
4. Look for errors in service logs

### No Data Showing

**Problem**: Dashboard shows "Loading..." or "--"

**Solutions**:
1. Check `/monitoring/dashboard` endpoint: `curl http://localhost:5000/monitoring/dashboard`
2. Verify monitoring is initialized
3. Check browser console for errors
4. Try manual refresh

### High Memory Usage

**Problem**: Monitoring using too much memory

**Solutions**:
1. Reduce history limits
2. Export and clear old metrics
3. Restart service periodically
4. Monitor system resources

### Missing Operations

**Problem**: Some operations not showing in dashboard

**Solutions**:
1. Verify monitoring integration in code
2. Check operation_id is being completed
3. Look for exceptions in logs
4. Increase max_history limit

## Best Practices

### 1. Regular Monitoring

- Check dashboard daily
- Review error trends weekly
- Export metrics monthly for analysis

### 2. Performance Optimization

- Monitor average durations
- Identify slow operations
- Optimize based on metrics

### 3. Error Management

- Review recent errors regularly
- Track error patterns
- Fix recurring issues

### 4. Resource Management

- Monitor memory trends
- Watch for memory leaks
- Plan capacity based on usage

### 5. Health Maintenance

- Address health issues promptly
- Keep health score >90
- Investigate degraded status

## Examples

### Example 1: Check System Health

```python
from monitoring import get_monitoring_dashboard

dashboard = get_monitoring_dashboard()
data = dashboard.get_dashboard_data()

print(f"Status: {data['health']['status']}")
print(f"Score: {data['health']['health_score']}")
print(f"Issues: {data['health']['issues']}")
```

### Example 2: Track Custom Operation

```python
from monitoring import get_monitoring_dashboard
import time

dashboard = get_monitoring_dashboard()

# Start operation
op_id = dashboard.performance_monitor.start_operation(
    operation_type="data_processing",
    function_name="process_data",
    parameters={"file": "data.csv"}
)

# Do work
time.sleep(1)

# Complete operation
dashboard.performance_monitor.complete_operation(
    op_id,
    success=True,
    result={"rows_processed": 1000}
)
```

### Example 3: Export Metrics for Analysis

```python
from monitoring import get_monitoring_dashboard
import json

dashboard = get_monitoring_dashboard()

# Export to file
dashboard.export_metrics('metrics.json')

# Load and analyze
with open('metrics.json') as f:
    data = json.load(f)
    
# Analyze performance
perf = data['performance']
print(f"Total operations: {perf['total_operations']}")
print(f"Average success rate: {sum(perf['success_rate'].values()) / len(perf['success_rate'])}")
```

## Support

For issues or questions:

1. Check this documentation
2. Review service logs
3. Check dashboard for health issues
4. Consult [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## Version

**Version:** 1.0.0  
**Last Updated:** December 2025  
**Status:** Production Ready
