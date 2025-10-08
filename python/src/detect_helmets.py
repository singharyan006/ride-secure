#!/usr/bin/env python3
"""
detect_helmets.py

Detect riders (person on bicycle/motorcycle) and whether they wear helmets.
Outputs:
 - annotated video (MP4)
 - violations CSV with specified fields

Requirements: see requirements.txt.

Usage example:
    python detect_helmets.py --input video.mp4 --output output.mp4 --helmet-model helmet_model.pt
    python detect_helmets.py --input 2.mp4 --output output.mp4 --helmet-model helmet_model.pt
"""

import argparse
import os
import time
from datetime import datetime, timedelta
import csv
from pathlib import Path
from collections import defaultdict

import cv2
import numpy as np
import pandas as pd
from tqdm import tqdm

# Ultralytics YOLO (v8)
from ultralytics import YOLO

# Deep SORT realtime
from deep_sort_realtime.deepsort_tracker import DeepSort

# -----------------------
# Helpers
# -----------------------
def xyxy_to_xywh(box):
    x1, y1, x2, y2 = box
    w = x2 - x1
    h = y2 - y1
    return [int(x1), int(y1), int(w), int(h)]

def iou_box(a, b):
    # a and b are [x1,y1,x2,y2]
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)
    if inter_x2 <= inter_x1 or inter_y2 <= inter_y1:
        return 0.0
    inter_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
    a_area = max(0, ax2 - ax1) * max(0, ay2 - ay1)
    b_area = max(0, bx2 - bx1) * max(0, by2 - by1)
    return inter_area / (a_area + b_area - inter_area + 1e-9)

def center(box):
    x1, y1, x2, y2 = box
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

# -----------------------
# Main
# -----------------------
def main(args):
    # Prepare paths
    input_path = Path(args.input)
    assert input_path.exists(), f"Input video not found: {input_path}"
    out_path = Path(args.output)
    csv_path = Path(args.csv)

    # Load models
    print("Loading detection models (this may download weights if missing)...")
    # 1) COCO model for person + bicycle/motorcycle
    coco_model = YOLO(args.coco_model)  # will download yolov8n.pt if not found
    # 2) Helmet model (user-provided or downloaded)
    helmet_model = YOLO(args.helmet_model)

    # Create tracker
    tracker = DeepSort(max_age=30,
                       n_init=1,  # how many frames before confirmed (low means faster)
                       nms_max_overlap=1.0)

    # Video IO
    cap = cv2.VideoCapture(str(input_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    print(f"Video: {input_path}, {width}x{height} @ {fps:.2f} FPS, {total_frames} frames")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(out_path), fourcc, fps, (width, height))

    # CSV prepare
    csv_fields = ["video_filename", "frame_id", "frame_timestamp_ms", "wall_clock_iso",
                  "track_id", "class", "confidence", "xmin", "ymin", "xmax", "ymax"]
    csv_rows = []

    # Track local state to avoid duplicate flood logging
    track_last_logged_frame = defaultdict(lambda: -9999)
    track_violation_state = defaultdict(lambda: False)

    start_wall = datetime.now()
    frame_idx = 0

    pbar = tqdm(total=total_frames if total_frames>0 else None, desc="Processing frames")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1
        frame_time_ms = int((frame_idx / fps) * 1000)
        wall_time = start_wall + timedelta(milliseconds=frame_time_ms)
        wall_time_iso = wall_time.isoformat(sep=' ', timespec='milliseconds')

        # ---------- Detect persons & bikes in this frame (COCO)
        # Run model; get first results object
        coco_results = coco_model(frame)[0]
        # Each row in coco_results.boxes.data is (x1,y1,x2,y2,conf,cls)
        boxes_data = coco_results.boxes.data.cpu().numpy() if hasattr(coco_results.boxes, "data") else coco_results.boxes.cpu().numpy()
        persons = []
        bikes = []
        for row in boxes_data:
            x1, y1, x2, y2, conf, cls = row
            cls = int(cls)
            cls_name = coco_model.model.names.get(cls, str(cls)) if hasattr(coco_model, "model") else str(cls)
            if conf < args.conf:
                continue
            # Accept person and bike-like classes
            if cls_name.lower() == "person":
                persons.append((int(x1), int(y1), int(x2), int(y2), float(conf)))
            elif cls_name.lower() in ("motorcycle", "bicycle", "motorbike", "bike"):
                bikes.append((int(x1), int(y1), int(x2), int(y2), float(conf)))

        # ---------- Detect helmets in frame (helmet_model)
        helmet_results = helmet_model(frame)[0]
        helmet_boxes = []
        helmet_data = helmet_results.boxes.data.cpu().numpy() if hasattr(helmet_results.boxes, "data") else helmet_results.boxes.cpu().numpy()
        # Helmet model class names: try to find any class name that contains 'helmet' or 'nohelmet'
        helmet_class_ids = []
        if hasattr(helmet_model, "model"):
            for cid, name in helmet_model.model.names.items():
                if "helmet" in name.lower() or "hardhat" in name.lower():
                    helmet_class_ids.append(int(cid))
        # If empty, we'll accept all detections from helmet model as helmet-class predictions.
        for row in helmet_data:
            x1, y1, x2, y2, conf, cls = row
            cls = int(cls)
            if conf < args.conf:
                continue
            if (len(helmet_class_ids) == 0) or (cls in helmet_class_ids):
                helmet_boxes.append((int(x1), int(y1), int(x2), int(y2), float(conf)))

        # ---------- Heuristic: identify riders (person close to a bike)
        rider_candidates = []
        for p in persons:
            px1, py1, px2, py2, pconf = p
            p_cx, p_cy = center((px1, py1, px2, py2))
            is_rider = False
            for b in bikes:
                bx1, by1, bx2, by2, bconf = b
                bike_w = bx2 - bx1
                bike_h = by2 - by1
                b_cx, b_cy = center((bx1, by1, bx2, by2))
                dx = abs(p_cx - b_cx)
                dy = abs(p_cy - b_cy)
                # If bounding boxes intersect or centers are close relative to bike width/height
                if iou_box((px1,py1,px2,py2),(bx1,by1,bx2,by2)) > 0.01 or (dx < 1.5*bike_w and dy < 1.5*bike_h):
                    is_rider = True
                    break
            if is_rider:
                rider_candidates.append(p)

        # Optionally, if no bikes were found but you still want to treat all persons as riders:
        if args.treat_all_persons_as_riders and len(rider_candidates) == 0:
            rider_candidates = persons.copy()

        # Prepare detections for tracker: format ([x,y,w,h], conf, class_name)
        detections_for_tracker = []
        for p in rider_candidates:
            x1,y1,x2,y2,pconf = p
            detections_for_tracker.append(( [int(x1), int(y1), int(x2 - x1), int(y2 - y1)], float(pconf), "person"))

        # Update tracks
        tracks = tracker.update_tracks(detections_for_tracker, frame=frame)

        # For drawing and logging
        annotated = frame.copy()

        # For quick helmet lookup, build list of helmet bboxes
        helmet_boxes_list = helmet_boxes  # (x1,y1,x2,y2,conf)

        for track in tracks:
            if not track.is_confirmed():
                continue
            track_id = track.track_id
            l, t, r, b = track.to_ltrb()  # left top right bottom
            l, t, r, b = int(l), int(t), int(r), int(b)
            # Before:
            # track_conf = track.det_conf if hasattr(track, "det_conf") else 1.0

            # Use this instead:
            raw_track_conf = getattr(track, "det_conf", None)
            try:
                track_conf = float(raw_track_conf) if raw_track_conf is not None else 0.0
            except Exception:
                track_conf = 0.0


            # Define head region inside person bbox (top fraction)
            head_h_frac = args.head_fraction  # e.g., 0.35
            head_x1 = l
            head_y1 = t
            head_x2 = r
            head_y2 = int(t + (b - t) * head_h_frac)
            head_bbox = (head_x1, head_y1, head_x2, head_y2)

            # Check if any helmet box overlaps head_bbox sufficiently
            helmet_present = False
            helmet_confidence_best = 0.0
            for hb in helmet_boxes_list:
                hx1, hy1, hx2, hy2, hconf = hb
                ov = iou_box(head_bbox, (hx1, hy1, hx2, hy2))
                # Also accept if helmet center lies within head bbox
                h_cx, h_cy = center((hx1, hy1, hx2, hy2))
                inside = (head_x1 <= h_cx <= head_x2) and (head_y1 <= h_cy <= head_y2)
                if ov >= args.helmet_iou_threshold or inside:
                    helmet_present = True
                    if hconf > helmet_confidence_best:
                        helmet_confidence_best = hconf

            # Annotate
            color = (0, 255, 0) if helmet_present else (0, 0, 255)
            label = f"ID{track_id} {'Helmet' if helmet_present else 'NO_HELMET'}"
            cv2.rectangle(annotated, (l, t), (r, b), color, 2)
            cv2.rectangle(annotated, (head_x1, head_y1), (head_x2, head_y2), (255, 200, 0), 1)
            cv2.putText(annotated, label, (l, max(t-6,10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # Decide logging: if no helmet => violation
            if not helmet_present:
                # Log on first detection for this track, and then repeat every log_repeat_frames
                last = track_last_logged_frame[track_id]
                if (frame_idx - last) >= args.log_repeat_frames:
                    # Append CSV row
                    row = {
                        "video_filename": input_path.name,
                        "frame_id": frame_idx,
                        "frame_timestamp_ms": frame_time_ms,
                        "wall_clock_iso": wall_time_iso,
                        "track_id": track_id,
                        "class": "no-helmet",
                        "confidence": float(track_conf),
                        "xmin": int(l),
                        "ymin": int(t),
                        "xmax": int(r),
                        "ymax": int(b)
                    }
                    csv_rows.append(row)
                    track_last_logged_frame[track_id] = frame_idx
                    track_violation_state[track_id] = True
            else:
                track_violation_state[track_id] = False

        # Write annotated frame to output
        writer.write(annotated)
        pbar.update(1)

    pbar.close()
    cap.release()
    writer.release()

    # Save CSV
    if len(csv_rows) > 0:
        df = pd.DataFrame(csv_rows, columns=csv_fields)
        df.to_csv(csv_path, index=False)
        print(f"Saved violations CSV to: {csv_path} ({len(df)} rows)")
    else:
        print("No violations logged; CSV not created.")
    print(f"Annotated video saved to: {out_path}")
    print("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Helmet detection + tracking for uploaded MP4.")
    parser.add_argument("--input", required=True, help="Input .mp4 video path")
    parser.add_argument("--output", default="output.mp4", help="Path to annotated output MP4")
    parser.add_argument("--csv", default="violations.csv", help="Path to output CSV")
    parser.add_argument("--helmet-model", default="helmet_model.pt", help="YOLOv8 helmet model weights (pt)")
    parser.add_argument("--coco-model", default="yolov8n.pt", help="General COCO YOLOv8 model for person+bike detection")
    parser.add_argument("--conf", type=float, default=0.4, help="Detection confidence threshold (default 0.4)")
    parser.add_argument("--helmet-iou-threshold", type=float, default=0.1, help="IOU threshold to match helmet to head region")
    parser.add_argument("--head-fraction", type=float, default=0.35, help="Top fraction of person bbox considered head region")
    parser.add_argument("--log-repeat-frames", type=int, default=30, help="How many frames between repeated logs for same track")
    parser.add_argument("--treat-all-persons-as-riders", action="store_true",
                        help="If set, treat all detected persons as riders (useful if bike detection fails)")
    args = parser.parse_args()
    main(args)