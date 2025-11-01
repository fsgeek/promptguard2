"""
Raw API Response Logger
Constitutional Principle VI: Data Provenance
NFR1: Raw API responses logged before any parsing

CRITICAL: Raw logging MUST occur before any parsing or processing.
Failure to log raw data is a data-spoiling error that MUST halt collection.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional


class RawLogger:
    """
    Logs raw API responses to JSONL format with atomic writes.

    Constitutional requirements:
    - Log raw response BEFORE any parsing
    - Atomic writes (prevents corruption)
    - One line per response (JSONL format)
    - Preserve complete response object

    Usage:
        logger = RawLogger(experiment_id="exp_phase1_step1_baseline_v1")
        logger.log_response(
            attack_id="attack_001",
            model="anthropic/claude-sonnet-4.5",
            raw_response={"id": "...", "choices": [...], ...},
            metadata={"step": "step1", "evaluation_type": "baseline"}
        )
    """

    def __init__(self, experiment_id: str, data_dir: Optional[Path] = None):
        """
        Initialize raw logger.

        Args:
            experiment_id: Experiment identifier (e.g., "exp_phase1_step1_baseline_v1")
            data_dir: Base data directory (defaults to data/experiments/)
        """
        self.experiment_id = experiment_id

        if data_dir is None:
            # Default to data/experiments/ in project root
            project_root = Path(__file__).parent.parent.parent
            data_dir = project_root / "data" / "experiments"

        # Create experiment-specific directory
        self.experiment_dir = data_dir / experiment_id
        self.experiment_dir.mkdir(parents=True, exist_ok=True)

        # Raw responses log file (JSONL)
        self.log_file = self.experiment_dir / "raw_responses.jsonl"

    def log_response(
        self,
        attack_id: str,
        model: str,
        raw_response: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Log raw API response to JSONL file.

        CRITICAL: This MUST be called BEFORE any parsing of the response.
        If logging fails, the calling code MUST raise an error and halt collection.

        Args:
            attack_id: Attack identifier
            model: Model identifier (e.g., "anthropic/claude-sonnet-4.5")
            raw_response: Complete raw API response object
            metadata: Additional metadata (step, evaluation_type, etc.)

        Raises:
            IOError: If atomic write fails (data-spoiling error)
        """
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "experiment_id": self.experiment_id,
            "attack_id": attack_id,
            "model": model,
            "raw_response": raw_response,
            "metadata": metadata or {},
        }

        try:
            # Atomic write: Write to temp file, then rename
            # (Constitutional Principle VI: Fail-fast if raw logging fails)
            temp_file = self.log_file.with_suffix(".jsonl.tmp")

            # Append to temp file
            with open(temp_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')

            # Atomic rename (overwrites if exists)
            temp_file.replace(self.log_file)

        except (IOError, OSError) as e:
            # CRITICAL FAILURE: Raw logging failed
            # This is a data-spoiling error - MUST halt collection
            raise IOError(
                f"CRITICAL: Raw response logging failed for attack {attack_id}, model {model}. "
                f"Cannot proceed without raw data provenance. Error: {e}"
            )

    def read_responses(self) -> list[Dict[str, Any]]:
        """
        Read all logged responses.

        Returns:
            List of log entries

        Raises:
            FileNotFoundError: If log file doesn't exist
        """
        if not self.log_file.exists():
            raise FileNotFoundError(
                f"Raw response log not found: {self.log_file}. "
                "No responses have been logged yet."
            )

        responses = []
        with open(self.log_file, 'r') as f:
            for line in f:
                if line.strip():
                    responses.append(json.loads(line))

        return responses

    def count_responses(self) -> int:
        """Count number of logged responses."""
        if not self.log_file.exists():
            return 0

        count = 0
        with open(self.log_file, 'r') as f:
            for line in f:
                if line.strip():
                    count += 1
        return count


def get_logger(experiment_id: str) -> RawLogger:
    """
    Get raw logger for experiment.

    Usage:
        from src.logging.raw_logger import get_logger

        logger = get_logger("exp_phase1_step1_baseline_v1")
        logger.log_response(...)
    """
    return RawLogger(experiment_id=experiment_id)
