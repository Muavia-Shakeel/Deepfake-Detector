"""
src/preprocessing/preprocessor.py

Preprocessing pipeline for deepfake detection:
- Resize face frames to target size (224x224)
- Normalize using ImageNet mean/std
- Save processed images to data/processed/faces/
- Works on pre-cropped face PNGs (DFDC format) or raw frames
"""

import os
import logging
from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# ImageNet normalization constants
IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD  = np.array([0.229, 0.224, 0.225], dtype=np.float32)


def load_image(path: str) -> Optional[np.ndarray]:
    """
    Load image from disk as RGB numpy array (H, W, 3) uint8.
    Returns None if load fails.
    """
    try:
        img = cv2.imread(str(path))
        if img is None:
            logger.warning(f"Could not read image: {path}")
            return None
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    except Exception as e:
        logger.warning(f"Error loading {path}: {e}")
        return None


def resize_image(img: np.ndarray, size: Tuple[int, int] = (224, 224)) -> np.ndarray:
    """
    Resize image to (size, size) using Lanczos interpolation.
    Maintains aspect ratio by center-cropping before resize.

    Args:
        img:  RGB numpy array (H, W, 3)
        size: target output (height, width)
    Returns:
        Resized uint8 array (size[0], size[1], 3)
    """
    h, w = img.shape[:2]
    target_h, target_w = size

    # Center crop to square first (preserves face proportions)
    crop_size = min(h, w)
    top  = (h - crop_size) // 2
    left = (w - crop_size) // 2
    img  = img[top:top + crop_size, left:left + crop_size]

    # Resize
    img = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
    return img


def normalize_image(img: np.ndarray) -> np.ndarray:
    """
    Normalize uint8 RGB image to float32 using ImageNet mean+std.

    Args:
        img: uint8 array (H, W, 3), values 0-255
    Returns:
        float32 array (H, W, 3), normalized
    """
    img = img.astype(np.float32) / 255.0
    img = (img - IMAGENET_MEAN) / IMAGENET_STD
    return img


def preprocess_image(
    path: str,
    size: Tuple[int, int] = (224, 224),
    normalize: bool = False,
) -> Optional[np.ndarray]:
    """
    Full preprocessing pipeline for a single image.

    Args:
        path:      path to input image
        size:      target (height, width)
        normalize: if True, apply ImageNet normalization (for direct model input)
                   if False, return uint8 (for saving to disk)
    Returns:
        Processed numpy array, or None on failure
    """
    img = load_image(path)
    if img is None:
        return None

    img = resize_image(img, size)

    if normalize:
        img = normalize_image(img)

    return img


def save_image(img: np.ndarray, out_path: str) -> bool:
    """
    Save uint8 RGB image to PNG.

    Args:
        img:      uint8 (H, W, 3) array
        out_path: destination path
    Returns:
        True on success, False on failure
    """
    try:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        bgr = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_RGB2BGR)
        return cv2.imwrite(str(out_path), bgr)
    except Exception as e:
        logger.warning(f"Error saving {out_path}: {e}")
        return False


def process_directory(
    src_dir: str,
    dst_dir: str,
    size: Tuple[int, int] = (224, 224),
    extensions: Tuple[str, ...] = (".png", ".jpg", ".jpeg"),
    overwrite: bool = False,
) -> dict:
    """
    Batch-process all images in src_dir → dst_dir.
    Preserves subdirectory structure (e.g. train/real/, train/fake/).

    Args:
        src_dir:    source root directory
        dst_dir:    output root directory
        size:       target image size
        extensions: file extensions to process
        overwrite:  re-process if output already exists
    Returns:
        dict with keys: processed, skipped, failed
    """
    src_root = Path(src_dir)
    dst_root = Path(dst_dir)

    if not src_root.exists():
        raise FileNotFoundError(f"Source directory not found: {src_root}")

    stats = {"processed": 0, "skipped": 0, "failed": 0}

    image_paths = [
        p for p in src_root.rglob("*")
        if p.suffix.lower() in extensions
    ]

    total = len(image_paths)
    logger.info(f"Found {total} images in {src_root}")

    for i, src_path in enumerate(image_paths):
        rel_path = src_path.relative_to(src_root)
        dst_path = dst_root / rel_path

        if not overwrite and dst_path.exists():
            stats["skipped"] += 1
            continue

        img = preprocess_image(str(src_path), size=size, normalize=False)
        if img is None:
            stats["failed"] += 1
            continue

        if save_image(img, str(dst_path)):
            stats["processed"] += 1
        else:
            stats["failed"] += 1

        if (i + 1) % 1000 == 0:
            logger.info(f"  Progress: {i+1}/{total} — {stats}")

    logger.info(f"Done. {stats}")
    return stats
