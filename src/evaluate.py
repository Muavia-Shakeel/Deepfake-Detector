"""
src/evaluate.py
Main evaluation script.
"""
import sys
import torch
import json
from torch.utils.data import DataLoader
from tqdm import tqdm
import pandas as pd

sys.path.append(".")

from src.utils.config_loader import load_config
from src.inference.predictor import Predictor
from src.training.dataset import DeepfakeDataset, collate_fn
from src.training.augmentations import get_val_transforms
from src.utils.metrics import get_all_metrics

def evaluate():
    cfg = load_config()
    device = torch.device(cfg.training.device if torch.cuda.is_available() else "cpu")

    # Use the predictor to load all models
    predictor = Predictor(cfg)
    
    # Test DataLoader
    test_transforms = get_val_transforms(cfg)
    test_dataset = DeepfakeDataset("data/processed/faces_index.csv", "data/processed", "test", test_transforms)
    test_loader = DataLoader(test_dataset, batch_size=cfg.training.batch_size, shuffle=False,
                             num_workers=cfg.training.num_workers, pin_memory=cfg.training.pin_memory,
                             collate_fn=collate_fn)
    
    all_results = {}

    # Evaluate individual models
    for name, model in predictor.models.items():
        print(f"Evaluating {name}...")
        y_true, y_pred_probs = [], []
        with torch.no_grad():
            for data, target in tqdm(test_loader, desc=f"Testing {name}"):
                data = data.to(device)
                logits = model(data).squeeze()
                probs = torch.sigmoid(logits)
                
                y_true.extend(target.cpu())
                y_pred_probs.extend(probs.cpu())

        y_true_tensor = torch.tensor(y_true)
        y_pred_probs_tensor = torch.tensor(y_pred_probs)
        metrics = get_all_metrics(y_true_tensor, y_pred_probs_tensor)
        all_results[name] = metrics
        print(f"Results for {name}: {metrics}")

    # Evaluate ensemble
    print("Evaluating ensemble...")
    y_true_ensemble, y_pred_probs_ensemble = [], []
    with torch.no_grad():
        for i, (data, target) in enumerate(tqdm(test_loader, desc="Testing Ensemble")):
            # The predictor expects image paths, not tensors.
            # So, we'll iterate through the dataset to get paths.
            start_index = i * cfg.training.batch_size
            end_index = start_index + len(target)
            
            for j in range(len(target)):
                actual_index = start_index + j
                image_path = "data/processed/" + test_dataset.df.iloc[actual_index]['path']
                
                result = predictor.predict_image(image_path)
                if result:
                    y_pred_probs_ensemble.append(result['final_probability'])
                    y_true_ensemble.append(target[j].item())

    y_true_tensor_ens = torch.tensor(y_true_ensemble)
    y_pred_probs_tensor_ens = torch.tensor(y_pred_probs_ensemble)
    ensemble_metrics = get_all_metrics(y_true_tensor_ens, y_pred_probs_tensor_ens)
    all_results['ensemble'] = ensemble_metrics
    print(f"Results for Ensemble: {ensemble_metrics}")

    # Save results
    with open("evaluation_results.json", "w") as f:
        json.dump(all_results, f, indent=4)
    print("Evaluation results saved to evaluation_results.json")

if __name__ == '__main__':
    evaluate()
