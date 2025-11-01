"""
Checkpoint Manager with Atomic Rename
Constitutional Principle VI: Data Provenance
NFR5: Observability & Recovery

Manages experiment checkpoints for crash recovery and progress tracking.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional


class CheckpointManager:
    """
    Manages experiment checkpoints with atomic file operations.

    Checkpoint schema (per spec.md NFR5):
    {
        "completed_attacks": ["attack_001", "attack_002", ...],
        "failed_attempts": {"attack_003": 2, "attack_004": 1},
        "started": "2025-10-31T12:00:00Z",
        "last_updated": "2025-10-31T12:30:00Z"
    }

    Usage:
        manager = CheckpointManager(experiment_id="exp_phase1_step1_baseline_v1")
        manager.create()  # Initialize checkpoint

        # Mark attack as completed
        manager.mark_completed("attack_001")

        # Mark attack as failed (with retry count)
        manager.mark_failed("attack_002", retry_count=1)

        # Load checkpoint on resume
        checkpoint = manager.load()
        completed = checkpoint["completed_attacks"]
    """

    def __init__(self, experiment_id: str, data_dir: Optional[Path] = None):
        """
        Initialize checkpoint manager.

        Args:
            experiment_id: Experiment identifier
            data_dir: Base data directory (defaults to data/experiments/)
        """
        self.experiment_id = experiment_id

        if data_dir is None:
            project_root = Path(__file__).parent.parent.parent
            data_dir = project_root / "data" / "experiments"

        self.checkpoint_dir = data_dir / experiment_id
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        self.checkpoint_file = self.checkpoint_dir / "checkpoint.json"
        self.temp_file = self.checkpoint_dir / "checkpoint.json.tmp"

    def create(self) -> None:
        """
        Create new checkpoint file.

        Raises:
            FileExistsError: If checkpoint already exists (use load() instead)
        """
        if self.checkpoint_file.exists():
            raise FileExistsError(
                f"Checkpoint already exists for {self.experiment_id}. "
                "Use load() to resume or delete checkpoint to start fresh."
            )

        checkpoint = {
            "completed_attacks": [],
            "failed_attempts": {},
            "started": datetime.now(timezone.utc).isoformat(),
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

        self._write_atomic(checkpoint)

    def load(self) -> Dict[str, Any]:
        """
        Load checkpoint from file.

        Returns:
            Checkpoint data

        Raises:
            FileNotFoundError: If checkpoint doesn't exist
        """
        if not self.checkpoint_file.exists():
            raise FileNotFoundError(
                f"No checkpoint found for {self.experiment_id}. "
                "Run create() first."
            )

        with open(self.checkpoint_file, 'r') as f:
            return json.load(f)

    def mark_completed(self, attack_id: str) -> None:
        """
        Mark attack as completed.

        Args:
            attack_id: Attack identifier

        Raises:
            FileNotFoundError: If checkpoint doesn't exist
        """
        checkpoint = self.load()

        if attack_id not in checkpoint["completed_attacks"]:
            checkpoint["completed_attacks"].append(attack_id)

        # Remove from failed attempts if present
        if attack_id in checkpoint["failed_attempts"]:
            del checkpoint["failed_attempts"][attack_id]

        checkpoint["last_updated"] = datetime.now(timezone.utc).isoformat()
        self._write_atomic(checkpoint)

    def mark_failed(self, attack_id: str, retry_count: int = 1) -> None:
        """
        Mark attack as failed with retry count.

        Args:
            attack_id: Attack identifier
            retry_count: Number of failed attempts

        Raises:
            FileNotFoundError: If checkpoint doesn't exist
        """
        checkpoint = self.load()

        checkpoint["failed_attempts"][attack_id] = retry_count
        checkpoint["last_updated"] = datetime.now(timezone.utc).isoformat()

        self._write_atomic(checkpoint)

    def is_completed(self, attack_id: str) -> bool:
        """
        Check if attack is already completed.

        Args:
            attack_id: Attack identifier

        Returns:
            True if attack is in completed_attacks list
        """
        try:
            checkpoint = self.load()
            return attack_id in checkpoint["completed_attacks"]
        except FileNotFoundError:
            return False

    def get_failed_attacks(self, max_retries: int = 3) -> List[str]:
        """
        Get attacks that failed but haven't exceeded max retries.

        Args:
            max_retries: Maximum retry attempts

        Returns:
            List of attack IDs eligible for retry
        """
        try:
            checkpoint = self.load()
            return [
                attack_id
                for attack_id, count in checkpoint["failed_attempts"].items()
                if count < max_retries
            ]
        except FileNotFoundError:
            return []

    def get_stats(self) -> Dict[str, Any]:
        """
        Get checkpoint statistics.

        Returns:
            Dict with completed_count, failed_count, started, last_updated
        """
        try:
            checkpoint = self.load()
            return {
                "completed_count": len(checkpoint["completed_attacks"]),
                "failed_count": len(checkpoint["failed_attempts"]),
                "started": checkpoint["started"],
                "last_updated": checkpoint["last_updated"],
            }
        except FileNotFoundError:
            return {
                "completed_count": 0,
                "failed_count": 0,
                "started": None,
                "last_updated": None,
            }

    def _write_atomic(self, checkpoint: Dict[str, Any]) -> None:
        """
        Write checkpoint with atomic rename.

        Constitutional requirement: Prevents corruption on crashes.

        1. Write to .tmp file
        2. Atomic rename to .json (overwrites if exists)
        """
        try:
            # Write to temp file
            with open(self.temp_file, 'w') as f:
                json.dump(checkpoint, f, indent=2)

            # Atomic rename
            self.temp_file.replace(self.checkpoint_file)

        except (IOError, OSError) as e:
            raise IOError(
                f"Failed to write checkpoint for {self.experiment_id}: {e}"
            )

    def delete(self) -> None:
        """Delete checkpoint file (use with caution)."""
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()
        if self.temp_file.exists():
            self.temp_file.unlink()
