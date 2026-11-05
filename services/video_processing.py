"""
DeepGuard - Video processing service.
OpenCV and NumPy are optional; their absence is handled gracefully.
"""

import os
import logging
from config import Config

logger = logging.getLogger(__name__)

try:
    import cv2
    import numpy as np
    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False
    logger.warning("OpenCV / NumPy not installed. Video processing unavailable.")


def extract_frames(video_path: str, sample_rate: int = None, max_frames: int = None) -> dict:
    """Extract frames from a video file at the given sample rate."""
    if not _CV2_AVAILABLE:
        raise ValueError("OpenCV is not installed. Install requirements_ml.txt with Python 3.12.")

    if sample_rate is None:
        sample_rate = Config.VIDEO_FRAME_SAMPLE_RATE
    if max_frames is None:
        max_frames = Config.VIDEO_MAX_FRAMES

    if not os.path.exists(video_path):
        raise ValueError(f"Video file not found: {video_path}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Cannot open video file – it may be corrupt or use an unsupported codec.")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0

    frames = []
    frame_indices = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % sample_rate == 0:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(rgb_frame)
            frame_indices.append(frame_idx)
            if len(frames) >= max_frames:
                break
        frame_idx += 1

    cap.release()

    return {
        "frames": frames,
        "frame_indices": frame_indices,
        "total_frames": total_frames,
        "fps": fps,
        "duration_seconds": round(duration, 2),
        "frames_extracted": len(frames),
    }


def preprocess_frame(frame_rgb, target_size=None):
    """Resize and normalise a single RGB frame for model input."""
    if target_size is None:
        target_size = Config.IMAGE_MODEL_INPUT_SIZE
    resized = cv2.resize(frame_rgb, target_size, interpolation=cv2.INTER_AREA)
    normalised = resized.astype(np.float32) / 255.0
    return np.expand_dims(normalised, axis=0)


def get_video_info(video_path: str) -> dict:
    """Return basic video metadata without extracting frames."""
    if not _CV2_AVAILABLE:
        raise ValueError("OpenCV is not installed.")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Cannot open video file.")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return {
        "fps": round(fps, 2),
        "total_frames": total_frames,
        "duration_seconds": round(total_frames / fps if fps else 0, 2),
        "width": width,
        "height": height,
        "file_size_bytes": os.path.getsize(video_path),
    }
