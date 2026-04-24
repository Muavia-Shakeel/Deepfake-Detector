"""
src/training/model.py
Defines the model architecture.
"""
import timm
from torch import nn

def get_model(cfg, model_name):
    """
    Loads a pretrained model from timm and replaces the classifier.
    """
    if model_name == 'xceptionnet':
        model_cfg = cfg.models.xceptionnet
    elif model_name == 'efficientnet':
        model_cfg = cfg.models.efficientnet
    elif model_name == 'vit':
        model_cfg = cfg.models.vit
    else:
        raise ValueError(f"Unknown model name: {model_name}")

    model = timm.create_model(
        model_cfg.variant if 'variant' in model_cfg.__dict__ else 'xception',
        pretrained=model_cfg.pretrained,
        num_classes=1 # Use 1 for binary classification with BCEWithLogitsLoss
    )

    # You can customize the classifier head here if needed
    # For timm models, num_classes argument usually handles this.
    # Example of custom head:
    # if hasattr(model, 'fc'):
    #     in_features = model.fc.in_features
    #     model.fc = nn.Sequential(
    #         nn.Dropout(p=model_cfg.dropout),
    #         nn.Linear(in_features, model_cfg.num_classes)
    #     )
    
    return model
