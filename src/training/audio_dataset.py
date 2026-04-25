"""
src/training/audio_dataset.py
Custom PyTorch Dataset for loading audio spectrograms.
"""
import torch
from torch.utils.data import Dataset
import pandas as pd
from pathlib import Path
import numpy as np

class AudioDataset(Dataset):
    def __init__(self, index_csv, transform=None):
        self.df = pd.read_csv(index_csv)
        self.transform = transform
        self.class_to_idx = {'real': 0, 'fake': 1}

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        spectrogram_path = row['spectrogram_path']
        label_str = row['label']
        
        # Load spectrogram (saved as .npy)
        spectrogram = np.load(spectrogram_path)
        
        # Add a channel dimension (H, W) -> (1, H, W)
        spectrogram = np.expand_dims(spectrogram, axis=0)

        # Apply transforms if any
        if self.transform:
            spectrogram = self.transform(spectrogram)
            
        label = self.class_to_idx[label_str]
        
        return torch.tensor(spectrogram, dtype=torch.float32), torch.tensor(label, dtype=torch.long)
