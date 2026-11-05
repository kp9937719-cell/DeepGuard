"""
DeepGuard - Model loader.
Handles loading and caching of TensorFlow / Keras models.
TensorFlow is optional; clearly reports availability.
Reads model_metadata.json to detect demo (untrained) models.
"""

import os
import json
import logging
from config import Config

logger = logging.getLogger(__name__)

_image_model = None
_video_model = None

try:
    import tensorflow as tf
    _TF_AVAILABLE = True
except ImportError:
    _TF_AVAILABLE = False
    logger.warning(
        "TensorFlow not installed. AI detection is unavailable on this Python version. "
        "To enable model inference, use Python 3.12 and: pip install -r requirements_ml.txt"
    )

# Check if models are demo (untrained) by reading metadata
_META_PATH = os.path.join(Config.MODEL_DIR, "model_metadata.json")


def _read_meta() -> dict:
    if os.path.exists(_META_PATH):
        try:
            with open(_META_PATH) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


_MODEL_META = _read_meta()
_IS_DEMO = _MODEL_META.get("model_type") == "demo_random_weights"

IMAGE_MODEL_INFO = {
    "name": "DeepGuard Image Detector",
    "version": "1.0-demo" if _IS_DEMO else "1.0",
    "type": "CNN – Binary Classification (Real vs AI-Generated / Manipulated)",
    "input_size": Config.IMAGE_MODEL_INPUT_SIZE,
    "status": "not_loaded",
    "is_demo": _IS_DEMO,
    "demo_warning": (
        "⚠️ DEMO MODEL – Random weights, not trained on real data. "
        "Predictions are NOT meaningful. Train the model first."
    ) if _IS_DEMO else None,
}

VIDEO_MODEL_INFO = {
    "name": "DeepGuard Video Detector",
    "version": "1.0-demo" if _IS_DEMO else "1.0",
    "type": "CNN – Frame-level Binary Classification (Real vs Deepfake)",
    "input_size": Config.IMAGE_MODEL_INPUT_SIZE,
    "status": "not_loaded",
    "is_demo": _IS_DEMO,
    "demo_warning": IMAGE_MODEL_INFO["demo_warning"],
}


def load_image_model():
    """Load the image detection model. Returns (model, info_dict)."""
    global _image_model
    if _image_model is not None:
        IMAGE_MODEL_INFO["status"] = "loaded"
        return _image_model, IMAGE_MODEL_INFO

    if not _TF_AVAILABLE:
        IMAGE_MODEL_INFO["status"] = "tf_unavailable"
        return None, IMAGE_MODEL_INFO

    path = Config.IMAGE_MODEL_PATH
    if not os.path.exists(path):
        logger.warning("Image model not found at: %s", path)
        IMAGE_MODEL_INFO["status"] = "not_found"
        return None, IMAGE_MODEL_INFO

    try:
        _image_model = tf.keras.models.load_model(path)
        IMAGE_MODEL_INFO["status"] = "loaded"
        logger.info("Image model loaded from %s (demo=%s)", path, _IS_DEMO)
        return _image_model, IMAGE_MODEL_INFO
    except Exception as exc:
        logger.error("Failed to load image model: %s", exc)
        IMAGE_MODEL_INFO["status"] = "load_error"
        IMAGE_MODEL_INFO["error"] = str(exc)
        return None, IMAGE_MODEL_INFO


def load_video_model():
    """Load the video detection model. Returns (model, info_dict)."""
    global _video_model
    if _video_model is not None:
        VIDEO_MODEL_INFO["status"] = "loaded"
        return _video_model, VIDEO_MODEL_INFO

    if not _TF_AVAILABLE:
        VIDEO_MODEL_INFO["status"] = "tf_unavailable"
        return None, VIDEO_MODEL_INFO

    path = Config.VIDEO_MODEL_PATH
    if not os.path.exists(path):
        logger.warning("Video model not found at: %s", path)
        VIDEO_MODEL_INFO["status"] = "not_found"
        return None, VIDEO_MODEL_INFO

    try:
        _video_model = tf.keras.models.load_model(path)
        VIDEO_MODEL_INFO["status"] = "loaded"
        logger.info("Video model loaded from %s (demo=%s)", path, _IS_DEMO)
        return _video_model, VIDEO_MODEL_INFO
    except Exception as exc:
        logger.error("Failed to load video model: %s", exc)
        VIDEO_MODEL_INFO["status"] = "load_error"
        VIDEO_MODEL_INFO["error"] = str(exc)
        return None, VIDEO_MODEL_INFO


def get_model_status():
    """Return a dict describing the current availability of models."""
    img_path = Config.IMAGE_MODEL_PATH
    vid_path = Config.VIDEO_MODEL_PATH
    onnx_path = os.path.join(Config.MODEL_DIR, "image_detector.onnx")
    has_onnx = os.path.exists(onnx_path)

    image_status = {
        **IMAGE_MODEL_INFO,
        "path": onnx_path if has_onnx else img_path,
        "file_exists": has_onnx or os.path.exists(img_path),
        "tf_available": _TF_AVAILABLE,
        "is_demo": False if has_onnx else _IS_DEMO,
    }
    if has_onnx:
        image_status["name"] = "DeepGuard FeatureNet (ONNX)"
        image_status["version"] = "1.0-onnx"
        image_status["type"] = "ONNX Neural Network – AI Feature Classifier"
        image_status["status"] = "loaded"
        image_status["demo_warning"] = None

    return {
        "image_model": image_status,
        "video_model": {
            **VIDEO_MODEL_INFO,
            "path": vid_path,
            "file_exists": os.path.exists(vid_path),
            "tf_available": _TF_AVAILABLE,
            "is_demo": _IS_DEMO,
        },
    }
