#!/usr/bin/env python3
"""
Adaptive Error Handler - Development vs Production Error Handling

In development: Let it crash! Errors are bugs to be fixed.
In production: Stay solid. Log, notify, gracefully degrade.

The same code behaves differently based on APP_MODE environment variable.
"""

import os
import sys
import json
import traceback
from datetime import datetime
from pathlib import Path
from functools import wraps
from typing import Callable, Any, Optional
import logging

# Configure based on environment
APP_MODE = os.environ.get("APP_MODE", "production")
IS_DEV = APP_MODE.lower() in ("development", "dev", "debug")

# Setup logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG if IS_DEV else logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f"errors_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger(__name__)


class ErrorPattern:
    """Captures error patterns for future auto-fixing."""

    def __init__(self, error: Exception, context: dict):
        self.error_type = type(error).__name__
        self.message = str(error)
        self.traceback = traceback.format_exc()
        self.context = context
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "error_type": self.error_type,
            "message": self.message,
            "traceback": self.traceback,
            "context": self.context,
            "timestamp": self.timestamp
        }

    def save_pattern(self):
        """Save error pattern for future analysis and auto-fixing."""
        patterns_file = LOG_DIR / "error_patterns.jsonl"
        with open(patterns_file, "a") as f:
            f.write(json.dumps(self.to_dict()) + "\n")


class DevelopmentErrorHandler:
    """Development mode: Crash loudly and learn."""

    @staticmethod
    def handle(error: Exception, func_name: str, context: dict) -> None:
        logger.error(f"💥 CRASH in {func_name}: {type(error).__name__}")
        logger.error(f"Message: {error}")

        # Log pattern for future auto-fixing
        pattern = ErrorPattern(error, context)
        pattern.save_pattern()
        logger.info(f"📝 Error pattern saved to {LOG_DIR / 'error_patterns.jsonl'}")

        # Re-raise to crash the application
        logger.info("🔍 Development mode: Re-raising exception for debugging")
        raise


class ProductionErrorHandler:
    """Production mode: Stay solid, log everything, notify developers."""

    @staticmethod
    def handle(error: Exception, func_name: str, context: dict) -> Any:
        # Sanitize error message (remove sensitive data)
        safe_message = ProductionErrorHandler._sanitize_error(error)

        # Log securely (no sensitive data)
        logger.error(f"Error in {func_name}: {safe_message}")
        logger.debug(f"Full traceback: {traceback.format_exc()}")

        # Save pattern for offline analysis
        pattern = ErrorPattern(error, {
            "function": func_name,
            "error_type": type(error).__name__
            # Deliberately exclude sensitive context in production
        })
        pattern.save_pattern()

        # TODO: Notify developers (email, Sentry, PagerDuty, etc.)
        ProductionErrorHandler._notify_developers(error, func_name)

        # Return safe fallback value
        return None

    @staticmethod
    def _sanitize_error(error: Exception) -> str:
        """Remove potentially sensitive information from error message."""
        message = str(error)
        # Remove file paths
        message = message.replace(str(Path.home()), "~")
        # Remove potential tokens/keys (simple pattern)
        import re
        message = re.sub(r'[A-Za-z0-9]{20,}', '[REDACTED]', message)
        return message

    @staticmethod
    def _notify_developers(error: Exception, func_name: str):
        """Notify developers of production error (stub for now)."""
        # In real production, integrate with:
        # - Sentry: sentry_sdk.capture_exception(error)
        # - Email: send_email(admin, subject, body)
        # - PagerDuty: trigger_incident(error)
        logger.info(f"🔔 Developer notification triggered for {type(error).__name__} in {func_name}")


def adaptive_error_handler(fallback_value: Any = None, context: Optional[dict] = None):
    """
    Decorator for adaptive error handling.

    Development mode: Crashes with full stack trace
    Production mode: Returns fallback value and logs securely

    Usage:
        @adaptive_error_handler(fallback_value={})
        def risky_function():
            return dangerous_operation()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as error:
                func_name = func.__name__
                error_context = context or {
                    "function": func_name,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys())
                }

                if IS_DEV:
                    DevelopmentErrorHandler.handle(error, func_name, error_context)
                else:
                    return ProductionErrorHandler.handle(error, func_name, error_context) or fallback_value

        return wrapper
    return decorator


class AdaptiveErrorContext:
    """
    Context manager for adaptive error handling.

    Usage:
        with AdaptiveErrorContext("database_operation"):
            risky_database_call()
    """

    def __init__(self, operation_name: str, fallback_value: Any = None):
        self.operation_name = operation_name
        self.fallback_value = fallback_value

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            return False  # No exception

        error_context = {
            "operation": self.operation_name,
            "error_type": exc_type.__name__
        }

        if IS_DEV:
            DevelopmentErrorHandler.handle(exc_val, self.operation_name, error_context)
            return False  # Let exception propagate
        else:
            ProductionErrorHandler.handle(exc_val, self.operation_name, error_context)
            return True  # Suppress exception


def analyze_error_patterns(min_occurrences: int = 2):
    """
    Analyze collected error patterns to identify frequent issues.

    This feeds the feedback loop: frequently occurring errors should
    be added to ERROR_DATABASE for automatic fixing.
    """
    patterns_file = LOG_DIR / "error_patterns.jsonl"

    if not patterns_file.exists():
        print("No error patterns found yet.")
        return

    # Load all patterns
    patterns = []
    with open(patterns_file, "r") as f:
        for line in f:
            patterns.append(json.loads(line))

    # Count by error type
    error_counts = {}
    for pattern in patterns:
        error_type = pattern["error_type"]
        error_counts[error_type] = error_counts.get(error_type, 0) + 1

    # Report frequent errors
    print(f"\n📊 Error Pattern Analysis ({len(patterns)} total errors)")
    print("=" * 60)

    frequent_errors = {k: v for k, v in error_counts.items() if v >= min_occurrences}

    if frequent_errors:
        print(f"\n🔥 Frequent Errors (≥{min_occurrences} occurrences):")
        for error_type, count in sorted(frequent_errors.items(), key=lambda x: x[1], reverse=True):
            print(f"  {error_type}: {count} occurrences")
            print(f"    → Should add to ERROR_DATABASE for auto-fixing")

    # Show unique errors
    unique_errors = {k: v for k, v in error_counts.items() if v == 1}
    if unique_errors:
        print(f"\n💡 Unique Errors ({len(unique_errors)}):")
        for error_type in sorted(unique_errors.keys()):
            print(f"  {error_type}")

    print("\n" + "=" * 60)
    return error_counts


# Example usage and testing
if __name__ == "__main__":
    print(f"🔧 Adaptive Error Handler running in {APP_MODE.upper()} mode")
    print(f"   Development mode: {IS_DEV}")
    print()

    # Example 1: Decorator usage
    @adaptive_error_handler(fallback_value={})
    def parse_config(filename: str) -> dict:
        """Parse JSON config file."""
        with open(filename) as f:
            return json.load(f)

    # Example 2: Context manager usage
    def process_data():
        """Process data with error handling."""
        with AdaptiveErrorContext("data_processing"):
            # This might fail
            result = 10 / 0
            return result

    # Test the decorator
    print("Testing decorator with missing file...")
    config = parse_config("nonexistent.json")
    print(f"Result: {config}")

    if not IS_DEV:
        # In production, we get the fallback value
        print("✅ Production mode: graceful degradation worked!")

    print("\nTesting context manager with zero division...")
    process_data()

    if not IS_DEV:
        print("✅ Production mode: error suppressed, execution continued")

    # Show analytics
    print("\n" + "=" * 60)
    analyze_error_patterns(min_occurrences=1)
