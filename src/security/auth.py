"""
Beta password authentication for Streamlit app
Simple password protection with session management
"""

import streamlit as st
import hashlib
from typing import Optional


class BetaAuthenticator:
    """Simple password authentication for beta access"""

    def __init__(self, password: Optional[str] = None):
        """
        Initialize authenticator

        Args:
            password: Optional password override. If None, uses Streamlit secrets
        """
        # Get password from secrets or use provided password
        if password:
            self.password = password
        else:
            self.password = st.secrets.get("beta_password", None)

        # Initialize session state
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False

    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False)

    def authenticate(self, input_password: str) -> bool:
        """
        Authenticate user with password

        Args:
            input_password: Password provided by user

        Returns:
            True if authentication successful
        """
        if not self.password:
            # No password configured, allow access
            st.session_state.authenticated = True
            return True

        # Hash input password and compare
        if self._hash_password(input_password) == self._hash_password(self.password):
            st.session_state.authenticated = True
            return True

        return False

    def logout(self):
        """Logout user"""
        st.session_state.authenticated = False

    def show_login_form(self) -> bool:
        """
        Display login form and handle authentication

        Returns:
            True if authenticated, False otherwise
        """
        if self.is_authenticated():
            return True

        # If no password configured, auto-authenticate
        if not self.password:
            st.session_state.authenticated = True
            return True

        # Show login form
        st.title("🔐 AI Content Marketing Strategist")
        st.markdown("### Beta Access")

        st.info("This application is currently in private beta. Please enter your access code to continue.")

        with st.form("login_form"):
            password_input = st.text_input(
                "Access Code",
                type="password",
                placeholder="Enter your beta access code"
            )

            submit = st.form_submit_button("Access Application", use_container_width=True)

            if submit:
                if password_input:
                    if self.authenticate(password_input):
                        st.success("✅ Access granted! Loading application...")
                        st.rerun()
                    else:
                        st.error("❌ Invalid access code. Please try again.")
                else:
                    st.warning("⚠️ Please enter an access code")

        st.markdown("---")
        st.markdown("""
        **Need access?**

        This tool is currently in private beta testing. If you'd like to request access:
        - Contact the development team
        - Email: your-email@example.com
        """)

        return False

    def show_logout_button(self):
        """Display logout button in sidebar"""
        if self.is_authenticated() and self.password:
            if st.sidebar.button("🚪 Logout", use_container_width=True):
                self.logout()
                st.rerun()

    @staticmethod
    def _hash_password(password: str) -> str:
        """
        Hash password using SHA256

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()


class DevelopmentAuthenticator(BetaAuthenticator):
    """Authenticator for development that always allows access"""

    def __init__(self):
        super().__init__(password=None)

    def is_authenticated(self) -> bool:
        """Always authenticated in development"""
        return True

    def show_login_form(self) -> bool:
        """Skip login in development"""
        st.session_state.authenticated = True
        return True

    def show_logout_button(self):
        """No logout button in development"""
        pass
