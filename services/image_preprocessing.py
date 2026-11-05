"""
DeepGuard - Image preprocessing service.
Handles loading, validation, resizing, normalisation, and EXIF/metadata extraction.
CV2 and NumPy are optional; their absence is handled gracefully.
"""

import os
import logging
from config import Config

logger = logging.getLogger(__name__)

# Optional heavy dependencies
try:
    import numpy as np
    import cv2
    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False
    logger.warning("OpenCV / NumPy not installed. Image preprocessing unavailable.")

try:
    from PIL import Image, ExifTags, UnidentifiedImageError
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False
    logger.warning("Pillow not installed. Image loading unavailable.")


def load_and_preprocess(image_path: str, target_size=None):
    """
    Load an image, validate it, and return a normalised NumPy array ready for model input.

    Returns: (preprocessed_array, metadata_dict)
    Raises: ValueError on invalid / unreadable image or missing dependencies.
    """
    if not _PIL_AVAILABLE or not _CV2_AVAILABLE:
        raise ValueError(
            "Required libraries (Pillow, OpenCV, NumPy) are not installed. "
            "Install them with: pip install -r requirements_ml.txt"
        )

    if target_size is None:
        target_size = Config.IMAGE_MODEL_INPUT_SIZE

    if not os.path.exists(image_path):
        raise ValueError(f"Image file not found: {image_path}")

    try:
        pil_img = Image.open(image_path)
        pil_img.verify()
    except Exception as exc:
        raise ValueError(f"Cannot read image – it may be corrupt: {exc}") from exc

    pil_img = Image.open(image_path).convert("RGB")
    metadata = extract_metadata(pil_img, image_path)

    resized = pil_img.resize(target_size, Image.LANCZOS)
    arr = np.array(resized, dtype=np.float32) / 255.0
    arr = np.expand_dims(arr, axis=0)

    return arr, metadata


def extract_metadata(pil_img, image_path: str) -> dict:
    """Extract image dimensions, format, and EXIF data."""
    meta = {
        "width": pil_img.width,
        "height": pil_img.height,
        "mode": pil_img.mode,
        "format": pil_img.format or os.path.splitext(image_path)[1].lstrip(".").upper(),
        "file_size_bytes": os.path.getsize(image_path) if os.path.exists(image_path) else 0,
        "exif": {},
    }
    try:
        raw_exif = pil_img._getexif()  # type: ignore[attr-defined]
        if raw_exif:
            from PIL import ExifTags
            for tag_id, value in raw_exif.items():
                tag = ExifTags.TAGS.get(tag_id, str(tag_id))
                if isinstance(value, bytes):
                    continue
                meta["exif"][tag] = str(value)
    except Exception:
        pass
    return meta


def validate_image_file(file_path: str) -> bool:
    """Quick check that a file is a valid, non-corrupt image."""
    if not _CV2_AVAILABLE:
        raise ValueError("OpenCV not installed – cannot validate image.")
    img = cv2.imread(file_path)
    if img is None:
        raise ValueError("OpenCV could not decode the image.")
    return True
