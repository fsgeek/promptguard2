"""
Experiment Metadata Logger
Constitutional Principle VI: Data Provenance
NFR1: Experiment tagging on every document

Logs experiment metadata to ArangoDB for tracking and analysis.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
from arango.database import StandardDatabase
from arango.exceptions import DocumentInsertError


class ExperimentLogger:
    """
    Logs experiment metadata to ArangoDB experiments collection.

    Tracks experiment lifecycle: started → in_progress → completed/failed

    Usage:
        logger = ExperimentLogger(db)
        logger.start_experiment(
            experiment_id="exp_phase1_step1_baseline_v1",
            phase="phase1",
            step="step1",
            description="Baseline RLHF behavior",
            parameters={"target_models": [...], ...}
        )
        logger.complete_experiment("exp_phase1_step1_baseline_v1")
    """

    def __init__(self, db: StandardDatabase):
        """
        Initialize experiment logger.

        Args:
            db: ArangoDB database instance
        """
        self.db = db
        self.collection_name = "experiments"

        # Ensure collection exists
        if not self.db.has_collection(self.collection_name):
            self.db.create_collection(self.collection_name)

    def start_experiment(
        self,
        experiment_id: str,
        phase: str,
        step: str,
        description: str,
        parameters: Dict[str, Any],
    ) -> None:
        """
        Log experiment start.

        Args:
            experiment_id: Unique experiment identifier
            phase: Phase identifier (e.g., "phase1")
            step: Step identifier (e.g., "step1")
            description: Human-readable description
            parameters: Experiment parameters (models, temperature, etc.)

        Raises:
            DocumentInsertError: If experiment_id already exists
        """
        experiment_doc = {
            "_key": experiment_id,
            "experiment_id": experiment_id,
            "phase": phase,
            "step": step,
            "description": description,
            "parameters": parameters,
            "started": datetime.now(timezone.utc).isoformat(),
            "completed": None,
            "status": "in_progress",
        }

        try:
            self.db.collection(self.collection_name).insert(experiment_doc)
        except DocumentInsertError as e:
            raise DocumentInsertError(
                f"Experiment {experiment_id} already exists. "
                "Cannot start duplicate experiment. Use unique experiment_id."
            )

    def complete_experiment(
        self,
        experiment_id: str,
        status: str = "completed"
    ) -> None:
        """
        Mark experiment as completed.

        Args:
            experiment_id: Experiment identifier
            status: Final status ("completed" or "failed")
        """
        self.db.collection(self.collection_name).update({
            "_key": experiment_id,
            "completed": datetime.now(timezone.utc).isoformat(),
            "status": status,
        })

    def get_experiment(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get experiment metadata.

        Args:
            experiment_id: Experiment identifier

        Returns:
            Experiment document or None if not found
        """
        try:
            return self.db.collection(self.collection_name).get(experiment_id)
        except Exception:
            return None

    def update_progress(
        self,
        experiment_id: str,
        progress_data: Dict[str, Any]
    ) -> None:
        """
        Update experiment progress metadata.

        Args:
            experiment_id: Experiment identifier
            progress_data: Progress information (e.g., {"completed_count": 100, "total": 3810})
        """
        self.db.collection(self.collection_name).update({
            "_key": experiment_id,
            "progress": progress_data,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        })
