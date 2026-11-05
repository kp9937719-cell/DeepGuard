"""
DeepGuard – ONNX-based image feature extractor + predictor.
Extracts 7 statistical features from an image using only Pillow + NumPy,
then runs them through the trained ONNX FeatureNet for a real prediction.

Feature vector (order must match train_onnx_model.py):
  [blur_noise, local_var, color_entropy, vibrancy,
   edge_cv, gradient_cv, format_score]
"""

import os
import math
import logging
import statistics
import time

import numpy as np
from PIL import Image, ImageFilter

logger = logging.getLogger(__name__)

MODEL_NAME    = "DeepGuard FeatureNet"
MODEL_VERSION = "1.0-onnx"

_session = None   # ONNX InferenceSession (lazy-loaded)


def _load_session():
    global _session
    if _session is not None:
        return _session
    model_path = os.path.join("models", "image_detector.onnx")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"ONNX model not found: {model_path}")
    import onnxruntime as ort
    opts = ort.SessionOptions()
    opts.log_severity_level = 3
    _session = ort.InferenceSession(model_path, opts,
                                    providers=["CPUExecutionProvider"])
    logger.info("ONNX model loaded: %s", model_path)
    return _session


def _px(img):
    """Pillow-version-safe pixel list."""
    try:
        return list(img.getdata())
    except TypeError:
        return list(img.get_flattened_data())


def extract_features(image_path: str) -> np.ndarray:
    """
    Extract the 7-element feature vector from an image file.
    Returns shape (1, 7) float32 ndarray.
    """
    img  = Image.open(image_path).convert("RGB")
    work = img.resize((512, 512), Image.LANCZOS)
    gray = work.convert("L")

    # ── 1. blur_noise ────────────────────────────────────────────────────────
    blurred  = gray.filter(ImageFilter.GaussianBlur(radius=1))
    gp, bp   = _px(gray), _px(blurred)
    blur_noise = sum(abs(a - b) for a, b in zip(gp, bp)) / len(gp)

    # ── 2. local_var ─────────────────────────────────────────────────────────
    pix  = np.array(gp, dtype=np.float32).reshape(512, 512)
    tile = 32
    tvars = []
    for ty in range(0, 512, tile):
        for tx in range(0, 512, tile):
            patch = pix[ty:ty+tile, tx:tx+tile].flatten()
            if len(patch) > 1:
                tvars.append(float(patch.var()))
    local_var = float(np.mean(tvars)) if tvars else 500.0

    # ── 3. color_entropy ─────────────────────────────────────────────────────
    small = work.resize((128, 128), Image.LANCZOS)
    hist  = small.histogram()
    total = sum(hist)
    entropy = -sum((p/total)*math.log2(p/total) for p in hist if p > 0)

    # ── 4. vibrancy ──────────────────────────────────────────────────────────
    sm = work.resize((256, 256), Image.LANCZOS)
    r_, g_, b_ = sm.split()
    r_d, g_d, b_d = _px(r_), _px(g_), _px(b_)
    vibs = [(max(r, g, b) - min(r, g, b)) / max(max(r, g, b), 1)
            for r, g, b in zip(r_d, g_d, b_d)]
    vibrancy = float(np.mean(vibs))

    # ── 5. edge_cv ───────────────────────────────────────────────────────────
    sm_gray = gray.resize((256, 256), Image.LANCZOS)
    edges   = sm_gray.filter(ImageFilter.FIND_EDGES)
    ep      = np.array(_px(edges), dtype=np.float32)
    mean_e  = ep.mean()
    edge_cv = float(ep.std() / max(mean_e, 1))

    # ── 6. gradient_cv ───────────────────────────────────────────────────────
    sm_pix = np.array(_px(sm_gray), dtype=np.float32).reshape(256, 256)
    h_diff = np.abs(np.diff(sm_pix, axis=1)).flatten()
    v_diff = np.abs(np.diff(sm_pix, axis=0)).flatten()
    all_d  = np.concatenate([h_diff, v_diff])
    m_d    = all_d.mean()
    gradient_cv = float(all_d.std() / max(m_d, 1))

    # ── 7. format_score ──────────────────────────────────────────────────────
    # Low value = real (JPEG + camera EXIF), High value = AI (PNG / AI metadata / no EXIF)
    ext = os.path.splitext(image_path)[1].lower()
    exif_count   = 0
    has_cam_tags = False
    try:
        raw_exif = img._getexif()  # type: ignore
        if raw_exif:
            exif_count   = len(raw_exif)
            has_cam_tags = (271 in raw_exif or 272 in raw_exif)
    except Exception:
        pass

    # Check for direct AI watermarks / provenance (Google AI, C2PA, SynthID, etc.)
    ai_provenance = False
    meta_text = ""
    for k, v in getattr(img, "info", {}).items():
        if isinstance(v, bytes):
            meta_text += " " + v.decode("utf-8", errors="ignore").lower()
        elif isinstance(v, str):
            meta_text += " " + v.lower()
        elif isinstance(v, dict):
            for subv in v.values():
                if isinstance(subv, bytes):
                    meta_text += " " + subv.decode("utf-8", errors="ignore").lower()
                elif isinstance(subv, str):
                    meta_text += " " + subv.lower()

    ai_keywords = [
        "trainedalgorithmicmedia",
        "made with google ai",
        "synthid",
        "c2pa",
        "generative",
        "midjourney",
        "stable diffusion",
        "dall-e",
        "dalle",
        "firefly",
        "novelai"
    ]
    if any(kw in meta_text for kw in ai_keywords):
        ai_provenance = True

    if ai_provenance:
        format_score = 1.00
    elif has_cam_tags and exif_count > 5:
        format_score = 0.05
    elif has_cam_tags:
        format_score = 0.15
    elif exif_count > 5:
        format_score = 0.25
    elif ext == ".png" and exif_count == 0:
        format_score = 0.90
    elif exif_count == 0:
        format_score = 0.55
    else:
        format_score = 0.35

    feat = np.array([[blur_noise, local_var, entropy, vibrancy,
                      edge_cv, gradient_cv, format_score]], dtype=np.float32)

    logger.debug(
        "Features: blur=%.2f lvar=%.0f ent=%.2f vib=%.3f "
        "ecv=%.2f gcv=%.2f fmt=%.2f",
        blur_noise, local_var, entropy, vibrancy,
        edge_cv, gradient_cv, format_score,
    )
    return feat


def predict_onnx(image_path: str) -> dict:
    """
    Full prediction pipeline: extract features → ONNX inference → result dict.
    Returns the same dict format as image_prediction.py / heuristic_analyzer.py.
    """
    start = time.time()
    try:
        sess = _load_session()
    except FileNotFoundError as exc:
        return {"status": "model_unavailable", "message": str(exc)}
    except Exception as exc:
        return {"status": "model_unavailable", "message": f"Cannot load ONNX model: {exc}"}

    try:
        feat = extract_features(image_path)
    except Exception as exc:
        return {"status": "preprocessing_error", "message": f"Feature extraction failed: {exc}"}

    try:
        out       = sess.run(None, {"input": feat})
        fake_prob = float(out[0][0][0])
    except Exception as exc:
        return {"status": "prediction_error", "message": f"ONNX inference failed: {exc}"}

    real_prob = 1.0 - fake_prob

    # Calibrated thresholds
    if fake_prob >= 0.60:
        prediction, risk = "LIKELY AI-GENERATED / MANIPULATED", "High"
    elif fake_prob <= 0.40:
        prediction, risk = "LIKELY REAL", "Low"
    else:
        prediction, risk = "INCONCLUSIVE", "Medium"

    elapsed = round(time.time() - start, 3)

    logger.info(
        "ONNX prediction: fake_prob=%.4f → %s (%.1f%% confidence)",
        fake_prob, prediction, max(fake_prob, real_prob) * 100,
    )

    return {
        "status":           "success",
        "prediction":       prediction,
        "risk":             risk,
        "confidence":       round(max(fake_prob, real_prob) * 100, 2),
        "real_probability": round(real_prob * 100, 2),
        "fake_probability": round(fake_prob * 100, 2),
        "processing_time":  elapsed,
        "model_name":       MODEL_NAME,
        "model_version":    MODEL_VERSION,
        "is_demo":          False,
        "is_heuristic":     False,
        "heuristic_scores": {
            "blur_noise":    round(float(feat[0][0]), 3),
            "local_var":     round(float(feat[0][1]), 1),
            "color_entropy": round(float(feat[0][2]), 3),
            "vibrancy":      round(float(feat[0][3]), 3),
            "edge_cv":       round(float(feat[0][4]), 3),
            "gradient_cv":   round(float(feat[0][5]), 3),
            "format_score":  round(float(feat[0][6]), 3),
        },
    }
