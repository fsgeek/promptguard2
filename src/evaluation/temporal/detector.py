"""Abstract base class for temporal attack detectors.

Provides pluggable architecture (FR-011) for implementing different
temporal detection algorithms on T/I/F trajectories.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel, Field

from src.database.schemas.phase3_evaluation import PrincipleEvaluation


class DetectionResult(BaseModel):
    """Result of temporal attack detection.

    Attributes:
        attack_detected: Whether an attack was detected in the trajectory
        confidence: Confidence score (0.0-1.0) in the detection
        trigger_turn: Turn number where attack was detected (if applicable)
        reasoning: Human-readable explanation of detection logic
        pattern_name: Name of detected pattern (e.g., "gradual_drift", "threshold_crossing")
    """

    attack_detected: bool = Field(..., description="True if attack detected")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence (0.0-1.0)")
    trigger_turn: Optional[int] = Field(None, description="Turn where detection triggered")
    reasoning: str = Field(..., description="Explanation of detection decision")
    pattern_name: str = Field(..., description="Name of detected pattern")

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "attack_detected": True,
                "confidence": 0.85,
                "trigger_turn": 4,
                "reasoning": "F score exceeded threshold of 0.7 at turn 4 (F=0.75)",
                "pattern_name": "threshold_crossing",
            }
        }


class TemporalDetector(ABC):
    """Abstract base class for temporal attack detection algorithms.

    Pluggable Architecture (FR-011):
    Detectors analyze T/I/F score trajectories to identify attacks. Different
    algorithms can be implemented by subclassing and implementing detect().

    Design principles:
    - Stateless: Each detect() call is independent
    - Composable: Can evaluate multiple principles separately
    - Explainable: Must return reasoning for decisions

    Usage:
        detector = TrustEMADetector(alpha=0.3, threshold=0.7)
        trajectory = load_trajectory(attack_id, principle)
        result = detector.detect(trajectory, principle)
        if result.attack_detected:
            print(f"Attack detected at turn {result.trigger_turn}: {result.reasoning}")
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for this detector."""
        pass

    @abstractmethod
    def detect(
        self,
        trajectories: List[PrincipleEvaluation],
        principle: str,
    ) -> DetectionResult:
        """Detect attack in T/I/F score trajectory.

        Args:
            trajectories: Ordered list of evaluations (sorted by turn_number)
            principle: Principle being evaluated (for context)

        Returns:
            DetectionResult with detection decision and reasoning

        Raises:
            ValueError: If trajectories is empty or not sorted
        """
        pass

    def _validate_trajectory(self, trajectories: List[PrincipleEvaluation]) -> None:
        """Validate trajectory is non-empty and sorted.

        Args:
            trajectories: List of evaluations to validate

        Raises:
            ValueError: If validation fails
        """
        if not trajectories:
            raise ValueError("Cannot detect on empty trajectory")

        # Verify sorted by turn_number
        turn_numbers = [t.turn_number for t in trajectories]
        if turn_numbers != sorted(turn_numbers):
            raise ValueError(
                f"Trajectory must be sorted by turn_number, got: {turn_numbers}"
            )

        # Verify all same attack_id
        attack_ids = set(t.attack_id for t in trajectories)
        if len(attack_ids) > 1:
            raise ValueError(
                f"Trajectory must have consistent attack_id, got: {attack_ids}"
            )

        # Verify all same principle
        principles = set(t.principle.value for t in trajectories)
        if len(principles) > 1:
            raise ValueError(
                f"Trajectory must have consistent principle, got: {principles}"
            )
