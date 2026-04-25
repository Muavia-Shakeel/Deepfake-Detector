"""
src/api/main.py
FastAPI application for deepfake detection.
"""
import sys
import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
import uuid

# Add src to path
sys.path.append(".")

from src.utils.config_loader import load_config
from src.inference.predictor import Predictor
from src.utils.video_utils import extract_frames

# --- App Initialization ---
app = FastAPI(title="Deepfake Detector API")
cfg = load_config()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=cfg.api.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the predictor on startup
predictor = None

@app.on_event("startup")
def load_predictor():
    global predictor
    print("Loading models...")
    predictor = Predictor(cfg)
    print("Models loaded successfully.")

# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Deepfake Detector API is running."}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not predictor:
        raise HTTPException(status_code=503, detail="Models are not loaded yet.")

    print(f"Received file: {file.filename}")

    # Create a temporary directory for the upload
    temp_dir = Path(cfg.paths.uploads) / str(uuid.uuid4())
    temp_dir.mkdir(parents=True, exist_ok=True)
    file_path = temp_dir / file.filename

    try:
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"Saved file to: {file_path}")

        # Check file extension
        ext = os.path.splitext(file.filename)[1].lower().replace('.', '')
        print(f"File extension: {ext}")
        if ext not in cfg.api.allowed_extensions:
            print("File type not allowed.")
            raise HTTPException(status_code=400, detail=f"Invalid file type: {ext}")

        # --- Process based on file type ---
        image_extensions = ['jpg', 'jpeg', 'png']
        video_extensions = ['mp4', 'avi', 'mov']

        if ext in image_extensions:
            # Single image prediction
            print("Processing as single image.")
            result = predictor.predict_image(str(file_path))
            if not result:
                print("Prediction failed for image.")
                raise HTTPException(status_code=500, detail="Prediction failed for image.")
            print(f"Prediction result: {result}")
            return result

        elif ext in video_extensions:
            # Video prediction
            print("Processing as video.")
            frames = extract_frames(str(file_path), str(temp_dir), cfg.preprocessing.frame_interval)
            if not frames:
                print("Could not extract frames from video.")
                raise HTTPException(status_code=500, detail="Could not extract frames from video.")
            
            # Predict on each frame and average the results
            video_probs = []
            for frame_path in frames:
                frame_result = predictor.predict_image(frame_path)
                if frame_result:
                    video_probs.append(frame_result['final_probability'])
            
            if not video_probs:
                print("Prediction failed for all video frames.")
                raise HTTPException(status_code=500, detail="Prediction failed for all video frames.")

            avg_prob = sum(video_probs) / len(video_probs)
            verdict = "Fake" if avg_prob > cfg.ensemble.threshold else "Real"
            print(f"Final probability: {avg_prob}, Verdict: {verdict}")
            return {
                "final_probability": avg_prob,
                "verdict": verdict,
                "frame_count": len(frames),
            }
        
    finally:
        # Clean up the temporary directory
        if cfg.api.delete_after_inference and temp_dir.exists():
            shutil.rmtree(temp_dir)
            print(f"Cleaned up temp directory: {temp_dir}")

    raise HTTPException(status_code=500, detail="Server error processing file.")


if __name__ == '__main__':
    uvicorn.run(app, host=cfg.api.host, port=cfg.api.port)
