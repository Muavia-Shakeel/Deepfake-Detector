"""
src/utils/video_utils.py
Utilities for processing video files.
"""
import cv2
import os
from pathlib import Path
from typing import List

def extract_frames(video_path: str, out_dir: str, frame_interval: int) -> List[str]:
    """
    Extracts frames from a video at a given interval.

    Args:
        video_path (str): Path to the video file.
        out_dir (str): Directory to save extracted frames.
        frame_interval (int): Interval to save frames (e.g., 10 means every 10th frame).

    Returns:
        List[str]: A list of paths to the extracted frames.
    """
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return []

    frame_count = 0
    saved_count = 0
    frame_paths = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % frame_interval == 0:
            frame_filename = f"frame_{saved_count:04d}.png"
            frame_path = os.path.join(out_dir, frame_filename)
            cv2.imwrite(frame_path, frame)
            frame_paths.append(frame_path)
            saved_count += 1
            
        frame_count += 1

    cap.release()
    return frame_paths
