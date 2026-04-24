"""
src/training/train.py
Main training script for a single model.
"""
import sys
import torch
from torch.utils.data import DataLoader
from torch import nn, optim

# Add src to path to allow direct script execution
sys.path.append(".")

from src.utils.config_loader import load_config
from src.training.dataset import DeepfakeDataset, collate_fn
from src.training.augmentations import get_train_transforms, get_val_transforms
from src.training.model import get_model
from src.training.engine import Trainer

def main(model_name='xceptionnet'):
    """
    Main training function.
    """
    cfg = load_config()
    device = torch.device(cfg.training.device if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Datasets and DataLoaders
    train_transforms = get_train_transforms(cfg)
    val_transforms = get_val_transforms(cfg)
    
    train_dataset = DeepfakeDataset("data/processed/faces_index.csv", "data/processed", "train", train_transforms)
    val_dataset = DeepfakeDataset("data/processed/faces_index.csv", "data/processed", "val", val_transforms)
    
    train_loader = DataLoader(train_dataset, batch_size=cfg.training.batch_size, shuffle=True, 
                              num_workers=cfg.training.num_workers, pin_memory=cfg.training.pin_memory,
                              collate_fn=collate_fn)
    val_loader = DataLoader(val_dataset, batch_size=cfg.training.batch_size, shuffle=False,
                            num_workers=cfg.training.num_workers, pin_memory=cfg.training.pin_memory)
    
    # Model
    model = get_model(cfg, model_name)
    model.to(device)

    # Optimizer, Scheduler, Loss
    optimizer = optim.AdamW(model.parameters(), lr=cfg.training.learning_rate, weight_decay=cfg.training.weight_decay)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=cfg.training.num_epochs)
    loss_fn = nn.BCEWithLogitsLoss()

    # Trainer
    trainer = Trainer(model, optimizer, scheduler, loss_fn, device, train_loader, val_loader, cfg)
    
    # Start training
    trainer.fit()

if __name__ == '__main__':
    main()
