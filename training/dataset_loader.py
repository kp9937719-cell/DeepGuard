"""
DeepGuard – Dataset Loader / Helper.

Provides utilities for:
  1. Downloading CIFAKE from Kaggle (requires kaggle API key).
  2. Extracting face crops from FaceForensics++ videos (requires OpenCV + a face detector).
  3. Splitting datasets into train/test directories.

NOTE: You must comply with each dataset's licensing terms before use.
"""

import os
import shutil
import random
import cv2
from pathlib import Path


# ── CIFAKE downloader ──────────────────────────────────────────────────────────
def download_cifake(output_dir: str = "dataset/image"):
    """
    Download CIFAKE dataset using the Kaggle API.

    Prerequisites:
      1. Install kaggle: pip install kaggle
      2. Place your kaggle.json API key at ~/.kaggle/kaggle.json
      3. Accept the dataset terms on Kaggle.

    After download the dataset should unzip into:
        dataset/image/train/REAL/
        dataset/image/train/FAKE/
        dataset/image/test/REAL/
        dataset/image/test/FAKE/
    """
    import subprocess
    os.makedirs(output_dir, exist_ok=True)
    print("[INFO] Downloading CIFAKE from Kaggle …")
    result = subprocess.run(
        ["kaggle", "datasets", "download", "-d",
         "birdy654/cifake-real-and-ai-generated-synthetic-images",
         "--unzip", "-p", output_dir],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print("[ERROR] Kaggle download failed:")
        print(result.stderr)
    else:
        print("[INFO] CIFAKE downloaded successfully.")
        print(result.stdout)


# ── Face crop extractor for FF++ frames ───────────────────────────────────────
def extract_face_crops(video_path: str, output_dir: str,
                       max_frames: int = 50, every_n: int = 10):
    """
    Extract face crops from a video and save them as JPEG images.

    Uses OpenCV's Haarcascade face detector.
    For production use, consider a more accurate detector (e.g. RetinaFace).

    Args:
        video_path:  Path to input video.
        output_dir:  Directory to save face crop images.
        max_frames:  Maximum number of face crops to extract.
        every_n:     Sample every Nth frame.
    """
    os.makedirs(output_dir, exist_ok=True)
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascade_path)

    cap = cv2.VideoCapture(video_path)
    saved = 0
    frame_idx = 0

    while saved < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % every_n == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(64, 64))
            for (x, y, w, h) in faces:
                crop = frame[y:y+h, x:x+w]
                crop_resized = cv2.resize(crop, (224, 224))
                out_path = os.path.join(output_dir, f"frame_{frame_idx}_face.jpg")
                cv2.imwrite(out_path, crop_resized)
                saved += 1
                if saved >= max_frames:
                    break
        frame_idx += 1

    cap.release()
    print(f"[INFO] Saved {saved} face crops to {output_dir}")
    return saved


# ── Train/test split ───────────────────────────────────────────────────────────
def split_dataset(source_dir: str, output_dir: str,
                  train_ratio: float = 0.8, seed: int = 42):
    """
    Split a flat directory of images into train/test subdirectories.

    source_dir structure:
        source_dir/
            REAL/ ...
            FAKE/ ...
    """
    random.seed(seed)
    for label in ["REAL", "FAKE"]:
        src = os.path.join(source_dir, label)
        if not os.path.isdir(src):
            print(f"[WARN] Directory not found: {src}")
            continue

        files = [f for f in os.listdir(src) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        random.shuffle(files)
        split = int(len(files) * train_ratio)
        train_files, test_files = files[:split], files[split:]

        for subset, file_list in [("train", train_files), ("test", test_files)]:
            dest = os.path.join(output_dir, subset, label)
            os.makedirs(dest, exist_ok=True)
            for fname in file_list:
                shutil.copy(os.path.join(src, fname), os.path.join(dest, fname))

        print(f"[INFO] {label}: {len(train_files)} train / {len(test_files)} test")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--action", choices=["download_cifake", "split"], required=True)
    args = ap.parse_args()
    if args.action == "download_cifake":
        download_cifake()
    elif args.action == "split":
        split_dataset("dataset/image/raw", "dataset/image")
