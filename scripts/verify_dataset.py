"""
scripts/verify_dataset.py
Loads a few samples from the DeepfakeDataset and visualizes them
with augmentations to verify correctness.
"""
import sys
import matplotlib.pyplot as plt
import torch
import cv2
import numpy as np

# Add src to path to allow direct script execution
sys.path.append(".")

from src.utils.config_loader import load_config
from src.training.dataset import DeepfakeDataset
from src.training.augmentations import get_train_transforms

def tensor_to_cv2(tensor_img):
    """Convert a PyTorch tensor (C, H, W) to an OpenCV image (H, W, C)"""
    # Denormalize
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    
    # Check if tensor is on GPU and move to CPU
    if tensor_img.is_cuda:
        tensor_img = tensor_img.cpu()

    # Convert to numpy and transpose
    img = tensor_img.numpy().transpose((1, 2, 0))
    
    # Denormalize
    img = std * img + mean
    img = np.clip(img, 0, 1)
    
    # Convert to BGR for OpenCV
    img = (img * 255).astype(np.uint8)
    return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

def verify():
    print("Loading config...")
    cfg = load_config()

    print("Setting up training dataset...")
    train_transforms = get_train_transforms(cfg)
    train_dataset = DeepfakeDataset(
        index_csv="data/processed/faces_index.csv",
        data_root="data/processed",
        split="train",
        transform=train_transforms
    )

    print(f"Train dataset size: {len(train_dataset)}")
    
    if len(train_dataset) == 0:
        print("Dataset is empty. Check paths in config.yaml and faces_index.csv")
        return

    print("Visualizing 8 random augmented samples...")
    figure = plt.figure(figsize=(12, 6))
    cols, rows = 4, 2
    
    # Get 8 random indices
    indices = torch.randperm(len(train_dataset))[:8]

    for i, idx_tensor in enumerate(indices):
        idx = idx_tensor.item() # Convert tensor to int
        img_tensor, label = train_dataset[idx]
        
        # Convert tensor back to displayable image
        img_display = tensor_to_cv2(img_tensor)

        ax = figure.add_subplot(rows, cols, i + 1)
        ax.set_title(f"Label: {'Fake' if label == 1 else 'Real'}")
        ax.axis("off")
        
        # Display BGR image with matplotlib (needs conversion back to RGB)
        ax.imshow(cv2.cvtColor(img_display, cv2.COLOR_BGR2RGB))

    plt.tight_layout()
    # Save the figure instead of showing it for non-interactive environments
    output_path = "docs/step4_augmentation_verification.png"
    plt.savefig(output_path)
    print(f"Saved verification plot to {output_path}")

if __name__ == "__main__":
    verify()
