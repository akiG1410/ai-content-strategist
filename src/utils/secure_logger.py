"""
Secure logging with PII sanitization for Streamlit Cloud
"""

import streamlit as st
import re
from datetime import datetime
from typing import Optional, Any, Dict
from enum import Enum


class LogLevel(Enum):
    """Log level enumeration"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class SecureLogger:
    """Secure logger with PII sanitization"""

    # PII patterns to sanitize
    PII_PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        'api_key': r'\b(sk-[a-zA-Z0-9]{32,})\b',
        'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    }

    def __init__(self):
        """Initialize secure logger"""
        # Lazy import to avoid circular dependency
        from ..config.secure_config import config
        self.log_config = config.get_logging_config()
        self.sanitize_pii = self.log_config['sanitize_pii']

        # Initialize session state for logs
        if 'app_logs' not in st.session_state:
            st.session_state.app_logs = []

    def _sanitize_message(self, message: str) -> str:
        """
        Sanitize message to remove PII

        Args:
            message: Original message

        Returns:
            Sanitized message
        """
        if not self.sanitize_pii:
            return message

        sanitized = message

        # Replace each PII pattern
        for pii_type, pattern in self.PII_PATTERNS.items():
            sanitized = re.sub(
                pattern,
                f"[REDACTED_{pii_type.upper()}]",
                sanitized,
                flags=re.IGNORECASE
            )

        return sanitized

    def _format_log_entry(
        self,
        level: LogLevel,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Format log entry

        Args:
            level: Log level
            message: Log message
            context: Optional context dictionary

        Returns:
            Formatted log entry
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{timestamp}] [{level.value}] {message}"

        if context and self.log_config['include_user_context']:
            sanitized_context = {
                k: self._sanitize_message(str(v))
                for k, v in context.items()
            }
            formatted += f" | Context: {sanitized_context}"

        return formatted

    def _should_log(self, level: LogLevel) -> bool:
        """
        Check if message should be logged based on configured level

        Args:
            level: Log level

        Returns:
            True if should log
        """
        level_hierarchy = {
            'DEBUG': 0,
            'INFO': 1,
            'WARNING': 2,
            'ERROR': 3,
            'CRITICAL': 4
        }

        configured_level = self.log_config['level']
        return level_hierarchy[level.value] >= level_hierarchy[configured_level]

    def _log(
        self,
        level: LogLevel,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        show_in_ui: bool = False
    ):
        """
        Internal log method

        Args:
            level: Log level
            message: Log message
            context: Optional context
            show_in_ui: Whether to display in Streamlit UI
        """
        if not self._should_log(level):
            return

        # Sanitize message
        safe_message = self._sanitize_message(message)

        # Format entry
        log_entry = self._format_log_entry(level, safe_message, context)

        # Store in session state
        st.session_state.app_logs.append({
            'timestamp': datetime.now(),
            'level': level.value,
            'message': safe_message,
            'context': context,
            'entry': log_entry
        })

        # Keep only last 100 logs
        if len(st.session_state.app_logs) > 100:
            st.session_state.app_logs = st.session_state.app_logs[-100:]

        # Show in UI if requested
        if show_in_ui:
            if level == LogLevel.ERROR or level == LogLevel.CRITICAL:
                st.error(safe_message)
            elif level == LogLevel.WARNING:
                st.warning(safe_message)
            elif level == LogLevel.INFO:
                st.info(safe_message)
            else:
                st.write(safe_message)

    def debug(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        show_in_ui: bool = False
    ):
        """Log debug message"""
        self._log(LogLevel.DEBUG, message, context, show_in_ui)

    def info(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        show_in_ui: bool = False
    ):
        """Log info message"""
        self._log(LogLevel.INFO, message, context, show_in_ui)

    def warning(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        show_in_ui: bool = True
    ):
        """Log warning message"""
        self._log(LogLevel.WARNING, message, context, show_in_ui)

    def error(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        show_in_ui: bool = True
    ):
        """Log error message"""
        self._log(LogLevel.ERROR, message, context, show_in_ui)

    def critical(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        show_in_ui: bool = True
    ):
        """Log critical message"""
        self._log(LogLevel.CRITICAL, message, context, show_in_ui)

    def get_logs(
        self,
        level: Optional[LogLevel] = None,
        limit: int = 50
    ) -> list[Dict[str, Any]]:
        """
        Get recent logs

        Args:
            level: Optional filter by log level
            limit: Maximum number of logs to return

        Returns:
            List of log entries
        """
        logs = st.session_state.app_logs

        if level:
            logs = [log for log in logs if log['level'] == level.value]

        return logs[-limit:]

    def clear_logs(self):
        """Clear all logs"""
        st.session_state.app_logs = []

    def show_log_viewer(self):
        """Display log viewer in Streamlit expander"""
        with st.expander("📋 Application Logs"):
            # Log level filter
            selected_level = st.selectbox(
                "Filter by level",
                options=["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                index=0
            )

            # Get logs
            if selected_level == "ALL":
                logs = self.get_logs(limit=50)
            else:
                logs = self.get_logs(level=LogLevel[selected_level], limit=50)

            # Display logs
            if not logs:
                st.info("No logs available")
            else:
                st.text(f"Showing {len(logs)} most recent logs")

                # Display in reverse chronological order
                for log in reversed(logs):
                    level_emoji = {
                        'DEBUG': '🔍',
                        'INFO': 'ℹ️',
                        'WARNING': '⚠️',
                        'ERROR': '❌',
                        'CRITICAL': '🚨'
                    }

                    emoji = level_emoji.get(log['level'], '•')
                    st.text(f"{emoji} {log['entry']}")

            # Clear logs button
            if st.button("Clear Logs"):
                self.clear_logs()
                st.rerun()


# Global logger instance
logger = SecureLogger()


def log_api_call(
    endpoint: str,
    method: str = "POST",
    success: bool = True,
    error: Optional[str] = None
):
    """
    Log API call

    Args:
        endpoint: API endpoint
        method: HTTP method
        success: Whether call was successful
        error: Optional error message
    """
    context = {
        'endpoint': endpoint,
        'method': method,
        'success': success
    }

    if success:
        logger.info(f"API call successful: {method} {endpoint}", context)
    else:
        logger.error(f"API call failed: {method} {endpoint} - {error}", context)


def log_user_action(action: str, details: Optional[Dict[str, Any]] = None):
    """
    Log user action

    Args:
        action: Action description
        details: Optional action details
    """
    logger.info(f"User action: {action}", context=details)


def log_generation_start(brand_name: str, phase: str):
    """
    Log content generation start

    Args:
        brand_name: Brand name
        phase: Generation phase
    """
    context = {'brand': brand_name, 'phase': phase}
    logger.info(f"Starting {phase} generation for {brand_name}", context)


def log_generation_complete(brand_name: str, phase: str, duration: float):
    """
    Log content generation completion

    Args:
        brand_name: Brand name
        phase: Generation phase
        duration: Duration in seconds
    """
    context = {
        'brand': brand_name,
        'phase': phase,
        'duration_seconds': duration
    }
    logger.info(
        f"Completed {phase} generation for {brand_name} in {duration:.2f}s",
        context
    )


def log_error(error: Exception, context: Optional[Dict[str, Any]] = None):
    """
    Log exception

    Args:
        error: Exception object
        context: Optional context
    """
    error_msg = f"{type(error).__name__}: {str(error)}"
    logger.error(error_msg, context=context, show_in_ui=True)
