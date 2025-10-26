"""
Client-side ML pattern recognition module for early flag detection.

Detects suspicious patterns locally before sending data to server.
Creates flagged data files for server-side re-analysis.
"""

from .pattern_detector import PatternDetector
from .ml_classifier import MLClassifier
from .flag_data_generator import FlagDataGenerator

__all__ = [
    "PatternDetector",
    "MLClassifier", 
    "FlagDataGenerator",
]
