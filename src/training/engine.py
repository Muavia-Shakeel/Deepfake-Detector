"""
src/training/engine.py
Training and evaluation engine.
"""
import torch
from tqdm import tqdm
import os
from pathlib import Path

from src.utils.metrics import accuracy

class Trainer:
    def __init__(self, model, optimizer, scheduler, loss_fn, device, train_loader, val_loader, cfg):
        self.model = model
        self.optimizer = optimizer
        self.scheduler = scheduler
        self.loss_fn = loss_fn
        self.device = device
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.cfg = cfg
        self.best_val_loss = float('inf')
        self.scaler = torch.cuda.amp.GradScaler(enabled=cfg.training.mixed_precision)

    def train_one_epoch(self):
        self.model.train()
        total_loss, total_acc = 0, 0
        
        loop = tqdm(self.train_loader, leave=True)
        for batch_idx, (data, target) in enumerate(loop):
            data, target = data.to(self.device), target.to(self.device).float()

            # Forward pass
            with torch.cuda.amp.autocast(enabled=self.cfg.training.mixed_precision):
                logits = self.model(data).squeeze()
                loss = self.loss_fn(logits, target)
            
            # Backward pass and optimization
            self.optimizer.zero_grad()
            self.scaler.scale(loss).backward()
            self.scaler.step(self.optimizer)
            self.scaler.update()

            total_loss += loss.item()
            total_acc += accuracy(target, logits)

            loop.set_postfix(loss=loss.item(), acc=total_acc / (batch_idx + 1))
        
        return total_loss / len(self.train_loader), total_acc / len(self.train_loader)

    def evaluate(self):
        self.model.eval()
        total_loss, total_acc = 0, 0

        with torch.no_grad():
            for data, target in self.val_loader:
                data, target = data.to(self.device), target.to(self.device).float()
                
                with torch.cuda.amp.autocast(enabled=self.cfg.training.mixed_precision):
                    logits = self.model(data).squeeze()
                    loss = self.loss_fn(logits, target)
                
                total_loss += loss.item()
                total_acc += accuracy(target, logits)

        return total_loss / len(self.val_loader), total_acc / len(self.val_loader)

    def fit(self):
        for epoch in range(self.cfg.training.num_epochs):
            print(f"Epoch {epoch+1}/{self.cfg.training.num_epochs}")
            train_loss, train_acc = self.train_one_epoch()
            val_loss, val_acc = self.evaluate()
            
            if self.scheduler:
                self.scheduler.step()

            print(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
            print(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")

            if val_loss < self.best_val_loss:
                self.best_val_loss = val_loss
                self.save_checkpoint('best.pth')
        
        self.save_checkpoint('last.pth')

    def save_checkpoint(self, filename):
        save_path = Path(self.cfg.models.xceptionnet.save_path).parent / filename
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        checkpoint = {
            'epoch': self.cfg.training.num_epochs,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'val_loss': self.best_val_loss
        }
        torch.save(checkpoint, save_path)
        print(f"Checkpoint saved to {save_path}")
