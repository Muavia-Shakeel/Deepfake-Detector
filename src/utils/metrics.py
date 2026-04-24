"""
src/utils/metrics.py
Functions for calculating performance metrics.
"""
import torch

def accuracy(y_true, y_pred):
    """
    Calculates accuracy.
    y_pred is expected to be logits.
    """
    # Get predictions
    y_pred_tags = torch.round(torch.sigmoid(y_pred))
    
    # Calculate accuracy
    correct_pred = (y_pred_tags == y_true).float()
    acc = correct_pred.sum() / len(correct_pred)
    acc = torch.round(acc * 100)
    
    return acc
