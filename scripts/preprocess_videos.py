"""
scripts/preprocess_videos.py
Extracts frames, detects and crops faces, and saves them.
"""
import sys
import os
from pathlib import Path
from tqdm import tqdm
import pandas as pd

sys.path.append(".")

from src.utils.config_loader import load_config
from src.utils.video_utils import extract_frames
from src.preprocessing.face_detector import FaceDetector
from src.preprocessing.preprocessor import resize_image, save_image, load_image

def main():
    cfg = load_config()
    face_detector = FaceDetector(confidence=cfg.preprocessing.min_face_confidence)

    # Example for Celeb-DF
    dataset_name = "celeb-df"
    video_dir = Path(cfg.paths.data_raw) / dataset_name
    output_dir_faces = Path(cfg.paths.faces) / dataset_name
    
    # Read the metadata to distinguish real/fake videos
    metadata_path = video_dir / "List_of_testing_videos.txt"
    if not metadata_path.exists():
        print(f"Error: Metadata file not found at {metadata_path}")
        print("Please ensure you have unzipped the Celeb-DF dataset.")
        return
        
    df = pd.read_csv(metadata_path, delimiter=' ', names=['label', 'path'])
    df['label'] = df['label'].apply(lambda x: 'real' if x == 1 else 'fake')

    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing videos"):
        label = row['label']
        video_path = video_dir / row['path']
        
        if not video_path.exists():
            continue
            
        video_name = video_path.stem
        
        # Create a temp dir for frames
        temp_frame_dir = Path("temp_frames") / video_name
        temp_frame_dir.mkdir(parents=True, exist_ok=True)

        # 1. Extract frames
        frame_paths = extract_frames(str(video_path), str(temp_frame_dir), cfg.preprocessing.frame_interval)

        # 2. Detect and crop faces from frames
        for frame_path in frame_paths:
            image = load_image(frame_path)
            if image is None: continue

            faces = face_detector.detect(image)
            
            for i, face in enumerate(faces):
                cropped_face = face_detector.crop_face(image, face['box'], margin=cfg.preprocessing.face_margin)
                
                # 3. Resize face
                resized_face = resize_image(cropped_face, size=(cfg.preprocessing.face_size, cfg.preprocessing.face_size))
                
                # 4. Save face
                face_filename = f"{video_name}_frame{Path(frame_path).stem.split('_')[1]}_face{i}.png"
                save_dir = output_dir_faces / label
                save_path = save_dir / face_filename
                
                save_image(resized_face, str(save_path))

        # Clean up temp frames
        for frame_path in frame_paths:
            os.remove(frame_path)
        os.rmdir(temp_frame_dir)

if __name__ == '__main__':
    main()
