"""
Safe file handling for Streamlit Cloud
Uses download buttons instead of file writes
"""

import streamlit as st
import tempfile
import os
from pathlib import Path
from typing import Optional, Union
from datetime import datetime
from ..config.secure_config import config
from ..security.input_validator import InputValidator


class FileHandler:
    """Safe file handler for Streamlit Cloud deployment"""

    def __init__(self):
        """Initialize file handler"""
        self.config = config.get_file_config()
        self.validator = InputValidator()

    def create_download_button(
        self,
        file_content: Union[str, bytes],
        filename: str,
        mime_type: str,
        button_label: str,
        help_text: Optional[str] = None,
        key: Optional[str] = None
    ) -> bool:
        """
        Create Streamlit download button

        Args:
            file_content: Content to download (string or bytes)
            filename: Suggested filename
            mime_type: MIME type (e.g., 'application/pdf')
            button_label: Button text
            help_text: Optional help text
            key: Optional unique key for button

        Returns:
            True if button was clicked
        """
        # Sanitize filename
        safe_filename = self.validator.sanitize_for_filename(filename)

        # Convert content to bytes if needed
        if isinstance(file_content, str):
            file_bytes = file_content.encode('utf-8')
        else:
            file_bytes = file_content

        # Check file size
        size_mb = len(file_bytes) / (1024 * 1024)
        if size_mb > self.config['max_file_size_mb']:
            st.error(f"❌ File too large: {size_mb:.2f}MB (max: {self.config['max_file_size_mb']}MB)")
            return False

        # Create download button
        return st.download_button(
            label=button_label,
            data=file_bytes,
            file_name=safe_filename,
            mime=mime_type,
            help=help_text,
            key=key,
            use_container_width=True
        )

    def create_temp_file(
        self,
        content: Union[str, bytes],
        suffix: str = ""
    ) -> Optional[str]:
        """
        Create temporary file (for internal processing only)

        Args:
            content: File content
            suffix: File extension (e.g., '.docx')

        Returns:
            Path to temporary file or None on error

        Note:
            Temp files are automatically cleaned up by OS
        """
        try:
            # Create temp file
            fd, path = tempfile.mkstemp(suffix=suffix)

            # Write content
            if isinstance(content, str):
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                with os.fdopen(fd, 'wb') as f:
                    f.write(content)

            return path

        except Exception as e:
            st.error(f"Error creating temporary file: {str(e)}")
            return None

    def read_temp_file(self, path: str, mode: str = 'rb') -> Optional[Union[str, bytes]]:
        """
        Read temporary file

        Args:
            path: Path to file
            mode: Read mode ('r' or 'rb')

        Returns:
            File content or None on error
        """
        try:
            with open(path, mode, encoding='utf-8' if 'b' not in mode else None) as f:
                return f.read()

        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            return None

    def delete_temp_file(self, path: str) -> bool:
        """
        Delete temporary file

        Args:
            path: Path to file

        Returns:
            True if successful
        """
        try:
            if os.path.exists(path):
                os.unlink(path)
            return True

        except Exception:
            return False

    def get_safe_filename(
        self,
        base_name: str,
        extension: str,
        include_timestamp: bool = True
    ) -> str:
        """
        Generate safe filename

        Args:
            base_name: Base filename (e.g., brand name)
            extension: File extension (e.g., '.docx')
            include_timestamp: Whether to include timestamp

        Returns:
            Safe filename
        """
        # Sanitize base name
        safe_base = self.validator.sanitize_for_filename(base_name)

        # Add timestamp if requested
        if include_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_base = f"{safe_base}_{timestamp}"

        # Ensure extension starts with dot
        if not extension.startswith('.'):
            extension = f".{extension}"

        return f"{safe_base}{extension}"

    def create_zip_download(
        self,
        files: dict[str, bytes],
        zip_filename: str,
        button_label: str = "📦 Download All Files",
        key: Optional[str] = None
    ) -> bool:
        """
        Create download button for multiple files as ZIP

        Args:
            files: Dictionary of {filename: content}
            zip_filename: Name of ZIP file
            button_label: Button text
            key: Optional unique key

        Returns:
            True if button was clicked
        """
        import zipfile
        import io

        try:
            # Create ZIP in memory
            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for filename, content in files.items():
                    safe_filename = self.validator.sanitize_for_filename(filename)
                    zip_file.writestr(safe_filename, content)

            zip_buffer.seek(0)
            zip_content = zip_buffer.read()

            # Create download button
            return self.create_download_button(
                file_content=zip_content,
                filename=zip_filename,
                mime_type='application/zip',
                button_label=button_label,
                key=key
            )

        except Exception as e:
            st.error(f"Error creating ZIP file: {str(e)}")
            return False


# Global file handler instance
file_handler = FileHandler()


def download_docx(
    content: bytes,
    brand_name: str,
    doc_type: str = "strategy",
    key: Optional[str] = None
) -> bool:
    """
    Create download button for DOCX file

    Args:
        content: DOCX file content
        brand_name: Brand name for filename
        doc_type: Type of document ('strategy' or 'calendar')
        key: Optional unique key

    Returns:
        True if button was clicked
    """
    filename = file_handler.get_safe_filename(
        base_name=f"{brand_name}_{doc_type}",
        extension=".docx"
    )

    return file_handler.create_download_button(
        file_content=content,
        filename=filename,
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        button_label=f"📄 Download {doc_type.title()} (DOCX)",
        key=key
    )


def download_xlsx(
    content: bytes,
    brand_name: str,
    key: Optional[str] = None
) -> bool:
    """
    Create download button for XLSX file

    Args:
        content: XLSX file content
        brand_name: Brand name for filename
        key: Optional unique key

    Returns:
        True if button was clicked
    """
    filename = file_handler.get_safe_filename(
        base_name=f"{brand_name}_calendar",
        extension=".xlsx"
    )

    return file_handler.create_download_button(
        file_content=content,
        filename=filename,
        mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        button_label="📊 Download Calendar (Excel)",
        key=key
    )


def download_json(
    content: str,
    brand_name: str,
    key: Optional[str] = None
) -> bool:
    """
    Create download button for JSON file

    Args:
        content: JSON content
        brand_name: Brand name for filename
        key: Optional unique key

    Returns:
        True if button was clicked
    """
    filename = file_handler.get_safe_filename(
        base_name=f"{brand_name}_data",
        extension=".json"
    )

    return file_handler.create_download_button(
        file_content=content,
        filename=filename,
        mime_type="application/json",
        button_label="📋 Download Data (JSON)",
        key=key
    )


def download_all_files(
    files: dict[str, bytes],
    brand_name: str,
    key: Optional[str] = None
) -> bool:
    """
    Create download button for all files as ZIP

    Args:
        files: Dictionary of {filename: content}
        brand_name: Brand name for filename
        key: Optional unique key

    Returns:
        True if button was clicked
    """
    zip_filename = file_handler.get_safe_filename(
        base_name=f"{brand_name}_complete",
        extension=".zip"
    )

    return file_handler.create_zip_download(
        files=files,
        zip_filename=zip_filename,
        key=key
    )
