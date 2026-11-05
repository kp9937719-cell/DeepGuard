"""
DeepGuard – Video/Face-Manipulation Model Training Script.

Dataset: FaceForensics++ (FF++)
Source:  https://github.com/ondyari/FaceForensics
License: Academic / Non-commercial use. See repository for full terms.

Access: FF++ requires registration and approval from the authors.
        Do NOT use this script without completing the dataset access form.

This script expects preprocessed face crops stored as image frames:
    dataset/video/
        train/
            REAL/    ← frames from original videos (face crops)
            FAKE/    ← frames from manipulated videos (face crops)
        test/
            REAL/
            FAKE/

Face extraction from raw video is a separate preprocessing step.
A sample face extraction script is provided in training/dataset_loader.py.

Usage:
    python training/train_video_model.py
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import json

# ── Config ────────────────────────────────────────────────────────────────────
DATASET_DIR = os.path.join("dataset", "video")
TRAIN_DIR   = os.path.join(DATASET_DIR, "train")
TEST_DIR    = os.path.join(DATASET_DIR, "test")
MODEL_PATH  = os.path.join("models", "video_detector.keras")

IMG_SIZE    = (224, 224)
BATCH_SIZE  = 32
EPOCHS      = 20
SEED        = 42

# ── Verify ────────────────────────────────────────────────────────────────────
for d in [TRAIN_DIR, TEST_DIR]:
    if not os.path.isdir(d):
        print(f"[ERROR] Dataset directory not found: {d}")
        print("Please prepare the FF++ face-crop dataset as described in the module docstring.")
        sys.exit(1)

# ── Data loaders ──────────────────────────────────────────────────────────────
print("[INFO] Loading datasets …")
train_ds = keras.utils.image_dataset_from_directory(
    TRAIN_DIR, image_size=IMG_SIZE, batch_size=BATCH_SIZE, seed=SEED, label_mode="binary",
)
val_ds = keras.utils.image_dataset_from_directory(
    TEST_DIR, image_size=IMG_SIZE, batch_size=BATCH_SIZE, seed=SEED, label_mode="binary",
)

class_names = train_ds.class_names
print(f"[INFO] Classes: {class_names}")

normalise = layers.Rescaling(1.0 / 255)
train_ds  = train_ds.map(lambda x, y: (normalise(x), y)).prefetch(tf.data.AUTOTUNE)
val_ds    = val_ds.map(lambda x, y: (normalise(x), y)).prefetch(tf.data.AUTOTUNE)

# ── Model (same architecture – retrain from scratch) ──────────────────────────
data_augmentation = keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.05),
    layers.RandomContrast(0.1),
], name="augmentation")

inputs = keras.Input(shape=(224, 224, 3))
x = data_augmentation(inputs)
for filters in [32, 64, 128, 256]:
    x = layers.Conv2D(filters, 3, padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D()(x)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dense(256, activation="relu")(x)
x = layers.Dropout(0.5)(x)
outputs = layers.Dense(1, activation="sigmoid")(x)
model = keras.Model(inputs, outputs, name="DeepGuard_VideoDetector")
model.summary()

model.compile(
    optimizer=keras.optimizers.Adam(1e-4),
    loss="binary_crossentropy",
    metrics=["accuracy", keras.metrics.AUC(name="auc")],
)

callbacks = [
    keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True),
    keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=3, min_lr=1e-6),
    keras.callbacks.ModelCheckpoint(MODEL_PATH, save_best_only=True, monitor="val_auc", mode="max"),
]

print("[INFO] Training …")
history = model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS, callbacks=callbacks)

print("[INFO] Evaluating …")
loss, acc, auc = model.evaluate(val_ds)
print(f"Test Loss: {loss:.4f}  |  Accuracy: {acc:.4f}  |  AUC: {auc:.4f}")

y_true, y_pred_prob = [], []
for images, labels in val_ds:
    preds = model.predict(images, verbose=0)
    y_true.extend(labels.numpy().flatten().tolist())
    y_pred_prob.extend(preds.flatten().tolist())

y_pred = [1 if p > 0.5 else 0 for p in y_pred_prob]
print("\nClassification Report:")
print(classification_report(y_true, y_pred, target_names=class_names))
print(f"ROC-AUC: {roc_auc_score(y_true, y_pred_prob):.4f}")

with open(os.path.join("models", "video_training_history.json"), "w") as f:
    json.dump({k: [float(v) for v in vals] for k, vals in history.history.items()}, f, indent=2)

print(f"[INFO] Model saved to {MODEL_PATH}")
