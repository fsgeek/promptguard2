"""Trust EMA (Exponential Moving Average) detector for gradual drift attacks.

Implements detection via exponential moving average of F (falsity) scores
across conversation turns. Based on TLA+ spec in specs/003-session-temporal-tracking/tla/TrustEMA.tla

Algorithm:
1. Calculate EMA of F scores: ema[i] = alpha * F[i] + (1 - alpha) * ema[i-1]
2. Calculate slope: slope[i] = F[i] - F[i-1]
3. Detect if: ema >= threshold OR slope > slope_threshold

References:
- TLA+ spec: specs/003-session-temporal-tracking/tla/TrustEMA.tla
- Config: specs/003-session-temporal-tracking/config/TrustEMA.cfg
"""

from typing import List

from src.evaluation.temporal.detector import TemporalDetector, DetectionResult
from src.database.schemas.phase3_evaluation import PrincipleEvaluation


class TrustEMADetector(TemporalDetector):
    """Detect gradual drift attacks via exponential moving average.

    Parameters (from TLA+ spec):
        alpha: EMA smoothing factor (0.0-1.0)
            - Higher alpha = more weight on recent values
            - Lower alpha = more smoothing
            - Default: 0.3 (from TrustEMA.cfg)

        threshold: EMA threshold for detection (0.0-1.0)
            - Detect if EMA >= threshold
            - Default: 0.7 (high falsity indicates attack)

        slope_threshold: Minimum F slope for rapid drift detection
            - Detect if F[i] - F[i-1] > slope_threshold
            - Default: 0.15 (15% jump in falsity)

    Example:
        detector = TrustEMADetector(alpha=0.3, threshold=0.7)
        result = detector.detect(trajectory, "reciprocity")
        if result.attack_detected:
            print(f"Drift detected at turn {result.trigger_turn}")
    """

    def __init__(
        self,
        alpha: float = 0.3,
        threshold: float = 0.7,
        slope_threshold: float = 0.15,
    ):
        """Initialize Trust EMA detector.

        Args:
            alpha: EMA smoothing factor (0.0-1.0)
            threshold: Detection threshold for EMA
            slope_threshold: Detection threshold for rapid slope

        Raises:
            ValueError: If parameters out of valid range
        """
        if not 0.0 <= alpha <= 1.0:
            raise ValueError(f"alpha must be in [0.0, 1.0], got {alpha}")
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"threshold must be in [0.0, 1.0], got {threshold}")
        if not 0.0 <= slope_threshold <= 1.0:
            raise ValueError(f"slope_threshold must be in [0.0, 1.0], got {slope_threshold}")

        self.alpha = alpha
        self.threshold = threshold
        self.slope_threshold = slope_threshold

    @property
    def name(self) -> str:
        """Human-readable detector name."""
        return "Trust EMA Detector"

    def detect(
        self,
        trajectories: List[PrincipleEvaluation],
        principle: str,
    ) -> DetectionResult:
        """Detect gradual drift via EMA of F scores.

        Args:
            trajectories: Ordered evaluations (sorted by turn_number)
            principle: Principle being evaluated

        Returns:
            DetectionResult with detection decision

        Raises:
            ValueError: If trajectory validation fails
        """
        # Validate trajectory
        self._validate_trajectory(trajectories)

        # Extract F scores
        f_scores = [t.scores.F for t in trajectories]

        # Calculate EMA
        ema = self._calculate_ema(f_scores)

        # Calculate slopes (first-order derivative)
        slopes = self._calculate_slopes(f_scores)

        # Detect threshold crossing or rapid drift
        attack_detected = False
        trigger_turn = None
        confidence = 0.0
        reasoning_parts = []

        # Check EMA threshold
        for i, ema_val in enumerate(ema):
            turn_num = i + 1
            if ema_val >= self.threshold:
                attack_detected = True
                trigger_turn = turn_num
                confidence = min(ema_val, 1.0)
                reasoning_parts.append(
                    f"EMA threshold crossed at turn {turn_num} (EMA={ema_val:.3f} >= {self.threshold})"
                )
                break

        # Check rapid drift (slope)
        if not attack_detected:
            for i, slope in enumerate(slopes):
                turn_num = i + 2  # Slopes start at turn 2 (comparing turn 2 vs turn 1)
                if slope > self.slope_threshold:
                    attack_detected = True
                    trigger_turn = turn_num
                    confidence = min(slope / self.slope_threshold, 1.0)
                    reasoning_parts.append(
                        f"Rapid drift detected at turn {turn_num} (DeltaF={slope:.3f} > {self.slope_threshold})"
                    )
                    break

        # Build reasoning
        if attack_detected:
            reasoning = "; ".join(reasoning_parts)
            reasoning += f" | F trajectory: {[round(f, 3) for f in f_scores]}"
        else:
            max_ema = max(ema) if ema else 0.0
            max_slope = max(slopes) if slopes else 0.0
            reasoning = (
                f"No attack detected. Max EMA={max_ema:.3f} < {self.threshold}, "
                f"Max slope={max_slope:.3f} < {self.slope_threshold}. "
                f"F trajectory: {[round(f, 3) for f in f_scores]}"
            )

        return DetectionResult(
            attack_detected=attack_detected,
            confidence=confidence,
            trigger_turn=trigger_turn,
            reasoning=reasoning,
            pattern_name="gradual_drift" if attack_detected else "none",
        )

    def _calculate_ema(self, values: List[float]) -> List[float]:
        """Calculate exponential moving average.

        Args:
            values: Time series values

        Returns:
            List of EMA values (same length as input)
        """
        if not values:
            return []

        ema = [values[0]]  # Initialize with first value

        for i in range(1, len(values)):
            ema_val = self.alpha * values[i] + (1 - self.alpha) * ema[i - 1]
            ema.append(ema_val)

        return ema

    def _calculate_slopes(self, values: List[float]) -> List[float]:
        """Calculate first-order derivative (slopes between consecutive values).

        Args:
            values: Time series values

        Returns:
            List of slopes (length = len(values) - 1)
        """
        if len(values) < 2:
            return []

        slopes = []
        for i in range(1, len(values)):
            slope = values[i] - values[i - 1]
            slopes.append(slope)

        return slopes
