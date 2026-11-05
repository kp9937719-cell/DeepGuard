"""
DeepGuard – Model Evaluation Script.
Loads saved models and prints metrics against a test dataset.

Usage:
    python training/evaluate_model.py --model image
    python training/evaluate_model.py --model video
"""

import os
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score, accuracy_score
)

parser = argparse.ArgumentParser()
parser.add_argument("--model", choices=["image", "video"], required=True,
                    help="Which model to evaluate.")
args = parser.parse_args()

MODEL_MAP = {
    "image": ("models/image_detector.keras", "dataset/image/test"),
    "video": ("models/video_detector.keras", "dataset/video/test"),
}

model_path, test_dir = MODEL_MAP[args.model]

if not os.path.exists(model_path):
    print(f"[ERROR] Model file not found: {model_path}")
    sys.exit(1)
if not os.path.isdir(test_dir):
    print(f"[ERROR] Test directory not found: {test_dir}")
    sys.exit(1)

print(f"[INFO] Loading model from {model_path} …")
model = keras.models.load_model(model_path)

IMG_SIZE = (224, 224)
BATCH_SIZE = 32

val_ds = keras.utils.image_dataset_from_directory(
    test_dir, image_size=IMG_SIZE, batch_size=BATCH_SIZE, label_mode="binary",
)
class_names = val_ds.class_names
normalise = layers.Rescaling(1.0 / 255)
val_ds = val_ds.map(lambda x, y: (normalise(x), y)).prefetch(tf.data.AUTOTUNE)

print("[INFO] Evaluating …")
loss, acc, *_ = model.evaluate(val_ds, verbose=1)
print(f"\nLoss: {loss:.4f}   Accuracy: {acc:.4f}")

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
