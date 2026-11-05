"""
DeepGuard - Image Metadata Analysis Service.
Extracts EXIF, dimension, format, and basic image properties using Pillow.
"""

import os
from PIL import Image, ExifTags, UnidentifiedImageError


def analyse_metadata(image_path: str) -> dict:
    """
    Extract metadata from an image file.

    Returns a dict with:
        - dimensions, mode, format, file_size
        - exif dict (human-readable tag names)

    Does NOT interpret missing EXIF as proof of AI generation.
    """
    if not os.path.exists(image_path):
        return {"error": "File not found"}

    try:
        img = Image.open(image_path)
    except (UnidentifiedImageError, Exception) as exc:
        return {"error": str(exc)}

    meta = {
        "width": img.width,
        "height": img.height,
        "mode": img.mode,
        "format": img.format or os.path.splitext(image_path)[1].lstrip(".").upper(),
        "file_size_bytes": os.path.getsize(image_path),
        "exif": {},
        "has_exif": False,
    }

    try:
        raw_exif = img._getexif()  # type: ignore[attr-defined]
        if raw_exif:
            meta["has_exif"] = True
            for tag_id, value in raw_exif.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                if isinstance(value, bytes):
                    continue  # skip binary blobs
                meta["exif"][tag_name] = str(value)
    except Exception:
        pass  # EXIF is optional; absence does not imply AI generation

    return meta
