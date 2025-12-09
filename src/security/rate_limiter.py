"""
Session-based rate limiting to prevent abuse
Tracks requests per user session with time windows
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Optional


class RateLimiter:
    """Session-based rate limiter for Streamlit"""

    def __init__(self, max_requests: int = 5, window_seconds: int = 3600):
        """
        Initialize rate limiter

        Args:
            max_requests: Maximum requests allowed per window
            window_seconds: Time window in seconds (default: 3600 = 1 hour)
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds

        # Initialize session state for rate limiting
        if 'rate_limit_requests' not in st.session_state:
            st.session_state.rate_limit_requests = []

    def is_allowed(self) -> bool:
        """
        Check if request is allowed under rate limit

        Returns:
            True if request is allowed, False if rate limited
        """
        now = datetime.now()

        # Clean up old requests outside the window
        self._clean_old_requests(now)

        # Check if under limit
        if len(st.session_state.rate_limit_requests) < self.max_requests:
            # Record this request
            st.session_state.rate_limit_requests.append(now)
            return True

        return False

    def get_remaining_requests(self) -> int:
        """
        Get number of remaining requests in current window

        Returns:
            Number of requests remaining
        """
        now = datetime.now()
        self._clean_old_requests(now)

        remaining = self.max_requests - len(st.session_state.rate_limit_requests)
        return max(0, remaining)

    def get_reset_time(self) -> Optional[datetime]:
        """
        Get time when rate limit will reset

        Returns:
            Datetime when oldest request expires, or None if no requests
        """
        if not st.session_state.rate_limit_requests:
            return None

        oldest_request = min(st.session_state.rate_limit_requests)
        reset_time = oldest_request + timedelta(seconds=self.window_seconds)

        return reset_time

    def get_time_until_reset(self) -> Optional[str]:
        """
        Get human-readable time until rate limit resets

        Returns:
            String like "45 minutes" or "2 hours", or None if no limit
        """
        reset_time = self.get_reset_time()

        if not reset_time:
            return None

        now = datetime.now()
        delta = reset_time - now

        if delta.total_seconds() <= 0:
            return "now"

        # Convert to human-readable format
        minutes = int(delta.total_seconds() / 60)
        hours = minutes // 60
        remaining_minutes = minutes % 60

        if hours > 0:
            if remaining_minutes > 0:
                return f"{hours} hour{'s' if hours != 1 else ''} and {remaining_minutes} minute{'s' if remaining_minutes != 1 else ''}"
            else:
                return f"{hours} hour{'s' if hours != 1 else ''}"
        else:
            return f"{minutes} minute{'s' if minutes != 1 else ''}"

    def show_rate_limit_message(self):
        """Display user-friendly rate limit message in Streamlit"""
        reset_time = self.get_time_until_reset()

        st.error("🚫 Rate Limit Reached")
        st.warning(
            f"You've reached the maximum of **{self.max_requests} strategy generations** per hour. "
            f"This limit helps us provide quality service to all users."
        )

        if reset_time:
            st.info(f"⏰ Your limit will reset in **{reset_time}**")

        st.markdown("---")
        st.markdown("**Why rate limits?**")
        st.markdown(
            "- Ensures fair access for all users\n"
            "- Prevents system abuse\n"
            "- Helps manage AI API costs\n"
            "- Maintains service quality"
        )

        st.markdown("---")
        st.markdown(
            "💡 **Tip:** Use your generations wisely by preparing all your brand information before starting!"
        )

    def show_remaining_requests(self):
        """Display remaining requests info in Streamlit"""
        remaining = self.get_remaining_requests()

        if remaining > 0:
            if remaining <= 2:
                st.warning(f"⚠️ You have **{remaining}** strategy generation{'s' if remaining != 1 else ''} remaining this hour")
            else:
                st.info(f"ℹ️ You have **{remaining}** strategy generation{'s' if remaining != 1 else ''} remaining this hour")
        else:
            st.error("🚫 No generations remaining this hour")
            reset_time = self.get_time_until_reset()
            if reset_time:
                st.info(f"⏰ Your limit will reset in **{reset_time}**")

    def reset_for_session(self):
        """Reset rate limit for current session (admin/testing only)"""
        st.session_state.rate_limit_requests = []

    def _clean_old_requests(self, now: datetime):
        """Remove requests outside the time window"""
        cutoff = now - timedelta(seconds=self.window_seconds)

        st.session_state.rate_limit_requests = [
            req for req in st.session_state.rate_limit_requests
            if req > cutoff
        ]


class DevelopmentRateLimiter(RateLimiter):
    """Rate limiter for development that always allows requests"""

    def __init__(self):
        super().__init__(max_requests=999999, window_seconds=1)

    def is_allowed(self) -> bool:
        """Always allow in development mode"""
        return True

    def show_rate_limit_message(self):
        """Show development mode message"""
        st.info("🔧 Development mode: Rate limiting disabled")

    def get_remaining_requests(self) -> int:
        """Always return high number in dev mode"""
        return 999999
