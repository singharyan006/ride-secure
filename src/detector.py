from ultralytics import YOLO
from typing import List, Tuple
import numpy as np

class Detector:
    """
    Simple YOLO wrapper. Accepts a model path (pt) or model name passed as that path by registry.
    """
    def __init__(self, weights_path: str, conf_thresh: float = 0.4):
        self.weights_path = str(weights_path)
        self.conf_thresh = conf_thresh
        self.model = YOLO(self.weights_path)
        # map integer class -> name (if available)
        try:
            self.names = getattr(self.model, "model").names
        except Exception:
            # fallback to numeric names
            self.names = {}

    def predict(self, frame) -> List[Tuple[int,int,int,int,float,int]]:
        """
        Run detection and return list of (x1,y1,x2,y2,conf,cls_id)
        """
        res = self.model(frame)[0]
        boxes = []
        # res.boxes.data may be in different forms; handle robustly
        try:
            data = res.boxes.data.cpu().numpy()
        except Exception:
            try:
                data = res.boxes.cpu().numpy()
            except Exception:
                data = np.array([])
        for row in data:
            if len(row) < 6:
                continue
            x1, y1, x2, y2, conf, cls = row
            if conf < self.conf_thresh:
                continue
            boxes.append((int(x1), int(y1), int(x2), int(y2), float(conf), int(cls)))
        return boxes

    def class_name(self, cls_id: int) -> str:
        return self.names.get(cls_id, str(cls_id))
