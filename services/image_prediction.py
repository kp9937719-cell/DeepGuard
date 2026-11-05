"""
DeepGuard – Image prediction service.
Priority chain:
  1. ONNX FeatureNet  (Python 3.14 compatible, trained model)
  2. TensorFlow CNN   (Python 3.12 only, if available)
  3. Heuristic        (pure Pillow fallback, labelled clearly)
"""

import logging
import time
import os

logger = logging.getLogger(__name__)


def predict_image(image_path: str) -> dict:
    """
    Run image detection using the best available method.
    Never fabricates scores.
    """
    # ── Priority 1: ONNX trained model ───────────────────────────────────────
    onnx_path = os.path.join("models", "image_detector.onnx")
    if os.path.exists(onnx_path):
        try:
            from services.onnx_predictor import predict_onnx
            result = predict_onnx(image_path)
            if result.get("status") == "success":
                return result
            logger.warning("ONNX prediction failed: %s", result.get("message"))
        except Exception as exc:
            logger.warning("ONNX predictor error: %s", exc)

    # ── Priority 2: TensorFlow CNN ────────────────────────────────────────────
    try:
        import numpy as np
        from models.model_loader import load_image_model
        model, model_info = load_image_model()
        if model is not None:
            return _cnn_predict(model, model_info, image_path)
    except Exception as exc:
        logger.warning("TF CNN unavailable: %s", exc)

    # ── Priority 3: Heuristic fallback ────────────────────────────────────────
    logger.info("Using heuristic analyzer for: %s", image_path)
    from services.heuristic_analyzer import analyze_image_heuristic
    return analyze_image_heuristic(image_path)


def _cnn_predict(model, model_info: dict, image_path: str) -> dict:
    import numpy as np
    start = time.time()
    try:
        from services.image_preprocessing import load_and_preprocess
        preprocessed, meta = load_and_preprocess(image_path)
    except ValueError as exc:
        return {"status": "preprocessing_error", "message": str(exc)}
    try:
        raw_output = model.predict(preprocessed, verbose=0)
    except Exception as exc:
        return {"status": "prediction_error", "message": str(exc)}

    elapsed   = round(time.time() - start, 3)
    fake_prob = float(np.squeeze(raw_output))
    real_prob = 1.0 - fake_prob

    if fake_prob >= 0.60:
        prediction, risk = "LIKELY AI-GENERATED / MANIPULATED", "High"
    elif fake_prob <= 0.40:
        prediction, risk = "LIKELY REAL", "Low"
    else:
        prediction, risk = "INCONCLUSIVE", "Medium"

    return {
        "status":           "success",
        "prediction":       prediction,
        "risk":             risk,
        "confidence":       round(max(fake_prob, real_prob) * 100, 2),
        "real_probability": round(real_prob * 100, 2),
        "fake_probability": round(fake_prob * 100, 2),
        "processing_time":  elapsed,
        "model_name":       model_info["name"],
        "model_version":    model_info["version"],
        "is_demo":          model_info.get("is_demo", False),
        "demo_warning":     model_info.get("demo_warning"),
        "image_metadata":   meta,
    }
