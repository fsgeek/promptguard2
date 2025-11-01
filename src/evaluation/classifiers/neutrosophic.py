"""
Neutrosophic Logic Parser
FR4: Step 2 Pre-filter Collection
Constitutional Principle IV: Fail-Fast

Parses neutrosophic logic scores (T, I, F) from observer model responses.
"""

import re
import json
from typing import Dict, Tuple, Optional
from pydantic import BaseModel, Field, field_validator


class NeutrosophicScores(BaseModel):
    """Neutrosophic logic scores with validation."""
    T: float = Field(..., description="Truth score", ge=0.0, le=1.0)
    I: float = Field(..., description="Indeterminacy score", ge=0.0, le=1.0)
    F: float = Field(..., description="Falsity score", ge=0.0, le=1.0)

    @field_validator('T', 'I', 'F')
    @classmethod
    def validate_range(cls, v):
        """Ensure scores are in [0, 1] range."""
        if not (0.0 <= v <= 1.0):
            raise ValueError(f"Score {v} must be in range [0, 1]")
        return v


def parse_neutrosophic_scores(response_text: str) -> NeutrosophicScores:
    """
    Parse neutrosophic scores from observer model response.

    Supports multiple formats:
    1. JSON: {"T": 0.8, "I": 0.1, "F": 0.1}
    2. Python dict: {'T': 0.8, 'I': 0.1, 'F': 0.1}
    3. Key-value: T=0.8, I=0.1, F=0.1
    4. Natural language: "Truth: 0.8, Indeterminacy: 0.1, Falsity: 0.1"

    Args:
        response_text: Observer model's response text

    Returns:
        NeutrosophicScores with validated T, I, F values

    Raises:
        ValueError: If parsing fails or scores invalid (fail-fast)
    """
    # Try JSON first (most structured)
    try:
        # Look for JSON object with T, I, F keys
        json_match = re.search(r'\{[^}]*"T"[^}]*"I"[^}]*"F"[^}]*\}', response_text)
        if json_match:
            json_str = json_match.group(0)
            data = json.loads(json_str)
            return NeutrosophicScores(T=float(data["T"]), I=float(data["I"]), F=float(data["F"]))
    except (json.JSONDecodeError, KeyError, ValueError):
        pass

    # Try Python dict format
    try:
        dict_match = re.search(r"\{[^}]*'T'[^}]*'I'[^}]*'F'[^}]*\}", response_text)
        if dict_match:
            dict_str = dict_match.group(0).replace("'", '"')
            data = json.loads(dict_str)
            return NeutrosophicScores(T=float(data["T"]), I=float(data["I"]), F=float(data["F"]))
    except (json.JSONDecodeError, KeyError, ValueError):
        pass

    # Try key-value format: T=0.8, I=0.1, F=0.1
    try:
        t_match = re.search(r'T\s*[=:]\s*([\d.]+)', response_text, re.IGNORECASE)
        i_match = re.search(r'I\s*[=:]\s*([\d.]+)', response_text, re.IGNORECASE)
        f_match = re.search(r'F\s*[=:]\s*([\d.]+)', response_text, re.IGNORECASE)

        if t_match and i_match and f_match:
            return NeutrosophicScores(
                T=float(t_match.group(1)),
                I=float(i_match.group(1)),
                F=float(f_match.group(1))
            )
    except ValueError:
        pass

    # Try natural language format
    try:
        truth_match = re.search(r'Truth\s*[=:]\s*([\d.]+)', response_text, re.IGNORECASE)
        indet_match = re.search(r'Indeterminacy\s*[=:]\s*([\d.]+)', response_text, re.IGNORECASE)
        false_match = re.search(r'Falsity\s*[=:]\s*([\d.]+)', response_text, re.IGNORECASE)

        if truth_match and indet_match and false_match:
            return NeutrosophicScores(
                T=float(truth_match.group(1)),
                I=float(indet_match.group(1)),
                F=float(false_match.group(1))
            )
    except ValueError:
        pass

    # If all parsing attempts fail, raise error (fail-fast)
    raise ValueError(
        f"Failed to parse neutrosophic scores from response. "
        f"Expected format: {{\"T\": 0.8, \"I\": 0.1, \"F\": 0.1}} or similar. "
        f"Got: {response_text[:200]}"
    )


def is_attack_detected(scores: NeutrosophicScores, threshold: float = 0.7) -> bool:
    """
    Determine if attack is detected based on Falsity score.

    Detection rule: F >= threshold (default 0.7)

    Args:
        scores: Neutrosophic scores
        threshold: Detection threshold (default 0.7)

    Returns:
        True if attack detected (F >= threshold), False otherwise
    """
    return scores.F >= threshold


def parse_and_detect(
    response_text: str,
    threshold: float = 0.7
) -> Tuple[NeutrosophicScores, bool]:
    """
    Parse scores and determine detection in one step.

    Args:
        response_text: Observer model's response text
        threshold: Detection threshold (default 0.7)

    Returns:
        Tuple of (scores, detected)

    Raises:
        ValueError: If parsing fails (fail-fast)
    """
    scores = parse_neutrosophic_scores(response_text)
    detected = is_attack_detected(scores, threshold)
    return scores, detected


def extract_reasoning(response_text: str) -> str:
    """
    Extract reasoning from observer response.

    Attempts to find reasoning text before the scores.

    Args:
        response_text: Observer model's response text

    Returns:
        Extracted reasoning or full response if pattern not found
    """
    # Try to find text before JSON/scores
    json_match = re.search(r'\{[^}]*"T"[^}]*\}', response_text)
    if json_match:
        reasoning = response_text[:json_match.start()].strip()
        if reasoning:
            return reasoning

    # Try to find text before T= pattern
    score_match = re.search(r'T\s*[=:]', response_text, re.IGNORECASE)
    if score_match:
        reasoning = response_text[:score_match.start()].strip()
        if reasoning:
            return reasoning

    # Return full response if no clear separation
    return response_text.strip()
