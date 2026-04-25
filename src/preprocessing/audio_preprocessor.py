"""
src/preprocessing/audio_preprocessor.py
Utilities for extracting audio from videos and converting to spectrograms.
"""
import subprocess
import librosa
import librosa.display
import numpy as np
from pathlib import Path

def extract_audio(video_path: str, audio_path: str):
    """
    Extracts the audio track from a video file using ffmpeg.
    
    Args:
        video_path (str): Path to the input video.
        audio_path (str): Path to save the output audio file (e.g., .wav).
    """
    Path(audio_path).parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-i", str(video_path),
        "-ab", "160k",  # Audio bitrate
        "-ac", "1",      # Mono channel
        "-ar", "16000",  # Sample rate
        "-vn",           # No video
        str(audio_path),
        "-y",            # Overwrite output file if it exists
        "-hide_banner",
        "-loglevel", "error"
    ]
    try:
        subprocess.run(command, check=True)
    except FileNotFoundError:
        print("ffmpeg not found. Please install ffmpeg to process audio.")
        raise
    except subprocess.CalledProcessError as e:
        print(f"Error extracting audio from {video_path}: {e}")

def audio_to_melspectrogram(audio_path: str, cfg):
    """
    Converts an audio file to a Mel spectrogram.
    
    Args:
        audio_path (str): Path to the audio file.
        cfg: The project configuration object.
        
    Returns:
        np.ndarray: The Mel spectrogram.
    """
    y, sr = librosa.load(audio_path, sr=cfg.preprocessing.audio_sample_rate)
    
    mel_spectrogram = librosa.feature.melspectrogram(
        y=y,
        sr=sr,
        n_fft=cfg.preprocessing.n_fft,
        hop_length=cfg.preprocessing.hop_length,
        n_mels=cfg.preprocessing.n_mfcc  # Using n_mfcc for number of mel bands
    )
    
    # Convert to log scale (dB)
    log_mel_spectrogram = librosa.power_to_db(mel_spectrogram, ref=np.max)
    
    return log_mel_spectrogram
