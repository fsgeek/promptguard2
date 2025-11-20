"""Factory for creating temporal detectors by name.

Provides pluggable architecture for registering and creating detector instances.
"""

from typing import Dict, Type, List

from src.evaluation.temporal.detector import TemporalDetector


class TemporalDetectorFactory:
    """Registry for temporal detector implementations.

    Enables pluggable detector architecture (FR-011) by allowing
    detectors to be registered and instantiated by name.

    Usage:
        # Register a detector
        TemporalDetectorFactory.register("trust_ema", TrustEMADetector)

        # Create detector instance
        detector = TemporalDetectorFactory.create("trust_ema", alpha=0.3, threshold=0.7)

        # List available detectors
        detectors = TemporalDetectorFactory.list_detectors()
    """

    _registry: Dict[str, Type[TemporalDetector]] = {}

    @classmethod
    def register(cls, name: str, detector_class: Type[TemporalDetector]) -> None:
        """Register a detector class.

        Args:
            name: Unique name for this detector (e.g., "trust_ema")
            detector_class: Detector class (must subclass TemporalDetector)

        Raises:
            ValueError: If name already registered or class is not a TemporalDetector
        """
        if not issubclass(detector_class, TemporalDetector):
            raise ValueError(
                f"Detector class must subclass TemporalDetector, got {detector_class}"
            )

        if name in cls._registry:
            raise ValueError(
                f"Detector '{name}' is already registered as {cls._registry[name]}"
            )

        cls._registry[name] = detector_class

    @classmethod
    def create(cls, name: str, **kwargs) -> TemporalDetector:
        """Create detector instance by name.

        Args:
            name: Registered detector name
            **kwargs: Arguments passed to detector constructor

        Returns:
            Initialized detector instance

        Raises:
            ValueError: If detector name not found in registry
        """
        if name not in cls._registry:
            available = list(cls._registry.keys())
            raise ValueError(
                f"Detector '{name}' not found in registry. "
                f"Available detectors: {available}"
            )

        detector_class = cls._registry[name]
        return detector_class(**kwargs)

    @classmethod
    def list_detectors(cls) -> List[str]:
        """List all registered detector names.

        Returns:
            List of detector names
        """
        return list(cls._registry.keys())

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """Check if detector name is registered.

        Args:
            name: Detector name to check

        Returns:
            True if name is registered
        """
        return name in cls._registry


# Auto-register built-in detectors
from src.evaluation.temporal.trust_ema import TrustEMADetector

TemporalDetectorFactory.register("trust_ema", TrustEMADetector)
