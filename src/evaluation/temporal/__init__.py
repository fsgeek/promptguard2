"""Temporal detection components for multi-turn attack analysis.

This package provides a pluggable architecture for detecting attacks
via trajectory analysis across multi-turn conversations.

Key components:
- TemporalDetector: Abstract base class for detection algorithms
- TrustEMADetector: Exponential moving average detector
- DetectorFactory: Registry for creating detectors by name
"""

from src.evaluation.temporal.detector import TemporalDetector, DetectionResult
from src.evaluation.temporal.trust_ema import TrustEMADetector

__all__ = [
    "TemporalDetector",
    "DetectionResult",
    "TrustEMADetector",
]

# Lazy import of factory to avoid circular dependencies
def __getattr__(name):
    if name == "TemporalDetectorFactory":
        from src.evaluation.temporal.factory import TemporalDetectorFactory
        return TemporalDetectorFactory
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
