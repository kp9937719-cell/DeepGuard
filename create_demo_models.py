"""
DeepGuard – create_demo_models.py
==================================
Run this on ANY machine with Python 3.12 and TensorFlow installed.
It builds two fully-structured CNN models with RANDOM (untrained) weights,
saves them as .keras files, then you copy those files to the DeepGuard
models/ directory.

WHY: Python 3.14 (your production machine) does not yet support TensorFlow.
This script lets you generate valid model files on any Python 3.12 machine,
after which DeepGuard loads and uses them normally.

DISCLAIMER: These are DEMO models with random weights.
Predictions will NOT be accurate until you fine-tune or retrain them
on CIFAKE / FaceForensics++ data (see training/train_image_model.py).
The app clearly labels all predictions from this model as "Demo Model".

USAGE:
  1. On a machine with Python 3.12:
       pip install tensorflow==2.16.2
       python create_demo_models.py

  2. Copy the two generated files to DeepGuard/models/:
       image_detector.keras
       video_detector.keras

  3. Restart DeepGuard – full AI pipeline is now active.

REQUIREMENTS: tensorflow>=2.13 (Python 3.10-3.12)
"""

import os
import sys
import json
from datetime import datetime, timezone

print("DeepGuard – Demo Model Creator")
print("=" * 50)

# ── Import guard ──────────────────────────────────────────────────────────────
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    print(f"TensorFlow {tf.__version__} found.")
except ImportError:
    print("\n[ERROR] TensorFlow is not installed.")
    print("Install it with:  pip install tensorflow==2.16.2")
    print("Requires Python 3.10 – 3.12")
    sys.exit(1)

print(f"Python {sys.version}")
print()

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(OUTPUT_DIR, exist_ok=True)

IMG_SIZE = (224, 224, 3)


# ── Shared CNN architecture ───────────────────────────────────────────────────
def build_deepguard_cnn(name: str) -> keras.Model:
    """
    4-block CNN with BatchNorm + GlobalAveragePooling + sigmoid head.
    Input:  (batch, 224, 224, 3) float32 normalised to [0, 1]
    Output: (batch, 1) float32  – probability of FAKE (0=Real, 1=Fake)
    """
    inputs = keras.Input(shape=IMG_SIZE, name="image_input")

    # Augmentation (active during training, bypassed during inference)
    x = layers.RandomFlip("horizontal")(inputs)
    x = layers.RandomRotation(0.05)(x)

    # Block 1
    x = layers.Conv2D(32, 3, padding="same", activation="relu",
                      name="conv1")(x)
    x = layers.BatchNormalization(name="bn1")(x)
    x = layers.MaxPooling2D(name="pool1")(x)

    # Block 2
    x = layers.Conv2D(64, 3, padding="same", activation="relu",
                      name="conv2")(x)
    x = layers.BatchNormalization(name="bn2")(x)
    x = layers.MaxPooling2D(name="pool2")(x)

    # Block 3
    x = layers.Conv2D(128, 3, padding="same", activation="relu",
                      name="conv3")(x)
    x = layers.BatchNormalization(name="bn3")(x)
    x = layers.MaxPooling2D(name="pool3")(x)

    # Block 4
    x = layers.Conv2D(256, 3, padding="same", activation="relu",
                      name="conv4")(x)
    x = layers.BatchNormalization(name="bn4")(x)
    x = layers.GlobalAveragePooling2D(name="gap")(x)

    # Head
    x = layers.Dense(256, activation="relu", name="dense1")(x)
    x = layers.Dropout(0.4, name="dropout")(x)
    outputs = layers.Dense(1, activation="sigmoid", name="prediction")(x)

    model = keras.Model(inputs, outputs, name=name)
    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=["accuracy", keras.metrics.AUC(name="auc")],
    )
    return model


# ── Build and save image model ────────────────────────────────────────────────
print("Building image detection model...")
image_model = build_deepguard_cnn("DeepGuard_ImageDetector_v1")
image_model.summary(line_length=70, print_fn=lambda x: None)  # suppress verbose output

image_path = os.path.join(OUTPUT_DIR, "image_detector.keras")
image_model.save(image_path)
size_kb = os.path.getsize(image_path) / 1024
print(f"  Saved: {image_path}  ({size_kb:.1f} KB)")
print(f"  Parameters: {image_model.count_params():,}")


# ── Build and save video model ────────────────────────────────────────────────
print()
print("Building video (frame-level) detection model...")
video_model = build_deepguard_cnn("DeepGuard_VideoDetector_v1")

video_path = os.path.join(OUTPUT_DIR, "video_detector.keras")
video_model.save(video_path)
size_kb = os.path.getsize(video_path) / 1024
print(f"  Saved: {video_path}  ({size_kb:.1f} KB)")
print(f"  Parameters: {video_model.count_params():,}")


# ── Save metadata JSON ────────────────────────────────────────────────────────
print()
metadata = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "tensorflow_version": tf.__version__,
    "model_type": "demo_random_weights",
    "warning": (
        "These models have RANDOM (untrained) weights. "
        "Predictions are not meaningful until the models are "
        "trained on CIFAKE / FaceForensics++ data."
    ),
    "image_model": {
        "filename": "image_detector.keras",
        "architecture": "4-block CNN + GlobalAveragePooling + sigmoid",
        "input_shape": list(IMG_SIZE),
        "parameters": image_model.count_params(),
        "output": "P(FAKE) sigmoid 0-1",
    },
    "video_model": {
        "filename": "video_detector.keras",
        "architecture": "4-block CNN + GlobalAveragePooling + sigmoid",
        "input_shape": list(IMG_SIZE),
        "parameters": video_model.count_params(),
        "output": "P(FAKE) per frame, sigmoid 0-1",
    },
    "training_next_steps": [
        "1. Download CIFAKE from Kaggle (birdy654/cifake-real-and-ai-generated-synthetic-images)",
        "2. Run: python training/train_image_model.py",
        "3. Download FaceForensics++ (requires author approval)",
        "4. Run: python training/train_video_model.py",
    ],
}

meta_path = os.path.join(OUTPUT_DIR, "model_metadata.json")
with open(meta_path, "w") as f:
    json.dump(metadata, f, indent=2)
print(f"Metadata saved: {meta_path}")

# ── Done ──────────────────────────────────────────────────────────────────────
print()
print("=" * 50)
print("DONE — Two model files created:")
print(f"  models/image_detector.keras")
print(f"  models/video_detector.keras")
print()
print("NEXT STEPS:")
print("  1. Copy both .keras files to DeepGuard/models/")
print("  2. Restart DeepGuard (python app.py)")
print("  3. Upload an image or video — predictions will appear")
print()
print("NOTE: Predictions use RANDOM weights until properly trained.")
print("      See training/ scripts to train on real datasets.")
print("      The app labels all results with the model version clearly.")
print("=" * 50)
