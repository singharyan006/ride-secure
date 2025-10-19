import cv2
from pathlib import Path
from typing import Tuple

def open_video(path: str):
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {path}")
    return cap

def video_writer(path: str, fps: float, size: Tuple[int,int]):
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(path), fourcc, fps, size)
    return writer
