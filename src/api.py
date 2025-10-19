from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import numpy as np
import cv2
import io


app = FastAPI(title="RideSecure Inference API")

# Allow all origins by default (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Lazy singletons for detectors to avoid heavy imports at module import time
_detectors = {}


def _load_detector(model_name: str, category: str = "detection"):
    """Lazily create and cache a Detector for model_name.

    Returns a Detector instance or raises HTTPException with guidance.
    """
    if model_name in _detectors:
        return _detectors[model_name]

    try:
        # local imports to avoid importing heavy libs at module import time
        from .model_registry import resolve_model_path, load_manifest
        from .detector import Detector
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Dependencies not available: {e}")

    # resolve path (this may raise FileNotFoundError)
    try:
        model_path = resolve_model_path(model_name, category=category)
    except FileNotFoundError as e:
        # list available models to help client
        try:
            manifest = load_manifest()
            available = list(manifest.get(category, {}).keys())
        except Exception:
            available = []
        raise HTTPException(status_code=404, detail={
            "error": str(e),
            "available_models": available,
        })

    try:
        detector = Detector(str(model_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize detector: {e}")

    _detectors[model_name] = detector
    return detector


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/models")
def models(category: str = "detection"):
    try:
        from .model_registry import load_manifest
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Model registry not available: {e}")
    manifest = load_manifest()
    return {"available": manifest.get(category, {})}


def _read_imagefile_to_cv2(data: bytes):
    arr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Failed to decode image")
    return img


@app.post("/predict/frame")
async def predict_frame(file: UploadFile = File(...), model: str = "custom_helmet", conf: float = 0.4):
    """Accept an image file and return detections from the specified model.

    Request: multipart/form-data with file and optional model/conf fields.
    Response: JSON list of boxes: [{x1,y1,x2,y2,conf,cls}]
    """
    content = await file.read()
    try:
        frame = _read_imagefile_to_cv2(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {e}")

    detector = _load_detector(model)

    try:
        boxes = detector.predict(frame)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {e}")

    # serialize numpy types to plain Python types
    results = []
    for (x1, y1, x2, y2, confv, cls) in boxes:
        results.append({
            "x1": int(x1),
            "y1": int(y1),
            "x2": int(x2),
            "y2": int(y2),
            "confidence": float(confv),
            "class_id": int(cls),
            "class_name": detector.class_name(int(cls)),
        })

    return {"filename": file.filename, "detections": results}


@app.post("/predict/violations")
async def predict_violations(
    file: UploadFile = File(...), 
    coco_model: str = "yolov8n",
    helmet_model: str = "custom_helmet",
    conf: float = 0.4,
    head_fraction: float = 0.35,
    helmet_iou: float = 0.1
):
    """Full two-stage helmet violation detection (like CLI).
    
    Process:
    1. Detect people and motorcycles (COCO model)
    2. Identify riders (person near motorcycle)
    3. Detect helmets (custom helmet model)
    4. Match helmets to rider heads
    5. Return violations (riders without helmets)
    
    Returns: {"violations": [...], "riders": [...], "helmets": [...]}
    """
    content = await file.read()
    try:
        frame = _read_imagefile_to_cv2(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {e}")
    
    # Load both detectors
    coco = _load_detector(coco_model)
    helmet = _load_detector(helmet_model)
    
    try:
        # Stage 1: Detect people and vehicles
        coco_boxes = coco.predict(frame)
        
        # Classify COCO detections
        persons = [b for b in coco_boxes if coco.class_name(b[5]).lower() == "person"]
        bikes = [b for b in coco_boxes if coco.class_name(b[5]).lower() in ("motorcycle", "bicycle", "motorbike", "bike")]
        
        # Stage 2: Identify riders (person near motorcycle)
        riders = []
        for pbox in persons:
            px1, py1, px2, py2, pconf, pcls = pbox
            is_rider = False
            for bbox in bikes:
                bx1, by1, bx2, by2, bconf, bcls = bbox
                # Calculate IoU
                inter_x1 = max(px1, bx1)
                inter_y1 = max(py1, by1)
                inter_x2 = min(px2, bx2)
                inter_y2 = min(py2, by2)
                
                if inter_x1 < inter_x2 and inter_y1 < inter_y2:
                    inter_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
                    box1_area = (px2 - px1) * (py2 - py1)
                    box2_area = (bx2 - bx1) * (by2 - by1)
                    union_area = box1_area + box2_area - inter_area
                    iou = inter_area / union_area if union_area > 0 else 0
                    
                    if iou > 0.01:  # Same threshold as CLI
                        is_rider = True
                        break
            
            if is_rider:
                riders.append({
                    "x1": int(px1), "y1": int(py1), 
                    "x2": int(px2), "y2": int(py2),
                    "confidence": float(pconf)
                })
        
        # Stage 3: Detect helmets
        helmet_boxes = helmet.predict(frame)
        helmet_list = []
        for (hx1, hy1, hx2, hy2, hconf, hcls) in helmet_boxes:
            helmet_list.append({
                "x1": int(hx1), "y1": int(hy1),
                "x2": int(hx2), "y2": int(hy2),
                "confidence": float(hconf),
                "class_id": int(hcls),
                "class_name": helmet.class_name(int(hcls))
            })
        
        # Stage 4: Check each rider for helmet
        violations = []
        for rider in riders:
            rx1, ry1, rx2, ry2 = rider["x1"], rider["y1"], rider["x2"], rider["y2"]
            
            # Calculate head region (top portion of person bbox)
            person_height = ry2 - ry1
            head_y1 = ry1
            head_y2 = ry1 + int(person_height * head_fraction)
            head_x1 = rx1
            head_x2 = rx2
            
            # Check if any helmet overlaps with head region
            has_helmet = False
            matched_helmet = None
            
            for helm in helmet_list:
                hx1, hy1, hx2, hy2 = helm["x1"], helm["y1"], helm["x2"], helm["y2"]
                
                # Calculate IoU between helmet and head region
                inter_x1 = max(head_x1, hx1)
                inter_y1 = max(head_y1, hy1)
                inter_x2 = min(head_x2, hx2)
                inter_y2 = min(head_y2, hy2)
                
                if inter_x1 < inter_x2 and inter_y1 < inter_y2:
                    inter_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
                    head_area = (head_x2 - head_x1) * (head_y2 - head_y1)
                    helmet_area = (hx2 - hx1) * (hy2 - hy1)
                    union_area = head_area + helmet_area - inter_area
                    iou = inter_area / union_area if union_area > 0 else 0
                    
                    if iou > helmet_iou:
                        has_helmet = True
                        matched_helmet = helm
                        break
            
            # If no helmet found on head -> VIOLATION
            if not has_helmet:
                violations.append({
                    "rider_bbox": rider,
                    "violation_type": "NO_HELMET",
                    "confidence": rider["confidence"],
                    "head_region": {
                        "x1": head_x1, "y1": head_y1,
                        "x2": head_x2, "y2": head_y2
                    }
                })
        
        return {
            "filename": file.filename,
            "violations": violations,
            "riders": riders,
            "helmets": helmet_list,
            "stats": {
                "total_persons": len(persons),
                "total_bikes": len(bikes),
                "total_riders": len(riders),
                "total_helmets": len(helmet_list),
                "total_violations": len(violations)
            }
        }
        
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Violation detection failed: {e}")


@app.post("/process-video")
async def process_video(
    file: UploadFile = File(...),
    coco_model: str = "yolov8n",
    helmet_model: str = "custom_helmet",
    conf: float = 0.4,
    save_to_db: bool = True,
    create_annotated_video: bool = True
):
    """
    Process ENTIRE video file and return all violations at once
    
    Uses the SAME detection logic as CLI for consistency
    
    If save_to_db=True, violations are saved directly to Supabase
    If create_annotated_video=True, generates annotated video with bounding boxes
    """
    import tempfile
    import os
    from .model_registry import resolve_model_path
    from .detector import Detector
    from .tracker import Tracker
    from .database import get_db_service
    from collections import defaultdict
    
    # Initialize database service if saving
    db = get_db_service() if save_to_db else None
    
    def iou_box(box1, box2):
        """Calculate IoU between two boxes"""
        x1a, y1a, x2a, y2a = box1
        x1b, y1b, x2b, y2b = box2
        
        inter_x1 = max(x1a, x1b)
        inter_y1 = max(y1a, y1b)
        inter_x2 = min(x2a, x2b)
        inter_y2 = min(y2a, y2b)
        
        if inter_x1 < inter_x2 and inter_y1 < inter_y2:
            inter_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
            area1 = (x2a - x1a) * (y2a - y1a)
            area2 = (x2b - x1b) * (y2b - y1b)
            union = area1 + area2 - inter_area
            return inter_area / union if union > 0 else 0
        return 0
    
    try:
        # Save uploaded video to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_video:
            content = await file.read()
            tmp_video.write(content)
            video_path = tmp_video.name
        
        print(f"📹 Processing video: {file.filename} ({len(content)/1024:.1f} KB)")
        
        # Load models with same conf threshold as CLI
        coco_path = resolve_model_path(coco_model, category="detection")
        helmet_path = resolve_model_path(helmet_model, category="detection")
        
        # Create NEW detector instances with conf_thresh (don't use cached ones!)
        from .detector import Detector
        coco = Detector(str(coco_path), conf_thresh=conf)
        helmet = Detector(str(helmet_path), conf_thresh=conf)
        
        # Initialize tracker like CLI does
        tracker = Tracker(max_age=30, n_init=1)
        
        # Open video with OpenCV
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise HTTPException(status_code=400, detail="Could not open video file")
        
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"   Video info: {total_frames} frames @ {fps} FPS, {width}x{height}")
        
        # Setup video writer if annotation requested
        writer = None
        annotated_video_path = None
        if create_annotated_video:
            from pathlib import Path
            from .video_io import video_writer
            output_dir = Path("outputs/annotated_videos").resolve()  # Use absolute path
            output_dir.mkdir(parents=True, exist_ok=True)
            annotated_video_path = output_dir / f"annotated_{file.filename}"
            writer = video_writer(str(annotated_video_path), fps, (width, height))
            print(f"   📹 Will save annotated video to: {annotated_video_path}")
        
        all_violations = []
        frame_idx = 0
        track_last_logged_frame = defaultdict(lambda: -9999)
        last_conf_by_track = defaultdict(lambda: 0.0)
        
        # Process every frame WITH TRACKING (like CLI does)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Run detections
            coco_boxes = coco.predict(frame)
            helmet_boxes = helmet.predict(frame)
            
            # Filter persons and bikes using class names
            persons = [b for b in coco_boxes if coco.class_name(b[5]).lower() == "person"]
            bikes = [b for b in coco_boxes if coco.class_name(b[5]).lower() in ("motorcycle", "bicycle", "motorbike", "bike")]
            
            # Identify riders (person near bike with IoU > 0.01)
            riders = []
            for pbox in persons:
                px1, py1, px2, py2, pconf, _ = pbox
                is_rider = False
                for bbox in bikes:
                    bx1, by1, bx2, by2, bconf, _ = bbox
                    if iou_box((px1, py1, px2, py2), (bx1, by1, bx2, by2)) > 0.01:
                        is_rider = True
                        break
                if is_rider:
                    riders.append(pbox)
            
            # Prepare detections for tracker
            detections_for_tracker = []
            for p in riders:
                x1, y1, x2, y2, conf, cls = p
                detections_for_tracker.append(([int(x1), int(y1), int(x2 - x1), int(y2 - y1)], float(conf), "person"))
            
            # Update tracker
            tracks = tracker.update(detections_for_tracker, frame=frame)
            
            # Store helmet status per track for this frame (for annotation)
            track_helmet_status = {}
            
            # Check each confirmed track for helmet
            for track in tracks:
                if not track.is_confirmed():
                    continue
                
                track_id = track.track_id
                l, t, r, b = track.to_ltrb()
                l, t, r, b = int(l), int(t), int(r), int(b)
                
                # Get track confidence
                raw_conf = getattr(track, "det_conf", None)
                track_conf = float(raw_conf) if raw_conf is not None else last_conf_by_track.get(track_id, 0.0)
                if raw_conf is not None:
                    last_conf_by_track[track_id] = track_conf
                
                # Head region (top 35% of person bbox)
                head_h_frac = 0.35
                hx1, hy1, hx2, hy2 = l, t, r, int(t + (b - t) * head_h_frac)
                
                # Check for helmet overlap with head region
                helmet_present = False
                helmet_iou_threshold = 0.1
                
                for hb in helmet_boxes:
                    hx1b, hy1b, hx2b, hy2b, hconf, hcls = hb
                    
                    # Check IoU with head region
                    ov = iou_box((hx1, hy1, hx2, hy2), (hx1b, hy1b, hx2b, hy2b))
                    
                    # OR check if helmet center is inside head region
                    hc = ((hx1 <= (hx1b + hx2b) / 2 <= hx2) and (hy1 <= (hy1b + hy2b) / 2 <= hy2))
                    
                    if ov >= helmet_iou_threshold or hc:
                        helmet_present = True
                        break
                
                # Store helmet status for annotation (checked on EVERY frame)
                track_helmet_status[track_id] = helmet_present
                
                # Log violation if no helmet AND haven't logged this track recently
                if not helmet_present:
                    # Only log once per track (or at least 30 frames apart)
                    if frame_idx - track_last_logged_frame[track_id] >= 30:
                        violation_data = {
                            "frame_number": frame_idx,
                            "track_id": int(track_id),
                            "rider_bbox": {
                                "x1": l, "y1": t, "x2": r, "y2": b,
                                "confidence": track_conf
                            },
                            "violation_type": "NO_HELMET",
                            "confidence": track_conf
                        }
                        
                        all_violations.append(violation_data)
                        track_last_logged_frame[track_id] = frame_idx
                        
                        # Save to database immediately if enabled
                        if db:
                            db.save_violation(
                                video_source=file.filename,
                                frame_number=frame_idx,
                                track_id=int(track_id),
                                bbox_x1=l,
                                bbox_y1=t,
                                bbox_x2=r,
                                bbox_y2=b,
                                confidence=track_conf,
                                raw_detection=violation_data
                            )
            
            # Draw annotations on frame if video writer is enabled
            if writer is not None:
                annotated = frame.copy()
                
                # Draw all tracked riders
                for track in tracks:
                    if not track.is_confirmed():
                        continue
                    
                    track_id = track.track_id
                    l, t, r, b = track.to_ltrb()
                    l, t, r, b = int(l), int(t), int(r), int(b)
                    
                    # Head region
                    hx1, hy1, hx2, hy2 = l, t, r, int(t + (b - t) * 0.35)
                    
                    # Use REAL-TIME helmet status for annotation (not logged violations)
                    helmet_present = track_helmet_status.get(track_id, True)  # Default to True if not found
                    
                    # Color: RED if NO helmet, GREEN if helmet present
                    color = (0, 0, 255) if not helmet_present else (0, 255, 0)
                    label = f"Track {track_id}: {'NO HELMET' if not helmet_present else 'OK'}"
                    
                    # Draw bounding box and head region
                    cv2.rectangle(annotated, (l, t), (r, b), color, 2)
                    cv2.rectangle(annotated, (hx1, hy1), (hx2, hy2), (255, 200, 0), 1)  # Head region in cyan
                    
                    cv2.putText(annotated, label, (l, max(t-6, 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                # Write annotated frame
                writer.write(annotated)
            
            frame_idx += 1
            
            # Progress indicator
            if frame_idx % 50 == 0:
                print(f"   Processed {frame_idx}/{total_frames} frames, found {len(all_violations)} violations so far")
        
        cap.release()
        
        # Close video writer if used
        if writer is not None:
            writer.release()
            print(f"✅ Saved annotated video: {annotated_video_path}")
        
        os.unlink(video_path)  # Delete temp file
        
        print(f"✅ Video processing complete: {len(all_violations)} violations found in {frame_idx} frames")
        
        saved_to_db = len(all_violations) if db else 0
        
        return {
            "filename": file.filename,
            "total_frames": frame_idx,
            "violations": all_violations,
            "annotated_video_path": str(annotated_video_path) if annotated_video_path else None,
            "stats": {
                "total_violations": len(all_violations),
                "fps": fps,
                "saved_to_db": saved_to_db,
                "annotated_video_created": create_annotated_video
            }
        }
        
    except Exception as e:
        # Cleanup temp file on error
        if 'video_path' in locals() and os.path.exists(video_path):
            os.unlink(video_path)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Video processing failed: {str(e)}")


@app.get("/violations/recent")
def get_recent_violations(limit: int = 100):
    """
    Get recent violations from database
    
    Java can poll this endpoint to display real-time violations
    """
    try:
        from .database import get_db_service
        db = get_db_service()
        violations = db.get_recent_violations(limit=limit)
        
        # Convert timestamps to strings for JSON serialization
        for v in violations:
            if 'timestamp' in v and v['timestamp']:
                v['timestamp'] = v['timestamp'].isoformat()
        
        return {
            "violations": violations,
            "count": len(violations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch violations: {str(e)}")


@app.get("/violations/by-video/{video_name}")
def get_violations_by_video(video_name: str):
    """
    Get all violations for a specific video
    
    Java can call this after processing to get violations for display
    """
    try:
        from .database import get_db_service
        db = get_db_service()
        violations = db.get_violations_by_video(video_name)
        
        # Convert timestamps to strings
        for v in violations:
            if 'timestamp' in v and v['timestamp']:
                v['timestamp'] = v['timestamp'].isoformat()
        
        return {
            "video_name": video_name,
            "violations": violations,
            "count": len(violations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch violations: {str(e)}")


