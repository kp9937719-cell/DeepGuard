"""
DeepGuard – SHA-256 file hash service.
"""

import hashlib
import os


def compute_sha256(file_path: str) -> str:
    """Compute SHA-256 hash for a file at the given path."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def compute_sha256_bytes(data: bytes) -> str:
    """Compute SHA-256 hash for raw bytes."""
    return hashlib.sha256(data).hexdigest()
