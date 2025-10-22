"""
ACT MCP Logger

Centralized logging for MCP operations with structured output.
"""

import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class LogLevel(Enum):
    """Log level enumeration"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


class MCPLogger:
    """Structured logger for MCP operations"""

    def __init__(self, operation: str = "unknown", verbose: bool = False):
        """
        Initialize logger

        Args:
            operation: Operation name (e.g., "execute_node", "sync_catalog")
            verbose: Enable verbose logging
        """
        self.operation = operation
        self.verbose = verbose
        self.start_time = datetime.utcnow()
        self.logs = []

    def log(self, level: LogLevel, message: str, **kwargs):
        """
        Log a message

        Args:
            level: Log level
            message: Log message
            **kwargs: Additional context
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "level": level.value,
            "operation": self.operation,
            "message": message,
            **kwargs
        }

        self.logs.append(log_entry)

        if self.verbose:
            print(json.dumps(log_entry), file=sys.stderr)

    def debug(self, message: str, **kwargs):
        """Log debug message"""
        if self.verbose:
            self.log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log info message"""
        self.log(LogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.log(LogLevel.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message"""
        self.log(LogLevel.ERROR, message, **kwargs)

    def success(self, message: str, **kwargs):
        """Log success message"""
        self.log(LogLevel.SUCCESS, message, **kwargs)

    def get_duration(self) -> float:
        """Get execution duration in seconds"""
        return (datetime.utcnow() - self.start_time).total_seconds()

    def get_logs(self) -> list:
        """Get all logs"""
        return self.logs

    def output_result(self, success: bool, result: Optional[Dict[str, Any]] = None,
                      error: Optional[str] = None):
        """
        Output final result as JSON to stdout

        Args:
            success: Whether operation succeeded
            result: Result data (if successful)
            error: Error message (if failed)
        """
        output = {
            "success": success,
            "operation": self.operation,
            "duration": self.get_duration(),
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }

        if success:
            output["result"] = result or {}
        else:
            output["error"] = error or "Unknown error"

        if self.verbose:
            output["logs"] = self.logs

        print(json.dumps(output, default=str))


def get_logger(operation: str = "unknown", verbose: bool = False) -> MCPLogger:
    """
    Get a logger instance

    Args:
        operation: Operation name
        verbose: Enable verbose logging

    Returns:
        MCPLogger instance
    """
    return MCPLogger(operation, verbose)
