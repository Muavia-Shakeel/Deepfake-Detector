"""
src/inference/ensemble.py
Ensemble strategies for combining model predictions.
"""
import torch
import numpy as np

def weighted_average(predictions, weights):
    """
    Combines model predictions using a weighted average.

    Args:
        predictions (list of torch.Tensor): List of prediction tensors (logits) from each model.
        weights (list of float): List of weights for each model.

    Returns:
        torch.Tensor: The ensembled prediction.
    """
    if len(predictions) != len(weights):
        raise ValueError("Length of predictions and weights must be the same.")

    # Convert logits to probabilities
    probs = [torch.sigmoid(p) for p in predictions]
    
    # Calculate weighted average
    weighted_probs = [p * w for p, w in zip(probs, weights)]
    ensembled_prob = torch.sum(torch.stack(weighted_probs), dim=0)
    
    return ensembled_prob

def majority_vote(predictions, threshold=0.5):
    """
    Combines model predictions using a majority vote.

    Args:
        predictions (list of torch.Tensor): List of prediction tensors (logits) from each model.
        threshold (float): Probability threshold to classify as 'fake'.

    Returns:
        torch.Tensor: The ensembled prediction (as a probability).
    """
    # Convert logits to binary predictions
    binary_preds = [(torch.sigmoid(p) > threshold).int() for p in predictions]
    
    # Sum votes
    votes = torch.sum(torch.stack(binary_preds), dim=0)
    
    # Majority wins
    ensembled_pred = (votes > len(predictions) / 2).float()
    
    return ensembled_pred
