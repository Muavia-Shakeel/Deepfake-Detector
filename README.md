# Hybrid Ensemble Deepfake Detector

Web-based audio-video deepfake detection platform using ensemble deep learning.

## Team
- Ibrahim Rabbani (301-221001)
- Taha Sohail (301-221051)
- Eisha Tur Raziya (301-221022)

CS 7th A — Hazara University, Mansehra

## Project Structure
```
fyp-deepfake/
├── data/
│   ├── raw/          # Downloaded datasets (celeb-df, faceforensics, dfdc)
│   └── processed/    # Extracted frames, faces, audio
├── models/           # Saved model weights
├── src/
│   ├── preprocessing/  # Frame extraction, face detection
│   ├── training/       # Model training scripts
│   ├── inference/      # Ensemble inference
│   ├── api/            # FastAPI backend
│   └── utils/          # Shared utilities
├── frontend/         # HTML/CSS/Bootstrap UI
├── notebooks/        # Experimentation notebooks
├── docs/             # Project documentation
├── tests/            # Unit tests
└── scripts/          # Setup/utility scripts
```

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Models Used
- XceptionNet — pixel-level texture anomaly detection
- EfficientNet-B0 — general feature extraction
- ViT (Vision Transformer) — long-range dependency detection
- SyncNet — audio-visual lip-sync verification

## Datasets
- Celeb-DF v2
- FaceForensics++
- DFDC (subset)
- ASVspoof (audio)
