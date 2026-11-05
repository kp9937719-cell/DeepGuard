"""
DeepGuard - Video prediction service.
Runs the CNN model per frame when TensorFlow is available.
Falls back to Pillow-based heuristic analysis on Python 3.14
(or any environment where TensorFlow / OpenCV are not installed).
"""

import logging
import time
import os

logger = logging.getLogger(__name__)

try:
    import numpy as np
    _NUMPY_AVAILABLE = True
except ImportError:
    _NUMPY_AVAILABLE = False

FAKE_THRESHOLD            = 0.50
SUSPICIOUS_RATIO_THRESHOLD = 0.30
INCONCLUSIVE_RATIO         = 0.15


def predict_video(video_path: str) -> dict:
    """
    Run video detection. Priority:
      1. ONNX frame analyzer (when ONNX model is available)
      2. CNN model (when TensorFlow is available)
      3. Heuristic frame-level analysis fallback
    Never fabricates scores.
    """
    onnx_path = os.path.join("models", "image_detector.onnx")
    if os.path.exists(onnx_path):
        try:
            return _onnx_predict_video(video_path)
        except Exception as exc:
            logger.warning("ONNX video prediction failed, falling back: %s", exc)

    from models.model_loader import load_video_model
    model, model_info = load_video_model()

    # ── CNN path ─────────────────────────────────────────────────────────────
    if model is not None and _NUMPY_AVAILABLE:
        return _cnn_predict_video(model, model_info, video_path)

    # ── Heuristic fallback ────────────────────────────────────────────────────
    logger.info("TF/model unavailable – using heuristic video analysis for %s", video_path)
    return _heuristic_predict_video(video_path)


def _onnx_predict_video(video_path: str) -> dict:
    """
    Extract video frames and predict each frame using the trained ONNX model.
    """
    import tempfile, shutil
    from services.onnx_predictor import predict_onnx

    start = time.time()
    frames_extracted = []
    video_info = {}

    try:
        import cv2
        cap = cv2.VideoCapture(video_path)
        if cap.isOpened():
            fps          = cap.get(cv2.CAP_PROP_FPS) or 25.0
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width        = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height       = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            video_info   = {
                "fps": round(fps, 2),
                "total_frames": total_frames,
                "duration_seconds": round(total_frames / fps if fps else 0, 2),
                "width": width,
                "height": height,
                "file_size_bytes": os.path.getsize(video_path),
            }
            sample_interval = max(1, total_frames // 20)
            tmpdir = tempfile.mkdtemp(prefix="dg_onnxvid_")
            frame_idx = 0
            saved = 0
            try:
                while saved < 20:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    if frame_idx % sample_interval == 0:
                        path = os.path.join(tmpdir, f"frame_{saved:03d}.jpg")
                        cv2.imwrite(path, frame)
                        frames_extracted.append((saved, path))
                        saved += 1
                    frame_idx += 1
            finally:
                cap.release()
    except Exception as exc:
        logger.warning("Frame extraction error: %s", exc)

    if frames_extracted:
        frame_results = []
        fake_scores = []
        for idx, (frame_num, frame_path) in enumerate(frames_extracted):
            res = predict_onnx(frame_path)
            if res.get("status") == "success":
                fake_prob = res["fake_probability"] / 100.0
                real_prob = 1.0 - fake_prob
                is_suspicious = fake_prob > FAKE_THRESHOLD
                fake_scores.append(fake_prob)
                frame_results.append({
                    "frame_index": frame_num,
                    "frame_number": idx + 1,
                    "fake_probability": round(fake_prob * 100, 2),
                    "real_probability": round(real_prob * 100, 2),
                    "is_suspicious": is_suspicious,
                })

        try:
            shutil.rmtree(tmpdir, ignore_errors=True)
        except Exception:
            pass

        if fake_scores:
            import statistics
            mean_fake = statistics.mean(fake_scores)
            mean_real = 1.0 - mean_fake
            suspicious_count = sum(1 for f in frame_results if f["is_suspicious"])
            suspicious_ratio = suspicious_count / len(frame_results)

            if suspicious_ratio >= SUSPICIOUS_RATIO_THRESHOLD:
                prediction, risk = "DEEPFAKE / MANIPULATED", "High"
                overall_confidence = suspicious_ratio * 100
            elif suspicious_ratio <= INCONCLUSIVE_RATIO:
                prediction, risk = "LIKELY AUTHENTIC", "Low"
                overall_confidence = (1.0 - suspicious_ratio) * 100
            else:
                prediction, risk = "INCONCLUSIVE", "Medium"
                overall_confidence = 50.0

            elapsed = round(time.time() - start, 3)
            return {
                "status": "success",
                "prediction": prediction,
                "risk": risk,
                "confidence": round(overall_confidence, 2),
                "fake_probability": round(mean_fake * 100, 2),
                "real_probability": round(mean_real * 100, 2),
                "suspicious_frames": suspicious_count,
                "total_frames_extracted": len(frames_extracted),
                "total_frames_analysed": len(frame_results),
                "suspicious_ratio": round(suspicious_ratio * 100, 2),
                "frame_results": frame_results,
                "video_info": video_info,
                "processing_time": elapsed,
                "model_name": "DeepGuard FeatureNet (ONNX)",
                "model_version": "1.0-onnx",
                "is_demo": False,
                "is_heuristic": False,
                "aggregation_note": "Multi-frame neural network feature analysis across extracted video frames.",
            }

    # Fallback to heuristic
    return _heuristic_predict_video(video_path)


# ── CNN-based video prediction ───────────────────────────────────────────────

def _cnn_predict_video(model, model_info: dict, video_path: str) -> dict:
    start = time.time()
    from services.video_processing import extract_frames, preprocess_frame, get_video_info

    try:
        video_info = get_video_info(video_path)
    except ValueError as exc:
        return {"status": "preprocessing_error", "message": str(exc)}

    try:
        extraction = extract_frames(video_path)
    except ValueError as exc:
        return {"status": "preprocessing_error", "message": str(exc)}

    frames       = extraction["frames"]
    frame_indices = extraction["frame_indices"]

    if not frames:
        return {"status": "preprocessing_error",
                "message": "No frames could be extracted from the video."}

    frame_results = []
    fake_scores   = []

    for idx, (frame, original_idx) in enumerate(zip(frames, frame_indices)):
        preprocessed = preprocess_frame(frame)
        try:
            raw = model.predict(preprocessed, verbose=0)
            fake_prob = float(np.squeeze(raw))
        except Exception as exc:
            logger.error("Frame %d prediction failed: %s", idx, exc)
            continue

        real_prob    = 1.0 - fake_prob
        is_suspicious = fake_prob > FAKE_THRESHOLD
        fake_scores.append(fake_prob)
        frame_results.append({
            "frame_index":    original_idx,
            "frame_number":   idx + 1,
            "fake_probability": round(fake_prob * 100, 2),
            "real_probability": round(real_prob * 100, 2),
            "is_suspicious":  is_suspicious,
        })

    if not fake_scores:
        return {"status": "prediction_error",
                "message": "No frames were successfully analysed."}

    mean_fake_prob  = float(np.mean(fake_scores))
    mean_real_prob  = 1.0 - mean_fake_prob
    suspicious_count = sum(1 for f in frame_results if f["is_suspicious"])
    suspicious_ratio = suspicious_count / len(frame_results)

    if suspicious_ratio >= SUSPICIOUS_RATIO_THRESHOLD:
        prediction, risk = "LIKELY DEEPFAKE / MANIPULATED", "High"
    elif suspicious_ratio >= INCONCLUSIVE_RATIO:
        prediction, risk = "INCONCLUSIVE", "Medium"
    else:
        prediction, risk = "LIKELY REAL", "Low"

    confidence = max(mean_fake_prob, mean_real_prob) * 100.0
    elapsed    = round(time.time() - start, 3)

    return {
        "status":                 "success",
        "prediction":             prediction,
        "risk":                   risk,
        "confidence":             round(confidence, 2),
        "real_probability":       round(mean_real_prob * 100, 2),
        "fake_probability":       round(mean_fake_prob * 100, 2),
        "suspicious_frames":      suspicious_count,
        "total_frames_extracted": extraction["frames_extracted"],
        "total_frames_analysed":  len(frame_results),
        "suspicious_ratio":       round(suspicious_ratio * 100, 2),
        "frame_results":          frame_results,
        "video_info":             video_info,
        "processing_time":        elapsed,
        "model_name":             model_info["name"],
        "model_version":          model_info["version"],
        "is_demo":                model_info.get("is_demo", False),
        "demo_warning":           model_info.get("demo_warning"),
        "aggregation_note": (
            f"Overall prediction derived from ratio of suspicious frames "
            f"(>{int(FAKE_THRESHOLD*100)}% fake probability). Treat results as probabilistic."
        ),
    }


# ── Heuristic-based video prediction (Pillow only, no TF/OpenCV) ─────────────

def _heuristic_predict_video(video_path: str) -> dict:
    """
    Extract video frames using PIL-compatible approach and run
    heuristic image analysis on a sample of them.
    Falls back to single-frame analysis if frame extraction fails.
    """
    from services.heuristic_analyzer import analyze_image_heuristic
    import tempfile, shutil

    start = time.time()

    # Try OpenCV frame extraction first (may be available even without NumPy model support)
    frames_extracted = []
    video_info = {}
    try:
        import cv2
        cap = cv2.VideoCapture(video_path)
        if cap.isOpened():
            fps          = cap.get(cv2.CAP_PROP_FPS) or 25.0
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width        = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height       = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            video_info   = {
                "fps": round(fps, 2),
                "total_frames": total_frames,
                "duration_seconds": round(total_frames / fps if fps else 0, 2),
                "width": width,
                "height": height,
                "file_size_bytes": os.path.getsize(video_path),
            }

            sample_interval = max(1, total_frames // 20)   # up to 20 frames
            tmpdir = tempfile.mkdtemp(prefix="dg_vidframes_")
            frame_idx = 0
            saved = 0
            try:
                while saved < 20:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    if frame_idx % sample_interval == 0:
                        path = os.path.join(tmpdir, f"frame_{saved:03d}.jpg")
                        cv2.imwrite(path, frame)
                        frames_extracted.append((saved, path))
                        saved += 1
                    frame_idx += 1
            finally:
                cap.release()
        else:
            cap.release()
    except ImportError:
        pass   # OpenCV not available – analysis will be video-level only

    # If we got frames, analyse each with the heuristic analyzer
    if frames_extracted:
        frame_results = []
        fake_scores   = []

        for idx, (frame_num, frame_path) in enumerate(frames_extracted):
            res = analyze_image_heuristic(frame_path)
            if res.get("status") != "success":
                continue
            fake_prob    = res["fake_probability"] / 100.0
            real_prob    = 1.0 - fake_prob
            is_suspicious = fake_prob > FAKE_THRESHOLD
            fake_scores.append(fake_prob)
            frame_results.append({
                "frame_index":     frame_num,
                "frame_number":    idx + 1,
                "fake_probability": round(fake_prob * 100, 2),
                "real_probability": round(real_prob * 100, 2),
                "is_suspicious":   is_suspicious,
            })

        # Clean up temp frames
        try:
            shutil.rmtree(tmpdir, ignore_errors=True)
        except Exception:
            pass

        if fake_scores:
            import statistics
            mean_fake = statistics.mean(fake_scores)
            mean_real = 1.0 - mean_fake
            suspicious_count = sum(1 for f in frame_results if f["is_suspicious"])
            suspicious_ratio  = suspicious_count / len(frame_results)

            if suspicious_ratio >= SUSPICIOUS_RATIO_THRESHOLD:
                prediction, risk = "LIKELY DEEPFAKE / MANIPULATED", "High"
            elif suspicious_ratio >= INCONCLUSIVE_RATIO:
                prediction, risk = "INCONCLUSIVE", "Medium"
            else:
                prediction, risk = "LIKELY REAL", "Low"

            confidence = max(mean_fake, mean_real) * 100.0
            elapsed    = round(time.time() - start, 3)

            return {
                "status":                 "success",
                "prediction":             prediction,
                "risk":                   risk,
                "confidence":             round(confidence, 2),
                "real_probability":       round(mean_real * 100, 2),
                "fake_probability":       round(mean_fake * 100, 2),
                "suspicious_frames":      suspicious_count,
                "total_frames_extracted": len(frames_extracted),
                "total_frames_analysed":  len(frame_results),
                "suspicious_ratio":       round(suspicious_ratio * 100, 2),
                "frame_results":          frame_results,
                "video_info":             video_info,
                "processing_time":        elapsed,
                "model_name":             "DeepGuard Heuristic Analyzer",
                "model_version":          "1.0-heuristic",
                "is_demo":                True,
                "is_heuristic":           True,
                "aggregation_note": (
                    "Heuristic analysis: overall prediction derived from frame-level "
                    "statistical properties (noise, edges, colour entropy, saturation). "
                    "No trained CNN model is loaded. Accuracy is limited."
                ),
                "demo_warning": (
                    "⚠️ HEURISTIC ANALYSIS – Results are based on statistical image "
                    "properties, not a trained CNN. Install Python 3.12 and run "
                    "create_demo_models.py for CNN-based detection."
                ),
            }

    # Ultimate fallback: cannot analyse video at all
    return {
        "status":  "model_unavailable",
        "message": (
            "Video analysis requires OpenCV. Install it with Python 3.12: "
            "pip install -r requirements_ml.txt"
        ),
    }
