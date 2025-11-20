"""Unit tests for TrustEMADetector."""

import pytest
from datetime import datetime

from src.evaluation.temporal.trust_ema import TrustEMADetector
from src.database.schemas.phase3_evaluation import (
    PrincipleEvaluation,
    NeutrosophicScore,
    EvaluationPrinciple,
)


def create_trajectory(f_scores: list[float], attack_id: str = "test_001") -> list[PrincipleEvaluation]:
    """Create synthetic trajectory with given F scores."""
    trajectory = []

    for turn_num, f_score in enumerate(f_scores, start=1):
        # Keep T non-negative: T = max(0, 1.0 - F - I)
        t_score = max(0.0, 1.0 - f_score - 0.1)

        eval_doc = PrincipleEvaluation(
            attack_id=attack_id,
            principle=EvaluationPrinciple.RECIPROCITY,
            turn_number=turn_num,
            evaluator_model="test/model",
            observer_prompt_version="v2.1-c",
            timestamp=datetime.now(),
            scores=NeutrosophicScore(T=t_score, I=0.1, F=f_score),
            reasoning=f"Turn {turn_num}",
            raw_response="{}",
            experiment_id="test",
        )
        trajectory.append(eval_doc)

    return trajectory


def test_gradual_drift_detection():
    """Test detection of gradual drift pattern.

    F=[0.1, 0.2, 0.5, 0.8] triggers at turn 3 due to rapid drift (0.2->0.5 = 0.3 > 0.15)
    """
    detector = TrustEMADetector(alpha=0.3, threshold=0.7, slope_threshold=0.15)

    # Create trajectory with gradual drift
    trajectory = create_trajectory(f_scores=[0.1, 0.2, 0.5, 0.8])

    result = detector.detect(trajectory, "reciprocity")

    assert result.attack_detected, "Should detect gradual drift"
    assert result.trigger_turn in [3, 4], "Should trigger at turn 3 (rapid drift) or 4 (EMA)"
    assert result.confidence > 0.0
    assert "threshold" in result.reasoning.lower() or "drift" in result.reasoning.lower()
    assert result.pattern_name == "gradual_drift"


def test_no_attack_benign_trajectory():
    """Test that benign trajectory does not trigger detection."""
    detector = TrustEMADetector(alpha=0.3, threshold=0.7, slope_threshold=0.15)

    # Benign trajectory with low F scores
    trajectory = create_trajectory(f_scores=[0.1, 0.15, 0.12, 0.18, 0.14])

    result = detector.detect(trajectory, "reciprocity")

    assert not result.attack_detected, "Should not detect attack in benign trajectory"
    assert result.trigger_turn is None
    assert result.pattern_name == "none"


def test_rapid_drift_detection():
    """Test detection via rapid slope (sudden jump in F)."""
    detector = TrustEMADetector(alpha=0.3, threshold=0.7, slope_threshold=0.15)

    # Sudden jump at turn 3: F goes from 0.2 to 0.5 (�F=0.3 > 0.15)
    trajectory = create_trajectory(f_scores=[0.1, 0.2, 0.5, 0.6])

    result = detector.detect(trajectory, "reciprocity")

    assert result.attack_detected, "Should detect rapid drift"
    assert result.trigger_turn == 3, "Should trigger at turn 3 where slope exceeded threshold"


def test_threshold_crossing_detection():
    """Test detection via EMA threshold crossing."""
    detector = TrustEMADetector(alpha=0.3, threshold=0.7, slope_threshold=0.15)

    # EMA gradually climbs above 0.7 - use higher values to ensure EMA reaches threshold
    trajectory = create_trajectory(f_scores=[0.65, 0.70, 0.75, 0.80, 0.85])

    result = detector.detect(trajectory, "reciprocity")

    assert result.attack_detected, "Should detect via EMA threshold"
    assert "EMA threshold crossed" in result.reasoning or "Rapid drift" in result.reasoning


def test_empty_trajectory_raises_error():
    """Test that empty trajectory raises ValueError."""
    detector = TrustEMADetector()

    with pytest.raises(ValueError, match="Cannot detect on empty trajectory"):
        detector.detect([], "reciprocity")


def test_unsorted_trajectory_raises_error():
    """Test that unsorted trajectory raises ValueError."""
    detector = TrustEMADetector()

    # Create trajectory with turn numbers out of order
    trajectory = create_trajectory(f_scores=[0.1, 0.2, 0.3])
    trajectory[0], trajectory[2] = trajectory[2], trajectory[0]  # Swap turn 1 and 3

    with pytest.raises(ValueError, match="must be sorted by turn_number"):
        detector.detect(trajectory, "reciprocity")


def test_custom_parameters():
    """Test detector with custom threshold parameters."""
    # Very sensitive detector (low thresholds)
    detector = TrustEMADetector(alpha=0.5, threshold=0.3, slope_threshold=0.05)

    trajectory = create_trajectory(f_scores=[0.1, 0.2, 0.35])

    result = detector.detect(trajectory, "reciprocity")

    assert result.attack_detected, "Should detect with lower thresholds"


def test_invalid_parameters():
    """Test that invalid parameters raise ValueError."""
    with pytest.raises(ValueError, match="alpha must be in"):
        TrustEMADetector(alpha=1.5)

    with pytest.raises(ValueError, match="threshold must be in"):
        TrustEMADetector(threshold=-0.1)

    with pytest.raises(ValueError, match="slope_threshold must be in"):
        TrustEMADetector(slope_threshold=2.0)
