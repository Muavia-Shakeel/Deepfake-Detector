"""
src/training/augmentations.py
Image augmentation pipelines using Albumentations.
"""

import albumentations as A
from albumentations.pytorch import ToTensorV2

from src.preprocessing.preprocessor import IMAGENET_MEAN, IMAGENET_STD

def get_train_transforms(cfg):
    """
    Augmentations for the training set.
    Includes normalization and conversion to tensor.
    """
    aug_cfg = cfg.augmentation.train
    return A.Compose([
        A.HorizontalFlip(p=aug_cfg.horizontal_flip),
        A.Rotate(limit=aug_cfg.rotation_limit, p=0.5),
        A.RandomBrightnessContrast(
            brightness_limit=aug_cfg.brightness_contrast,
            contrast_limit=aug_cfg.brightness_contrast,
            p=0.5
        ),
        A.GaussNoise(var_limit=(10.0, 50.0), p=aug_cfg.gaussian_noise),
        A.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ToTensorV2(),
    ])

def get_val_transforms(cfg):
    """
    Augmentations for the validation/test set.
    Just normalization and conversion to tensor.
    """
    return A.Compose([
        A.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ToTensorV2(),
    ])
