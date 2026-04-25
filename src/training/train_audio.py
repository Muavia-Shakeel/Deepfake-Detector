"""
src/training/train_audio.py
Main training script for the audio classifier.
"""
import sys
import torch
from torch.utils.data import DataLoader
from torch import nn, optim
import argparse

sys.path.append(".")

from src.utils.config_loader import load_config
from src.training.audio_dataset import AudioDataset
from src.training.audio_model import AudioClassifier
from src.training.engine import Trainer

def main():
    parser = argparse.ArgumentParser(description="Deepfake Audio Classifier Training")
    args = parser.parse_args()
    
    cfg = load_config()
    device = torch.device(cfg.training.device if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Dataset and DataLoader
    # NOTE: This assumes an 'audio_index.csv' will be created by a preprocessing script.
    audio_dataset = AudioDataset("data/processed/audio_index.csv")
    audio_loader = DataLoader(audio_dataset, batch_size=cfg.training.batch_size, shuffle=True)
    
    # We will use the same loader for validation for this placeholder script
    val_loader = audio_loader
    
    # Model
    model = AudioClassifier()
    model.to(device)

    # Optimizer, Scheduler, Loss
    optimizer = optim.AdamW(model.parameters(), lr=cfg.training.learning_rate)
    scheduler = None # No scheduler for this simple model
    loss_fn = nn.BCEWithLogitsLoss()

    model_cfg = cfg.models.audio_classifier

    # Trainer
    trainer = Trainer(model, optimizer, scheduler, loss_fn, device, audio_loader, val_loader, cfg, model_cfg)
    
    print("NOTE: This script is a placeholder and will not run without a populated 'data/processed/audio_index.csv'.")
    print("Run the video preprocessing scripts once you have downloaded the video datasets.")
    # trainer.fit() # This line is commented out as it will fail without data

if __name__ == '__main__':
    main()
