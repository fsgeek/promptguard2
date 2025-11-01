"""
Experiments Collection Schema
Constitutional Principle VI: Data Provenance - Experiment tracking

Tracks experiment metadata and lifecycle.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from arango.database import StandardDatabase


class Experiment(BaseModel):
    """
    Experiment document schema.

    Tracks experiment execution from start to completion.
    """
    key: str = Field(..., alias="_key", description="Experiment ID (e.g., 'exp_phase1_step1_baseline_v1')")
    experiment_id: str = Field(..., description="Experiment identifier (same as _key)")
    phase: str = Field(..., description="Phase identifier (e.g., 'phase1')")
    step: str = Field(..., description="Step identifier (e.g., 'step1')")
    description: str = Field(..., description="Human-readable description")
    parameters: Dict[str, Any] = Field(..., description="Experiment parameters (models, temperature, etc.)")
    started: str = Field(..., description="Start timestamp (ISO 8601)")
    completed: Optional[str] = Field(None, description="Completion timestamp (ISO 8601)")
    status: str = Field(
        ...,
        description="Experiment status",
        pattern="^(in_progress|completed|failed)$"
    )
    progress: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Progress metadata")
    last_updated: Optional[str] = Field(None, description="Last update timestamp (ISO 8601)")

    class Config:
        populate_by_name = True


def create_experiments_collection(db: StandardDatabase) -> None:
    """
    Create experiments collection with indexes.

    Args:
        db: ArangoDB database instance
    """
    collection_name = "experiments"

    if not db.has_collection(collection_name):
        collection = db.create_collection(collection_name)

        # Create indexes
        collection.add_hash_index(fields=["status"], unique=False)
        collection.add_hash_index(fields=["phase"], unique=False)
        collection.add_hash_index(fields=["step"], unique=False)

        print(f"Created collection: {collection_name} with indexes")
    else:
        print(f"Collection {collection_name} already exists")
