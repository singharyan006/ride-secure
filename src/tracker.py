from deep_sort_realtime.deepsort_tracker import DeepSort
from typing import List, Tuple

class Tracker:
    def __init__(self, max_age=30, n_init=1):
        self.ds = DeepSort(max_age=max_age, n_init=n_init, nms_max_overlap=1.0)

    def update(self, detections: List[Tuple[List[int], float, str]], frame=None):
        """
        detections: list of ([x,y,w,h], conf, class_name)
        returns list of track objects from deep_sort_realtime (with attributes track_id, to_ltrb, det_conf, is_confirmed)
        """
        tracks = self.ds.update_tracks(detections, frame=frame)
        return tracks
