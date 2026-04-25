"""
src/inference/predictor.py
Main class for loading models and making predictions.
"""
import torch
from pathlib import Path

from src.training.model import get_model
from src.inference.ensemble import weighted_average, majority_vote
from src.preprocessing.preprocessor import preprocess_image

class Predictor:
    def __init__(self, cfg):
        self.cfg = cfg
        self.device = torch.device(cfg.training.device if torch.cuda.is_available() else "cpu")
        
        # Load models
        self.models = self._load_models()

    def _load_models(self):
        models = {}
        model_names = ['xceptionnet', 'efficientnet', 'vit'] # Visual models for now
        
        for name in model_names:
            print(f"Loading {name}...")
            model_cfg = getattr(self.cfg.models, name)
            model = get_model(self.cfg, name)
            
            checkpoint_path = Path(model_cfg.save_path)
            if not checkpoint_path.exists():
                print(f"Warning: Checkpoint not found for {name} at {checkpoint_path}. Skipping.")
                continue

            checkpoint = torch.load(checkpoint_path, map_location=self.device)
            model.load_state_dict(checkpoint['model_state_dict'])
            model.to(self.device)
            model.eval()
            models[name] = model
            
        print("All models loaded.")
        return models

    def predict_image(self, image_path):
        """
        Makes a deepfake prediction on a single image.
        """
        if not self.models:
            raise RuntimeError("No models were loaded. Cannot make a prediction.")

        # Preprocess the image
        img_tensor = preprocess_image(image_path, normalize=True)
        if img_tensor is None:
            return None
            
        # Add batch dimension and move to device
        img_tensor = torch.from_numpy(img_tensor).permute(2, 0, 1).unsqueeze(0).to(self.device)

        # Get predictions from each model
        predictions = []
        with torch.no_grad():
            for model in self.models.values():
                pred = model(img_tensor).squeeze()
                predictions.append(pred)

        # Ensemble the predictions
        ensemble_cfg = self.cfg.ensemble
        if ensemble_cfg.strategy == 'weighted_average':
            weights = [getattr(ensemble_cfg.weights, name) for name in self.models.keys()]
            final_prob = weighted_average(predictions, weights)
        elif ensemble_cfg.strategy == 'majority_vote':
            final_prob = majority_vote(predictions)
        else:
            # Default to simple average if strategy is unknown
            final_prob = weighted_average(predictions, [1.0] * len(predictions))

        final_prob = final_prob.item()
        verdict = "Fake" if final_prob > ensemble_cfg.threshold else "Real"
        
        return {
            "final_probability": final_prob,
            "verdict": verdict,
            "individual_probabilities": {name: torch.sigmoid(p).item() for name, p in zip(self.models.keys(), predictions)}
        }
