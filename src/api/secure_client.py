"""
Secure API client for OpenRouter with retry logic and error handling
"""

import requests
import time
from typing import Optional, Dict, Any
import streamlit as st
from ..config.secure_config import config


class APIError(Exception):
    """Custom exception for API errors"""
    pass


class RateLimitError(APIError):
    """Exception for rate limit errors"""
    pass


class AuthenticationError(APIError):
    """Exception for authentication errors"""
    pass


class SecureAPIClient:
    """Secure API client with retry logic and error handling"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize secure API client

        Args:
            api_key: Optional API key override. If None, uses config
        """
        self.api_key = api_key or config.get_api_key()
        self.retry_config = config.get_retry_config()
        self.model_config = config.get_model_config()

        if not self.api_key:
            raise AuthenticationError("API key not configured")

        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-content-strategist.streamlit.app",
            "X-Title": "AI Content Marketing Strategist"
        }

    def chat_completion(
        self,
        messages: list[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Make chat completion request with retry logic

        Args:
            messages: List of message dictionaries
            model: Optional model override
            temperature: Optional temperature override
            max_tokens: Optional max_tokens override

        Returns:
            API response dictionary

        Raises:
            APIError: If request fails after retries
            RateLimitError: If rate limited
            AuthenticationError: If authentication fails
        """
        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": model or self.model_config['model'],
            "messages": messages,
            "temperature": temperature or self.model_config['temperature'],
            "max_tokens": max_tokens or self.model_config['max_tokens']
        }

        return self._make_request_with_retry("POST", url, json=payload)

    def _make_request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make HTTP request with exponential backoff retry logic

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional request parameters

        Returns:
            Response JSON

        Raises:
            APIError: If request fails after retries
        """
        max_retries = self.retry_config['max_retries']
        backoff_factor = self.retry_config['backoff_factor']
        retry_statuses = self.retry_config['retry_on_status']

        last_error = None

        for attempt in range(max_retries + 1):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    timeout=self.model_config['timeout'],
                    **kwargs
                )

                # Check for specific error status codes
                if response.status_code == 401:
                    raise AuthenticationError("Invalid API key")

                if response.status_code == 429:
                    if attempt < max_retries:
                        # Rate limited, retry with backoff
                        wait_time = backoff_factor ** attempt
                        time.sleep(wait_time)
                        continue
                    else:
                        raise RateLimitError("Rate limit exceeded. Please try again later.")

                if response.status_code in retry_statuses:
                    if attempt < max_retries:
                        # Server error, retry with backoff
                        wait_time = backoff_factor ** attempt
                        time.sleep(wait_time)
                        continue
                    else:
                        raise APIError(f"Server error: {response.status_code}")

                # Raise for other error status codes
                response.raise_for_status()

                # Success
                return response.json()

            except requests.exceptions.Timeout as e:
                last_error = e
                if attempt < max_retries:
                    wait_time = backoff_factor ** attempt
                    time.sleep(wait_time)
                    continue

            except requests.exceptions.RequestException as e:
                last_error = e
                if attempt < max_retries:
                    wait_time = backoff_factor ** attempt
                    time.sleep(wait_time)
                    continue

            except AuthenticationError:
                # Don't retry authentication errors
                raise

            except RateLimitError:
                # Don't retry if we've exhausted retries
                raise

        # If we get here, all retries failed
        raise APIError(f"Request failed after {max_retries} retries: {str(last_error)}")

    def validate_connection(self) -> tuple[bool, Optional[str]]:
        """
        Validate API connection and credentials

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Make a minimal test request
            messages = [{"role": "user", "content": "test"}]
            self.chat_completion(messages, max_tokens=1)
            return (True, None)

        except AuthenticationError as e:
            return (False, f"Authentication failed: {str(e)}")

        except RateLimitError as e:
            return (False, f"Rate limit error: {str(e)}")

        except APIError as e:
            return (False, f"API error: {str(e)}")

        except Exception as e:
            return (False, f"Unexpected error: {str(e)}")

    def get_usage_info(self) -> Optional[Dict[str, Any]]:
        """
        Get API usage information

        Returns:
            Usage info dictionary or None if unavailable
        """
        try:
            # OpenRouter doesn't have a standard usage endpoint
            # This is a placeholder for future implementation
            return None
        except Exception:
            return None


def test_api_connection() -> None:
    """
    Test API connection and display results in Streamlit

    Displays success or error messages in the UI
    """
    try:
        with st.spinner("Testing API connection..."):
            client = SecureAPIClient()
            is_valid, error = client.validate_connection()

            if is_valid:
                st.success("✅ API connection successful")
            else:
                st.error(f"❌ API connection failed: {error}")

    except AuthenticationError as e:
        st.error(f"❌ Authentication Error: {str(e)}")
        st.error("Please check your OPENROUTER_API_KEY in secrets configuration")

    except Exception as e:
        st.error(f"❌ Unexpected Error: {str(e)}")


def get_client() -> SecureAPIClient:
    """
    Get or create API client instance

    Returns:
        SecureAPIClient instance

    Raises:
        AuthenticationError: If API key not configured
    """
    # Cache client in session state
    if 'api_client' not in st.session_state:
        st.session_state.api_client = SecureAPIClient()

    return st.session_state.api_client
