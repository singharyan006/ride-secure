"""
RideSecure API Package
REST API endpoints for detection service integration
"""

from .detection_api import app

__version__ = "1.0.0"
__all__ = ['app']