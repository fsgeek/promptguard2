"""
Processing Failures Collection Schema
Constitutional Principle VI: Data Provenance - Error tracking with raw data

Captures processing failures with complete context for debugging.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from arango.database import StandardDatabase


class ProcessingFailure(BaseModel):
    """
    Processing failure document schema.

    Captures failures with full context for debugging (Constitutional Principle VI).
    """
    attack_id: str = Field(..., description="Attack identifier")
    experiment_id: str = Field(..., description="Experiment identifier")
    stage: str = Field(..., description="Pipeline stage where error occurred")
    error_type: str = Field(..., description="Error type/class")
    error_message: str = Field(..., description="Error message")
    stack_trace: Optional[str] = Field(None, description="Stack trace")
    raw_data: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Raw data that caused error (for debugging)"
    )
    timestamp: str = Field(..., description="Error timestamp (ISO 8601)")
    model: Optional[str] = Field(None, description="Model identifier if applicable")
    recoverable: bool = Field(default=False, description="Whether error is recoverable")

    class Config:
        populate_by_name = True


def create_processing_failures_collection(db: StandardDatabase) -> None:
    """
    Create processing_failures collection with indexes.

    Args:
        db: ArangoDB database instance
    """
    collection_name = "processing_failures"

    if not db.has_collection(collection_name):
        collection = db.create_collection(collection_name)

        # Create indexes
        collection.add_hash_index(fields=["experiment_id"], unique=False)
        collection.add_hash_index(fields=["attack_id"], unique=False)
        collection.add_hash_index(fields=["stage"], unique=False)
        collection.add_hash_index(fields=["error_type"], unique=False)
        collection.add_hash_index(fields=["recoverable"], unique=False)

        print(f"Created collection: {collection_name} with indexes")
    else:
        print(f"Collection {collection_name} already exists")


def log_failure(
    db: StandardDatabase,
    attack_id: str,
    experiment_id: str,
    stage: str,
    error: Exception,
    raw_data: Optional[Dict[str, Any]] = None,
    model: Optional[str] = None,
    recoverable: bool = False,
) -> None:
    """
    Log processing failure to database.

    Args:
        db: ArangoDB database instance
        attack_id: Attack identifier
        experiment_id: Experiment identifier
        stage: Pipeline stage
        error: Exception object
        raw_data: Raw data that caused error
        model: Model identifier
        recoverable: Whether error is recoverable
    """
    from datetime import datetime, timezone
    import traceback

    failure_doc = {
        "attack_id": attack_id,
        "experiment_id": experiment_id,
        "stage": stage,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "stack_trace": traceback.format_exc(),
        "raw_data": raw_data or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "recoverable": recoverable,
    }

    db.collection("processing_failures").insert(failure_doc)


def get_failures_by_experiment(
    db: StandardDatabase,
    experiment_id: str,
    recoverable_only: bool = False
) -> List[ProcessingFailure]:
    """
    Get all failures for an experiment.

    Args:
        db: ArangoDB database instance
        experiment_id: Experiment identifier
        recoverable_only: Only return recoverable failures

    Returns:
        List of ProcessingFailure objects
    """
    aql = """
    FOR failure IN processing_failures
        FILTER failure.experiment_id == @experiment_id
        FILTER @recoverable_only == false OR failure.recoverable == true
        SORT failure.timestamp DESC
        RETURN failure
    """

    cursor = db.aql.execute(
        aql,
        bind_vars={
            "experiment_id": experiment_id,
            "recoverable_only": recoverable_only
        }
    )

    return [ProcessingFailure(**doc) for doc in cursor]
