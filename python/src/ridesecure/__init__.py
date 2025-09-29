"""
RideSecure Python Package
Complete ML foundation for helmet detection and violation management
"""

from .detection import HelmetDetector, PlateDetector, DetectionService

__version__ = "1.0.0"
__author__ = "RideSecure Team"
__description__ = "AI-powered helmet violation detection system"

__all__ = [
    'HelmetDetector',
    'PlateDetector', 
    'DetectionService'
]