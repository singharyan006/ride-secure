"""
RideSecure Detection Package
Main package for helmet detection and license plate recognition
"""

from .helmet_detector import HelmetDetector
from .plate_detector import PlateDetector  
from .detection_service import DetectionService

__version__ = "1.0.0"
__author__ = "RideSecure Team"

__all__ = [
    'HelmetDetector',
    'PlateDetector', 
    'DetectionService'
]