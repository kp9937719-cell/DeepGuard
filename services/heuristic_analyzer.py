"""
DeepGuard – Pillow-based heuristic image analyzer (v3 – dual-calibrated).
Works on Python 3.14 with only Pillow installed.

CALIBRATED against two measured images:
  AI  image (cartoon baby PNG, no EXIF):
      blur_diff=2.19, vibrancy=0.673, edge_cv=4.10,
      local_var=427, grad_cv=4.10, entropy=5.11

  Real photo (Pavagadh temple JPEG, no EXIF):
      blur_diff=13.35, vibrancy=0.411, edge_cv=1.45,
      local_var=1961, grad_cv=1.25, entropy=9.29

Each signal is scored so the AI image approaches 1.0 and the real photo
approaches 0.0, with graceful handling of boundary / ambiguous images.

7 signals weighted to sum to 1.0.
"""

import os
import math
import logging
import statistics
from PIL import Image, ImageFilter, ImageStat

logger = logging.getLogger(__name__)

MODEL_NAME    = "DeepGuard Heuristic Analyzer"
MODEL_VERSION = "3.0-heuristic"

_W = {
    "blur_noise":      0.30,  # strongest discriminator (AI=2, real=13)
    "local_variance":  0.22,  # very different (AI=427, real=1961)
    "color_entropy":   0.18,  # very different (AI=5.1, real=9.3)
    "format_exif":     0.12,  # PNG+noEXIF = strong AI signal
    "vibrancy":        0.10,  # moderate (AI=0.67, real=0.41)
    "edge_texture":    0.05,  # weaker signal
    "gradient_cv":     0.03,  # weakest – keep for tie-breaking
}


def _px(img):
    """Pillow 12/13 compatible pixel list."""
    try:
        return list(img.getdata())
    except TypeError:
        return list(img.get_flattened_data())


# ── Signal 1: blur_noise  (AI≈2.2 | Real≈13.3) ──────────────────────────────
def _blur_noise(gray: Image.Image) -> float:
    blurred = gray.filter(ImageFilter.GaussianBlur(radius=1))
    gp, bp  = _px(gray), _px(blurred)
    mean_d  = sum(abs(a - b) for a, b in zip(gp, bp)) / len(gp)
    # Linear interpolation anchored to measured values
    # AI=2.2 → 0.95, Real=13.3 → 0.08; midpoint ~7.7 → 0.5
    if mean_d < 2.0:  return 0.97
    if mean_d < 3.0:  return 0.92
    if mean_d < 4.5:  return 0.82
    if mean_d < 6.5:  return 0.68
    if mean_d < 9.0:  return 0.48
    if mean_d < 12.0: return 0.28
    if mean_d < 16.0: return 0.12
    return 0.06


# ── Signal 2: local_variance  (AI≈427 | Real≈1961) ──────────────────────────
def _local_variance(gray: Image.Image) -> float:
    pix  = _px(gray)
    W = H = 512
    tile = 32
    tvars = []
    for ty in range(0, H, tile):
        for tx in range(0, W, tile):
            patch = [pix[y * W + x]
                     for y in range(ty, min(ty + tile, H))
                     for x in range(tx, min(tx + tile, W))]
            if len(patch) > 1:
                tvars.append(statistics.variance(patch))
    if not tvars:
        return 0.5
    mv = statistics.mean(tvars)
    # AI≈427 → 0.90, Real≈1961 → 0.08; breakpoints:
    if mv < 100:   return 0.97
    if mv < 200:   return 0.90
    if mv < 350:   return 0.82
    if mv < 550:   return 0.70
    if mv < 800:   return 0.52
    if mv < 1200:  return 0.32
    if mv < 1600:  return 0.18
    if mv < 2200:  return 0.10
    return 0.06


# ── Signal 3: color_entropy  (AI≈5.1 | Real≈9.3) ────────────────────────────
def _color_entropy(img: Image.Image) -> float:
    small = img.resize((128, 128), Image.LANCZOS)
    hist  = small.histogram()
    total = sum(hist)
    if total == 0:
        return 0.5
    ent = -sum((p / total) * math.log2(p / total) for p in hist if p > 0)
    # Max theoretical = log2(768) ≈ 9.58
    norm = ent / 9.58
    # AI≈0.533 (5.1/9.58) → 0.90, Real≈0.969 (9.3/9.58) → 0.08
    if norm < 0.52:  return 0.95
    if norm < 0.60:  return 0.88
    if norm < 0.68:  return 0.78
    if norm < 0.76:  return 0.62
    if norm < 0.83:  return 0.42
    if norm < 0.90:  return 0.25
    if norm < 0.95:  return 0.12
    return 0.07


# ── Signal 4: format_exif ────────────────────────────────────────────────────
def _format_exif(img: Image.Image, image_path: str) -> float:
    ext = os.path.splitext(image_path)[1].lower()
    exif_count   = 0
    has_cam_tags = False
    try:
        raw = img._getexif()  # type: ignore[attr-defined]
        if raw:
            exif_count   = len(raw)
            has_cam_tags = (271 in raw or 272 in raw)  # Make / Model
    except Exception:
        pass

    if has_cam_tags and exif_count > 5:
        return 0.08   # strong real signal
    if has_cam_tags:
        return 0.15
    if exif_count > 8:
        return 0.22
    if exif_count > 3:
        return 0.35
    # No useful EXIF at all
    if ext == ".png":
        return 0.85   # PNG + zero EXIF = very likely AI
    if ext in (".jpg", ".jpeg"):
        return 0.50   # JPEG + no EXIF = ambiguous (stripped by social media)
    return 0.55


# ── Signal 5: vibrancy  (AI≈0.673 | Real≈0.411) ─────────────────────────────
def _vibrancy(img: Image.Image) -> float:
    small = img.resize((256, 256), Image.LANCZOS)
    r_, g_, b_ = small.split()
    r_d, g_d, b_d = _px(r_), _px(g_), _px(b_)
    vibs = [(max(r, g, b) - min(r, g, b)) / max(max(r, g, b), 1)
            for r, g, b in zip(r_d, g_d, b_d)]
    mv = sum(vibs) / len(vibs)
    # AI=0.673 → 0.88, Real=0.411 → 0.28
    # Mid-point ≈ 0.54, which is genuinely ambiguous → 0.55
    if mv > 0.72:   return 0.95
    if mv > 0.62:   return 0.85
    if mv > 0.54:   return 0.70
    if mv > 0.46:   return 0.52
    if mv > 0.38:   return 0.32
    if mv > 0.28:   return 0.20
    return 0.12


# ── Signal 6: edge_texture  (AI edge_cv≈4.1 | Real edge_cv≈1.45) ────────────
def _edge_texture(gray: Image.Image) -> float:
    """
    CV of edge-response pixel values.
    COUNTER-intuitive: high CV here means jagged, varied edges (real photos).
    Low CV means unnaturally uniform edges (AI smooth fills, OR AI sharp outlines
    with very uniform fill regions). We use mean_edge as secondary discriminator.
    """
    sm    = gray.resize((256, 256), Image.LANCZOS)
    edges = sm.filter(ImageFilter.FIND_EDGES)
    ep    = _px(edges)
    if not ep:
        return 0.5
    mean_e = sum(ep) / len(ep)
    std_e  = (sum((p - mean_e) ** 2 for p in ep) / len(ep)) ** 0.5
    cv     = std_e / max(mean_e, 1)
    # Real = cv≈1.45 (moderate, organic). AI cartoon = cv≈4.1 (high: sharp
    # outlines on flat fills create bimodal edge distribution → high std).
    # Real photorealism AI = cv likely 2-3.
    # Real photo: mean_e≈54 (sharp textures). AI cartoon: mean_e≈38 (smoother).
    # Combine both factors:
    if cv > 3.5 and mean_e < 45:   return 0.80   # high CV + low mean = AI cartoon
    if cv > 3.0:                   return 0.68
    if cv > 2.2:                   return 0.52
    if cv > 1.8:                   return 0.38
    if cv > 1.3:                   return 0.25   # real photo range
    return 0.18


# ── Signal 7: gradient_cv  (AI≈4.1 | Real≈1.25) ─────────────────────────────
def _gradient_cv(gray: Image.Image) -> float:
    sm  = gray.resize((256, 256), Image.LANCZOS)
    pix = _px(sm)
    W   = 256
    diffs = ([abs(pix[i + 1] - pix[i]) for i in range(len(pix) - 1) if (i + 1) % W != 0]
             + [abs(pix[i + W] - pix[i]) for i in range(len(pix) - W)])
    if not diffs:
        return 0.5
    m   = sum(diffs) / len(diffs)
    std = (sum((d - m) ** 2 for d in diffs) / len(diffs)) ** 0.5
    cv  = std / max(m, 1)
    # Real≈1.25 → 0.15, AI≈4.1 → 0.75 — both ends are clear
    if cv > 4.5:   return 0.88
    if cv > 3.5:   return 0.78
    if cv > 2.8:   return 0.65
    if cv > 2.0:   return 0.50
    if cv > 1.5:   return 0.35
    if cv > 1.0:   return 0.20
    return 0.12


# ── Master analysis function ─────────────────────────────────────────────────

def analyze_image_heuristic(image_path: str) -> dict:
    import time
    from services.image_preprocessing import extract_metadata

    if not os.path.exists(image_path):
        return {"status": "preprocessing_error",
                "message": f"File not found: {image_path}"}

    start = time.time()
    try:
        img = Image.open(image_path).convert("RGB")
    except Exception as exc:
        return {"status": "preprocessing_error",
                "message": f"Cannot open image: {exc}"}

    try:
        meta = extract_metadata(img, image_path)
    except Exception:
        meta = {"width": img.width, "height": img.height,
                "mode": "RGB", "format": "unknown", "exif": {}}

    work = img.resize((512, 512), Image.LANCZOS)
    gray = work.convert("L")

    raw = {
        "blur_noise":     _blur_noise(gray),
        "local_variance": _local_variance(gray),
        "color_entropy":  _color_entropy(work),
        "format_exif":    _format_exif(img, image_path),
        "vibrancy":       _vibrancy(work),
        "edge_texture":   _edge_texture(gray),
        "gradient_cv":    _gradient_cv(gray),
    }

    fake_prob = sum(_W[k] * v for k, v in raw.items())
    fake_prob = max(0.04, min(0.96, fake_prob))
    real_prob = 1.0 - fake_prob

    if fake_prob >= 0.62:
        prediction, risk = "LIKELY AI-GENERATED / MANIPULATED", "High"
    elif fake_prob <= 0.38:
        prediction, risk = "LIKELY REAL", "Low"
    else:
        prediction, risk = "INCONCLUSIVE", "Medium"

    elapsed = round(time.time() - start, 3)

    logger.info(
        "Heuristic v3: fake=%.3f pred=%s | %s",
        fake_prob, prediction,
        " ".join(f"{k}={v:.2f}" for k, v in raw.items()),
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
        "is_demo":          True,
        "is_heuristic":     True,
        "heuristic_scores": {k: round(v, 3) for k, v in raw.items()},
        "image_metadata":   meta,
        "demo_warning": (
            "⚠️ HEURISTIC ANALYSIS – Results are based on 7 statistical image signals "
            "(noise smoothness, local texture variance, colour entropy, format/EXIF, "
            "colour vibrancy, edge texture, gradient variation). "
            "Not a trained neural network. Install Python 3.12 + run "
            "create_demo_models.py for CNN-based detection."
        ),
    }
