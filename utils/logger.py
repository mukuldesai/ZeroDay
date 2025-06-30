import os
import sys
from pathlib import Path
from loguru import logger
from datetime import datetime
from typing import Dict, Any, Optional

class ZeroDayLogger:
    """
    Centralized logging configuration for ZeroDay application
    Provides structured logging with multiple outputs and log levels
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        self.log_dir = Path(self.config.get("log_directory", "logs"))
        self.setup_logging()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default logging configuration"""
        return {
            "log_directory": "logs",
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "log_format": "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            "rotation": "100 MB",
            "retention": "30 days",
            "compression": "gz",
            "enable_console": True,logs directory
            "enable_file": True,
            "enable_json": False,
            "enable_structured": True
        }
    
    def setup_logging(self):
        """Setup loguru logging configuration"""
        
        logger.remove()
        
        
        self.log_dir.mkdir(exist_ok=True)
        
      
        if self.config.get("enable_console", True):
            logger.add(
                sys.stderr,
                level=self.config["log_level"],
                format=self._get_console_format(),
                colorize=True,
                backtrace=True,
                diagnose=True
            )
        
  
        if self.config.get("enable_file", True):
            logger.add(
                self.log_dir / "zeroday.log",
                level=self.config["log_level"],
                format=self.config["log_format"],
                rotation=self.config["rotation"],
                retention=self.config["retention"],
                compression=self.config["compression"],
                backtrace=True,
                diagnose=True
            )
        
       
        logger.add(
            self.log_dir / "errors.log",
            level="ERROR",
            format=self.config["log_format"],
            rotation=self.config["rotation"],
            retention=self.config["retention"],
            compression=self.config["compression"],
            backtrace=True,
            diagnose=True
        )
        
        
        logger.add(
            self.log_dir / "agents.log",
            level="INFO",
            format=self.config["log_format"],
            rotation=self.config["rotation"],
            retention=self.config["retention"],
            compression=self.config["compression"],
            filter=lambda record: "agent" in record["name"].lower(),
            backtrace=True,
            diagnose=True
        )
        
      
        logger.add(
            self.log_dir / "api.log",
            level="INFO",
            format=self.config["log_format"],
            rotation=self.config["rotation"],
            retention=self.config["retention"],
            compression=self.config["compression"],
            filter=lambda record: "api" in record["name"].lower() or "fastapi" in record["name"].lower(),
            backtrace=True,
            diagnose=True
        )
        
        
        logger.add(
            self.log_dir / "data_processing.log",
            level="DEBUG",
            format=self.config["log_format"],
            rotation=self.config["rotation"],
            retention=self.config["retention"],
            compression=self.config["compression"],
            filter=lambda record: any(keyword in record["name"].lower() for keyword in ["parser", "ingestor", "fetcher", "indexer"]),
            backtrace=True,
            diagnose=True
        )
        
    
        if self.config.get("enable_json", False):
            logger.add(
                self.log_dir / "structured.json",
                level="INFO",
                format="{message}",
                serialize=True,
                rotation=self.config["rotation"],
                retention=self.config["retention"],
                compression=self.config["compression"]
            )
    
    def _get_console_format(self) -> str:
        """Get console-friendly format with colors"""
        return (
            "<green>{time:HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
    
    def get_logger(self, name: str) -> Any:
        """Get a logger with specific name"""
        return logger.bind(name=name)
    
    def log_performance(self, operation: str, duration: float, metadata: Dict[str, Any] = None):
        """Log performance metrics"""
        perf_logger = logger.bind(
            operation=operation,
            duration=duration,
            metadata=metadata or {}
        )
        perf_logger.info(f"Performance: {operation} completed in {duration:.3f}s")
    
    def log_api_request(self, method: str, path: str, status_code: int, duration: float, user_id: str = None):
        """Log API request details"""
        api_logger = logger.bind(
            method=method,
            path=path,
            status_code=status_code,
            duration=duration,
            user_id=user_id
        )
        api_logger.info(f"API: {method} {path} -> {status_code} ({duration:.3f}s)")
    
    def log_agent_activity(self, agent_type: str, action: str, user_id: str = None, metadata: Dict[str, Any] = None):
        """Log agent activity"""
        agent_logger = logger.bind(
            agent_type=agent_type,
            action=action,
            user_id=user_id,
            metadata=metadata or {}
        )
        agent_logger.info(f"Agent: {agent_type} - {action}")
    
    def log_data_processing(self, processor: str, source: str, processed_count: int, duration: float):
        """Log data processing activities"""
        data_logger = logger.bind(
            processor=processor,
            source=source,
            processed_count=processed_count,
            duration=duration
        )
        data_logger.info(f"Data: {processor} processed {processed_count} items from {source} in {duration:.3f}s")
    
    def log_error_with_context(self, error: Exception, context: Dict[str, Any] = None):
        """Log error with additional context"""
        error_logger = logger.bind(
            error_type=type(error).__name__,
            context=context or {}
        )
        error_logger.error(f"Error: {str(error)}")
    
    def log_security_event(self, event_type: str, user_id: str = None, ip_address: str = None, details: Dict[str, Any] = None):
        """Log security-related events"""
        security_logger = logger.bind(
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            details=details or {}
        )
        security_logger.warning(f"Security: {event_type}")
    
    def log_business_metric(self, metric_name: str, value: Any, labels: Dict[str, str] = None):
        """Log business metrics"""
        metric_logger = logger.bind(
            metric_name=metric_name,
            value=value,
            labels=labels or {},
            timestamp=datetime.now().isoformat()
        )
        metric_logger.info(f"Metric: {metric_name} = {value}")
    
    def configure_for_development(self):
        """Configure logging for development environment"""
        logger.remove()
        
       
        logger.add(
            sys.stderr,
            level="DEBUG",
            format=self._get_console_format(),
            colorize=True,
            backtrace=True,
            diagnose=True
        )
        
        
        self.log_dir.mkdir(exist_ok=True)
        logger.add(
            self.log_dir / "dev.log",
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
            rotation="10 MB",
            retention="7 days"
        )
    
    def configure_for_production(self):
        """Configure logging for production environment"""
        logger.remove()
        
  
        logger.add(
            sys.stderr,
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}",
            colorize=False,
            backtrace=False,
            diagnose=False
        )
        
       
        self.log_dir.mkdir(exist_ok=True)
        
       
        logger.add(
            self.log_dir{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
            rotation="500 MB",
            retention="90 days",
            compres / "application.log",
            level="INFO",
            format="sion="gz"
        )
        
       
        logger.add(
            self.log_dir / "error.log",
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
            rotation="100 MB",
            retention="180 days",
            compression="gz"
        )
        
      
        logger.add(
            self.log_dir / "structured.json",
            level="WARNING",
            serialize=True,
            rotation="100 MB",
            retention="90 days",
            compression="gz"
        )
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Get logging statistics"""
        log_files = list(self.log_dir.glob("*.log*"))
        
        stats = {
            "log_directory": str(self.log_dir),
            "total_log_files": len(log_files),
            "log_files": [],
            "total_size_mb": 0,
            "configuration": self.config
        }
        
        for log_file in log_files:
            try:
                size_bytes = log_file.stat().st_size
                size_mb = size_bytes / (1024 * 1024)
                modified = datetime.fromtimestamp(log_file.stat().st_mtime)
                
                stats["log_files"].append({
                    "name": log_file.name,
                    "size_mb": round(size_mb, 2),
                    "modified": modified.isoformat()
                })
                
                stats["total_size_mb"] += size_mb
                
            except Exception as e:
                logger.error(f"Error getting stats for {log_file}: {e}")
        
        stats["total_size_mb"] = round(stats["total_size_mb"], 2)
        return stats
    
    def cleanup_old_logs(self, days: int = 30):
        """Clean up old log files"""
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        cleaned_files = []
        
        for log_file in self.log_dir.glob("*.log*"):
            try:
                if log_file.stat().st_mtime < cutoff_date:
                    log_file.unlink()
                    cleaned_files.append(log_file.name)
            except Exception as e:
                logger.error(f"Error cleaning up {log_file}: {e}")
        
        if cleaned_files:
            logger.info(f"Cleaned up {len(cleaned_files)} old log files: {cleaned_files}")
        
        return cleaned_files


_logger_instance = None

def setup_logging(config: Dict[str, Any] = None, environment: str = "development") -> ZeroDayLogger:
    """Setup global logging configuration"""
    global _logger_instance
    
    _logger_instance = ZeroDayLogger(config)
    
    if environment == "production":
        _logger_instance.configure_for_production()
    else:
        _logger_instance.configure_for_development()
    
    logger.info(f"Logging configured for {environment} environment")
    return _logger_instance

def get_logger(name: str = None):
    """Get logger instance"""
    if _logger_instance is None:
        setup_logging()
    
    if name:
        return logger.bind(name=name)
    return logger

def log_performance(operation: str, duration: float, metadata: Dict[str, Any] = None):
    """Convenience function for performance logging"""
    if _logger_instance:
        _logger_instance.log_performance(operation, duration, metadata)

def log_api_request(method: str, path: str, status_code: int, duration: float, user_id: str = None):
    """Convenience function for API request logging"""
    if _logger_instance:
        _logger_instance.log_api_request(method, path, status_code, duration, user_id)

def log_agent_activity(agent_type: str, action: str, user_id: str = None, metadata: Dict[str, Any] = None):
    """Convenience function for agent activity logging"""
    if _logger_instance:
        _logger_instance.log_agent_activity(agent_type, action, user_id, metadata)

def log_data_processing(processor: str, source: str, processed_count: int, duration: float):
    """Convenience function for data processing logging"""
    if _logger_instance:
        _logger_instance.log_data_processing(processor, source, processed_count, duration)

def log_error_with_context(error: Exception, context: Dict[str, Any] = None):
    """Convenience function for error logging with context"""
    if _logger_instance:
        _logger_instance.log_error_with_context(error, context)

def log_security_event(event_type: str, user_id: str = None, ip_address: str = None, details: Dict[str, Any] = None):
    """Convenience function for security event logging"""
    if _logger_instance:
        _logger_instance.log_security_event(event_type, user_id, ip_address, details)

def log_business_metric(metric_name: str, value: Any, labels: Dict[str, str] = None):
    """Convenience function for business metric logging"""
    if _logger_instance:
        _logger_instance.log_business_metric(metric_name, value, labels)


class LogContext:
    """Context manager for automatic operation logging"""
    
    def __init__(self, operation: str, metadata: Dict[str, Any] = None):
        self.operation = operation
        self.metadata = metadata or {}
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        logger.debug(f"Starting operation: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            log_performance(self.operation, duration, self.metadata)
        else:
            logger.error(f"Operation failed: {self.operation} after {duration:.3f}s - {exc_val}")

class ApiLogContext:
    """Context manager for API request logging"""
    
    def __init__(self, method: str, path: str, user_id: str = None):
        self.method = method
        self.path = path
        self.user_id = user_id
        self.start_time = None
        self.status_code = 200
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def set_status_code(self, status_code: int):
        self.status_code = status_code
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is not None:
            self.status_code = 500
        
        log_api_request(self.method, self.path, self.status_code, duration, self.user_id)


__all__ = [
    "ZeroDayLogger",
    "setup_logging",
    "get_logger",
    "log_performance",
    "log_api_request",
    "log_agent_activity",
    "log_data_processing",
    "log_error_with_context",
    "log_security_event",
    "log_business_metric",
    "LogContext",
    "ApiLogContext"
]