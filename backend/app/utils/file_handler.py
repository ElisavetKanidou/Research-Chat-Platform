
"""
File Handler Utils (app/utils/file_handler.py) - Enhanced version
"""
import os
import uuid
import shutil
from typing import Optional, List, Dict, Any, BinaryIO
from pathlib import Path
import mimetypes
import hashlib
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class FileHandler:
    """Enhanced file handling utilities"""

    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.max_size = settings.MAX_UPLOAD_SIZE
        self.allowed_extensions = settings.ALLOWED_EXTENSIONS

        # Create upload directory
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def validate_file_extension(self, filename: str) -> bool:
        """Validate file extension"""
        ext = Path(filename).suffix.lower()
        return ext in self.allowed_extensions

    def validate_file_size(self, file_size: int) -> bool:
        """Validate file size"""
        return file_size <= self.max_size

    def generate_unique_filename(self, original_filename: str) -> str:
        """Generate unique filename preserving extension"""
        ext = Path(original_filename).suffix
        unique_name = f"{uuid.uuid4()}{ext}"
        return unique_name

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get comprehensive file information"""
        if not file_path.exists():
            return {}

        stat = file_path.stat()
        mime_type, _ = mimetypes.guess_type(str(file_path))

        return {
            "name": file_path.name,
            "size": stat.st_size,
            "size_human": self.format_file_size(stat.st_size),
            "mime_type": mime_type,
            "extension": file_path.suffix.lower(),
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "hash": self.calculate_file_hash(file_path)
        }

    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.1f} {size_names[i]}"

    def save_uploaded_file(
            self,
            file_content: bytes,
            original_filename: str,
            user_id: str,
            subfolder: Optional[str] = None
    ) -> Dict[str, Any]:
        """Save uploaded file with metadata"""

        # Validate
        if not self.validate_file_extension(original_filename):
            raise ValueError(f"File type not allowed: {Path(original_filename).suffix}")

        if not self.validate_file_size(len(file_content)):
            raise ValueError(f"File too large: {len(file_content)} bytes")

        # Generate paths
        unique_filename = self.generate_unique_filename(original_filename)
        user_dir = self.upload_dir / user_id

        if subfolder:
            user_dir = user_dir / subfolder

        user_dir.mkdir(parents=True, exist_ok=True)
        file_path = user_dir / unique_filename

        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)

        # Return file info
        file_info = self.get_file_info(file_path)
        file_info.update({
            "original_name": original_filename,
            "unique_name": unique_filename,
            "relative_path": str(file_path.relative_to(self.upload_dir)),
            "url": f"/files/{file_path.relative_to(self.upload_dir)}"
        })

        return file_info

    def delete_file(self, file_path: str) -> bool:
        """Delete file safely"""
        try:
            full_path = self.upload_dir / file_path

            # Security check - ensure path is within upload directory
            if not str(full_path.resolve()).startswith(str(self.upload_dir.resolve())):
                logger.warning(f"Attempted to delete file outside upload directory: {file_path}")
                return False

            if full_path.exists():
                full_path.unlink()
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False

    def cleanup_empty_directories(self, path: Path) -> None:
        """Remove empty directories recursively"""
        try:
            for item in path.iterdir():
                if item.is_dir():
                    self.cleanup_empty_directories(item)

            # Remove if empty
            if not any(path.iterdir()):
                path.rmdir()

        except Exception as e:
            logger.error(f"Failed to cleanup directory {path}: {e}")

