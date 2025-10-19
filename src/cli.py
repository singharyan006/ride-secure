#!/usr/bin/env python3
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

import cv2
from tqdm import tqdm

from .config import (ANNOTATED_DIR, CSV_DIR, DEFAULT_COCO_MODEL, DEFAULT_HELMET_MODEL,
                     DEFAULT_CONF, DEFAULT_HEAD_FRACTION, DEFAULT_HELMET_IOU, DEFAULT_LOG_REPEAT_FRAMES)
from .model_registry import resolve_model_path
from .detector import Detector
from .tracker import Tracker
from .video_io import open_video, video_writer
from .logger import save_csv
from .utils import iou_box, center, safe_float

"""
Run this file using:
uv run -- python -m src.cli --input data/videos/test_video_1.mp4 --helmet-model custom_helmet --coco-model yolov8n --output outputs/annotated_videos/output.mp4 --csv outputs/csv_logs/violations.csv --conf 0.4
"""


def parse_args():
    p = argparse.ArgumentParser(description="Helmet detection pipeline (modular).")
    p.add_argument("--input", required=True, help="Input .mp4 path")
    p.add_argument("--output", default=str(ANNOTATED_DIR/"output.mp4"), help="Annotated output path")
    p.add_argument("--csv", default=str(CSV_DIR/"violations.csv"), help="CSV output path")
    p.add_argument("--helmet-model", default=DEFAULT_HELMET_MODEL, help="helmet model name or path")
    p.add_argument("--coco-model", default=DEFAULT_COCO_MODEL, help="coco model name or path")
    p.add_argument("--conf", type=float, default=DEFAULT_CONF)
    p.add_argument("--head-fraction", type=float, default=DEFAULT_HEAD_FRACTION)
    p.add_argument("--helmet-iou-threshold", type=float, default=DEFAULT_HELMET_IOU)
    p.add_argument("--log-repeat-frames", type=int, default=DEFAULT_LOG_REPEAT_FRAMES)
    p.add_argument("--treat-all-persons-as-riders", action="store_true")
    return p.parse_args()

def main():
    args = parse_args()
    input_path = Path(args.input)
    assert input_path.exists(), f"Input does not exist: {input_path}"

    # Resolve models via registry or path
    coco_model_path = resolve_model_path(args.coco_model, category="detection")
    helmet_model_path = resolve_model_path(args.helmet_model, category="detection")
    print("Using COCO model:", coco_model_path)
    print("Using helmet model:", helmet_model_path)

    # init components
    coco = Detector(str(coco_model_path), conf_thresh=args.conf)
    helmet = Detector(str(helmet_model_path), conf_thresh=args.conf)
    tracker = Tracker(max_age=30, n_init=1)

    cap = open_video(str(input_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    writer = video_writer(str(out_path), fps, (width, height))

    start_wall = datetime.now()
    frame_idx = 0
    rows = []
    track_last_logged_frame = defaultdict(lambda: -9999)
    last_conf_by_track = defaultdict(lambda: 0.0)

    pbar = tqdm(total=total_frames if total_frames>0 else None, desc="Processing frames")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1
        frame_time_ms = int((frame_idx / fps) * 1000)
        wall_time = start_wall + timedelta(milliseconds=frame_time_ms)
        wall_time_iso = wall_time.isoformat(sep=' ', timespec='milliseconds')

        # detections
        coco_boxes = coco.predict(frame)
        helmet_boxes = helmet.predict(frame)

        # classify coco detections: persons and bikes
        persons = [b for b in coco_boxes if coco.class_name(b[5]).lower() == "person"]
        bikes = [b for b in coco_boxes if coco.class_name(b[5]).lower() in ("motorcycle","bicycle","motorbike","bike")]

        # riders = person close to a bike
        riders = []
        for pbox in persons:
            px1,py1,px2,py2, pconf, _ = pbox
            is_rider = False
            for bbox in bikes:
                bx1,by1,bx2,by2, bconf, _ = bbox
                if iou_box((px1,py1,px2,py2),(bx1,by1,bx2,by2)) > 0.01:
                    is_rider = True
                    break
            if is_rider:
                riders.append(pbox)
        if args.treat_all_persons_as_riders and not riders:
            riders = persons.copy()

        detections_for_tracker = []
        for p in riders:
            x1,y1,x2,y2,conf,cls = p
            detections_for_tracker.append(([int(x1), int(y1), int(x2-x1), int(y2-y1)], float(conf), "person"))

        tracks = tracker.update(detections_for_tracker, frame=frame)

        # quick helmet lookup list
        helmet_list = helmet_boxes  # (x1,y1,x2,y2,conf,cls_id)

        annotated = frame.copy()
        for track in tracks:
            if not track.is_confirmed():
                continue
            track_id = track.track_id
            l,t,r,b = track.to_ltrb()
            l,t,r,b = int(l), int(t), int(r), int(b)

            # safe track confidence handling
            raw_conf = getattr(track, "det_conf", None)
            track_conf = safe_float(raw_conf, default=last_conf_by_track.get(track_id, 0.0))
            if raw_conf is not None:
                last_conf_by_track[track_id] = track_conf

            head_h_frac = args.head_fraction
            hx1, hy1, hx2, hy2 = l, t, r, int(t + (b - t) * head_h_frac)

            # detect helmet overlap
            helmet_present = False
            best_h_conf = 0.0
            for hb in helmet_list:
                hx1b, hy1b, hx2b, hy2b, hconf, _ = hb
                ov = iou_box((hx1,hy1,hx2,hy2),(hx1b,hy1b,hx2b,hy2b))
                hc = ( (hx1 <= (hx1b+hx2b)/2 <= hx2) and (hy1 <= (hy1b+hy2b)/2 <= hy2) )
                if ov >= args.helmet_iou_threshold or hc:
                    helmet_present = True
                    if hconf > best_h_conf:
                        best_h_conf = hconf

            # annotate
            color = (0,255,0) if helmet_present else (0,0,255)
            cv2.rectangle(annotated, (l,t), (r,b), color, 2)
            cv2.rectangle(annotated, (hx1,hy1), (hx2,hy2), (255,200,0), 1)
            cv2.putText(annotated, f"ID{track_id} {'Helmet' if helmet_present else 'NO_HELMET'}", (l, max(t-6,10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # logging
            if not helmet_present:
                last = track_last_logged_frame[track_id]
                if (frame_idx - last) >= args.log_repeat_frames:
                    row = {
                        "video_filename": input_path.name,
                        "frame_id": frame_idx,
                        "frame_timestamp_ms": frame_time_ms,
                        "wall_clock_iso": wall_time_iso,
                        "track_id": track_id,
                        "class": "no-helmet",
                        "confidence": float(track_conf),
                        "xmin": l, "ymin": t, "xmax": r, "ymax": b
                    }
                    rows.append(row)
                    track_last_logged_frame[track_id] = frame_idx

        writer.write(annotated)

    # cleanup
    cap.release()
    writer.release()
    save_csv(rows, args.csv)
    print("Saved annotated video:", args.output)
    print("Saved CSV:", args.csv)

if __name__ == "__main__":
    main()
