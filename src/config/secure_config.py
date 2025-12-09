"""
Secure configuration management for Streamlit Cloud
Handles environment detection and secrets management
"""

import streamlit as st
import os
from typing import Optional, Dict, Any
from enum import Enum


class Environment(Enum):
    """Application environment types"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class SecureConfig:
    """Secure configuration manager"""

    def __init__(self):
        """Initialize configuration"""
        self.environment = self._detect_environment()

    def _detect_environment(self) -> Environment:
        """
        Detect current environment

        Returns:
            Environment enum value
        """
        # Check for Streamlit Cloud indicators
        if os.getenv('STREAMLIT_SHARING_MODE') or os.getenv('STREAMLIT_RUNTIME_ENV') == 'cloud':
            return Environment.PRODUCTION

        # Check for explicit environment variable
        env = os.getenv('ENVIRONMENT', 'development').lower()

        if env in ['prod', 'production']:
            return Environment.PRODUCTION
        elif env == 'testing':
            return Environment.TESTING
        else:
            return Environment.DEVELOPMENT

    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == Environment.PRODUCTION

    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == Environment.DEVELOPMENT

    def is_testing(self) -> bool:
        """Check if running in testing"""
        return self.environment == Environment.TESTING

    def get_api_key(self, service: str = "openrouter") -> Optional[str]:
        """
        Get API key securely

        Args:
            service: Service name (e.g., "openrouter")

        Returns:
            API key or None if not found
        """
        key_name = f"{service.upper()}_API_KEY"

        # Try Streamlit secrets first (production)
        try:
            if hasattr(st, 'secrets') and key_name in st.secrets:
                return st.secrets[key_name]
        except Exception:
            pass

        # Fall back to environment variables (development)
        return os.getenv(key_name)

    def get_beta_password(self) -> Optional[str]:
        """
        Get beta password securely

        Returns:
            Beta password or None if not configured
        """
        # Try Streamlit secrets first
        try:
            if hasattr(st, 'secrets') and 'BETA_PASSWORD' in st.secrets:
                return st.secrets['BETA_PASSWORD']
        except Exception:
            pass

        # Fall back to environment variable
        return os.getenv('BETA_PASSWORD')

    def get_rate_limit_config(self) -> Dict[str, int]:
        """
        Get rate limiting configuration

        Returns:
            Dictionary with max_requests and window_seconds
        """
        if self.is_production():
            # Strict limits in production
            return {
                'max_requests': 5,
                'window_seconds': 3600  # 1 hour
            }
        else:
            # Relaxed limits in development
            return {
                'max_requests': 999999,
                'window_seconds': 1
            }

    def get_model_config(self) -> Dict[str, Any]:
        """
        Get AI model configuration

        Returns:
            Model configuration dictionary
        """
        return {
            'model': 'anthropic/claude-sonnet-4-5:beta',
            'temperature': 0.7,
            'max_tokens': 16000,
            'timeout': 120  # 2 minutes
        }

    def get_retry_config(self) -> Dict[str, Any]:
        """
        Get retry configuration for API calls

        Returns:
            Retry configuration dictionary
        """
        return {
            'max_retries': 3,
            'backoff_factor': 2,  # 2^n seconds between retries
            'retry_on_status': [429, 500, 502, 503, 504]
        }

    def get_file_config(self) -> Dict[str, Any]:
        """
        Get file handling configuration

        Returns:
            File configuration dictionary
        """
        if self.is_production():
            return {
                'use_temp_files': True,
                'auto_cleanup': True,
                'max_file_size_mb': 10
            }
        else:
            return {
                'use_temp_files': False,
                'auto_cleanup': False,
                'max_file_size_mb': 50
            }

    def get_logging_config(self) -> Dict[str, Any]:
        """
        Get logging configuration

        Returns:
            Logging configuration dictionary
        """
        if self.is_production():
            return {
                'level': 'INFO',
                'sanitize_pii': True,
                'include_timestamps': True,
                'include_user_context': False
            }
        else:
            return {
                'level': 'DEBUG',
                'sanitize_pii': False,
                'include_timestamps': True,
                'include_user_context': True
            }

    def validate_config(self) -> tuple[bool, list[str]]:
        """
        Validate that all required configuration is present

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check API key
        api_key = self.get_api_key()
        if not api_key:
            errors.append("OPENROUTER_API_KEY not found in secrets or environment")

        # Check API key format
        if api_key and not api_key.startswith('sk-'):
            errors.append("OPENROUTER_API_KEY appears to be invalid (should start with 'sk-')")

        # Production-specific checks
        if self.is_production():
            # Check beta password if in production
            if not self.get_beta_password():
                errors.append("BETA_PASSWORD not configured for production")

        return (len(errors) == 0, errors)

    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get summary of current configuration (for debugging)

        Returns:
            Configuration summary dictionary
        """
        api_key = self.get_api_key()
        beta_password = self.get_beta_password()

        return {
            'environment': self.environment.value,
            'api_key_configured': bool(api_key),
            'api_key_preview': f"{api_key[:10]}..." if api_key else "Not configured",
            'beta_password_configured': bool(beta_password),
            'rate_limit_config': self.get_rate_limit_config(),
            'model_config': self.get_model_config(),
            'file_config': self.get_file_config(),
            'logging_config': self.get_logging_config()
        }


# Global configuration instance
config = SecureConfig()


def check_configuration() -> None:
    """
    Check configuration and display warnings in Streamlit

    Raises:
        RuntimeError: If critical configuration is missing
    """
    is_valid, errors = config.validate_config()

    if not is_valid:
        st.error("⚠️ Configuration Error")
        st.error("The following configuration issues were found:")

        for error in errors:
            st.error(f"• {error}")

        if config.is_production():
            st.stop()
        else:
            st.warning("⚠️ Running in development mode with missing configuration")


def show_config_debug() -> None:
    """Display configuration debug information in Streamlit expander"""
    if not config.is_production():
        with st.expander("🔧 Configuration Debug Info"):
            summary = config.get_config_summary()

            st.json(summary)

            st.markdown("**Environment Variables:**")
            env_vars = {
                'ENVIRONMENT': os.getenv('ENVIRONMENT', 'Not set'),
                'STREAMLIT_SHARING_MODE': os.getenv('STREAMLIT_SHARING_MODE', 'Not set'),
                'STREAMLIT_RUNTIME_ENV': os.getenv('STREAMLIT_RUNTIME_ENV', 'Not set')
            }
            st.json(env_vars)
