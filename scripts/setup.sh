#!/usr/bin/env bash
# ============================================================
# setup.sh — Hybrid Ensemble Deepfake Detector
# One-time environment setup script
# Usage: bash scripts/setup.sh
# ============================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "==========================================="
echo "  Deepfake Detector — Environment Setup"
echo "==========================================="

# ---- 1. Python version check --------------------------------
PYTHON_MIN="3.10"
PYTHON=$(command -v python3 || command -v python)
PYTHON_VERSION=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "[1/6] Python version: $PYTHON_VERSION"
if [[ "$(echo -e "$PYTHON_MIN\n$PYTHON_VERSION" | sort -V | head -1)" != "$PYTHON_MIN" ]]; then
    echo "ERROR: Python >= $PYTHON_MIN required. Found $PYTHON_VERSION."
    exit 1
fi

# ---- 2. Create virtual environment --------------------------
echo "[2/6] Creating virtual environment..."
if [ ! -d "venv" ]; then
    $PYTHON -m venv venv
    echo "       venv created."
else
    echo "       venv already exists, skipping."
fi

# Activate venv
source venv/bin/activate

# ---- 3. Upgrade pip -----------------------------------------
echo "[3/6] Upgrading pip..."
pip install --upgrade pip --quiet

# ---- 4. Install dependencies --------------------------------
echo "[4/6] Installing requirements..."
pip install -r requirements.txt --quiet
echo "       Dependencies installed."

# ---- 5. Create runtime directories --------------------------
echo "[5/6] Creating runtime directories..."
mkdir -p uploads temp logs \
         data/raw/celeb-df \
         data/raw/faceforensics \
         data/raw/dfdc \
         data/processed/frames \
         data/processed/faces \
         data/processed/audio \
         models/xception \
         models/efficientnet \
         models/vit \
         models/audio \
         models/ensemble \
         notebooks
echo "       Directories ready."

# ---- 6. .env setup ------------------------------------------
echo "[6/6] Setting up .env..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "       .env created from .env.example."
    echo "       IMPORTANT: Edit .env and set SECRET_KEY and DEVICE before running."
else
    echo "       .env already exists, skipping."
fi

echo ""
echo "==========================================="
echo "  Setup complete!"
echo "  Activate env:  source venv/bin/activate"
echo "  Run API:       uvicorn src.api.main:app --reload"
echo "==========================================="
