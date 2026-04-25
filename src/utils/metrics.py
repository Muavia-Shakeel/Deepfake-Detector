"""
src/utils/metrics.py
Functions for calculating performance metrics.
"""
import torch
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

def accuracy(y_true, y_pred):
    """
    Calculates accuracy for the training loop.
    y_pred is expected to be logits.
    """
    y_pred_tags = torch.round(torch.sigmoid(y_pred))
    correct_pred = (y_pred_tags == y_true).float()
    acc = correct_pred.sum() / len(correct_pred)
    return acc * 100

def get_all_metrics(y_true, y_pred_probs):
    """
    Calculates all classification metrics.
    y_pred_probs is expected to be probabilities (post-sigmoid).
    """
    y_pred_binary = (y_pred_probs > 0.5).int()

    y_true_np = y_true.cpu().numpy()
    y_pred_binary_np = y_pred_binary.cpu().numpy()
    y_pred_probs_np = y_pred_probs.cpu().numpy()

    metrics = {
        'accuracy': accuracy_score(y_true_np, y_pred_binary_np),
        'precision': precision_score(y_true_np, y_pred_binary_np),
        'recall': recall_score(y_true_np, y_pred_binary_np),
        'f1_score': f1_score(y_true_np, y_pred_binary_np),
        'auc_roc': roc_auc_score(y_true_np, y_pred_probs_np)
    }
    
    return metrics

