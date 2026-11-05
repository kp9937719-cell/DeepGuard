"""
DeepGuard – Image Model Training Script.

Dataset: CIFAKE (Real vs. AI-Generated Images)
Source:  https://www.kaggle.com/datasets/birdy654/cifake-real-and-ai-generated-synthetic-images
License: Creative Commons – check Kaggle page for current terms.

Usage:
    python training/train_image_model.py

The script expects the dataset to be organised as follows:
    dataset/image/
        train/
            REAL/    ← real images
            FAKE/    ← AI-generated images
        test/
            REAL/
            FAKE/

After training, the model is saved to:
    models/image_detector.keras
"""

import os
import sys

# Ensure project root is on path when run as script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import matplotlib.pyplot as plt
import json

# ── Config ────────────────────────────────────────────────────────────────────
DATASET_DIR = os.path.join("dataset", "image")
TRAIN_DIR   = os.path.join(DATASET_DIR, "train")
TEST_DIR    = os.path.join(DATASET_DIR, "test")
MODEL_PATH  = os.path.join("models", "image_detector.keras")

IMG_SIZE    = (224, 224)
BATCH_SIZE  = 32
EPOCHS      = 20
SEED        = 42

# ── Verify dataset ────────────────────────────────────────────────────────────
for d in [TRAIN_DIR, TEST_DIR]:
    if not os.path.isdir(d):
        print(f"[ERROR] Dataset directory not found: {d}")
        print("Please download CIFAKE from Kaggle and organise it as described in the module docstring.")
        sys.exit(1)


# ── Data loaders ──────────────────────────────────────────────────────────────
print("[INFO] Loading datasets …")
train_ds = keras.utils.image_dataset_from_directory(
    TRAIN_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    seed=SEED,
    label_mode="binary",
)
val_ds = keras.utils.image_dataset_from_directory(
    TEST_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    seed=SEED,
    label_mode="binary",
)

class_names = train_ds.class_names
print(f"[INFO] Classes: {class_names}")

# Normalise + prefetch
normalise = layers.Rescaling(1.0 / 255)
train_ds  = train_ds.map(lambda x, y: (normalise(x), y)).prefetch(tf.data.AUTOTUNE)
val_ds    = val_ds.map(lambda x, y: (normalise(x), y)).prefetch(tf.data.AUTOTUNE)


# ── Augmentation ──────────────────────────────────────────────────────────────
data_augmentation = keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.1),
    layers.RandomBrightness(0.1),
], name="augmentation")


# ── CNN Architecture ──────────────────────────────────────────────────────────
def build_model(input_shape=(224, 224, 3)):
    inputs = keras.Input(shape=input_shape)
    x = data_augmentation(inputs)

    # Block 1
    x = layers.Conv2D(32, 3, padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D()(x)

    # Block 2
    x = layers.Conv2D(64, 3, padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D()(x)

    # Block 3
    x = layers.Conv2D(128, 3, padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D()(x)

    # Block 4
    x = layers.Conv2D(256, 3, padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.GlobalAveragePooling2D()(x)

    # Head
    x = layers.Dense(256, activation="relu")(x)
    x = layers.Dropout(0.4)(x)
    outputs = layers.Dense(1, activation="sigmoid")(x)

    return keras.Model(inputs, outputs, name="DeepGuard_ImageDetector")


model = build_model()
model.summary()


# ── Compile ───────────────────────────────────────────────────────────────────
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=1e-4),
    loss="binary_crossentropy",
    metrics=["accuracy", keras.metrics.AUC(name="auc")],
)

callbacks = [
    keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True, monitor="val_loss"),
    keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=3, min_lr=1e-6),
    keras.callbacks.ModelCheckpoint(MODEL_PATH, save_best_only=True, monitor="val_auc", mode="max"),
]


# ── Train ─────────────────────────────────────────────────────────────────────
print("[INFO] Training …")
history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS,
    callbacks=callbacks,
)


# ── Evaluate ──────────────────────────────────────────────────────────────────
print("[INFO] Evaluating on test set …")
loss, acc, auc = model.evaluate(val_ds)
print(f"Test Loss: {loss:.4f}  |  Accuracy: {acc:.4f}  |  AUC: {auc:.4f}")

# Per-sample predictions for sklearn metrics
y_true, y_pred_prob = [], []
for images, labels in val_ds:
    preds = model.predict(images, verbose=0)
    y_true.extend(labels.numpy().flatten().tolist())
    y_pred_prob.extend(preds.flatten().tolist())

y_pred = [1 if p > 0.5 else 0 for p in y_pred_prob]
print("\nClassification Report:")
print(classification_report(y_true, y_pred, target_names=class_names))
print("\nConfusion Matrix:")
print(confusion_matrix(y_true, y_pred))
print(f"ROC-AUC: {roc_auc_score(y_true, y_pred_prob):.4f}")

# Save history
with open(os.path.join("models", "image_training_history.json"), "w") as f:
    json.dump({k: [float(v) for v in vals] for k, vals in history.history.items()}, f, indent=2)

print(f"[INFO] Model saved to {MODEL_PATH}")
