"""
Step 2 Pre-Evaluations Collection Schema
FR4: Step 2 Pre-filter Collection
Constitutional Principle VI: Data Provenance

Stores Step 2 pre-evaluation results with observer framing.
"""

from typing import Dict, Optional
from pydantic import BaseModel, Field, field_validator
from arango.database import StandardDatabase


class NeutrosophicScores(BaseModel):
    """Neutrosophic logic scores (T, I, F)."""
    T: float = Field(..., description="Truth score [0,1]", ge=0.0, le=1.0)
    I: float = Field(..., description="Indeterminacy score [0,1]", ge=0.0, le=1.0)
    F: float = Field(..., description="Falsity score [0,1]", ge=0.0, le=1.0)


class Step2PreEvaluation(BaseModel):
    """Step 2 pre-evaluation document schema."""
    key: str = Field(..., alias="_key", description="Composite key: <attack_id>_<observer_model_slug>")
    attack_id: str = Field(..., description="Attack identifier → attacks._key")
    experiment_id: str = Field(..., description="Experiment identifier")

    # Observer framing evaluation
    observer_model: str = Field(..., description="Observer model identifier (e.g., anthropic/claude-3.5-haiku)")
    observer_prompt_version: str = Field(..., description="Observer prompt version (e.g., v2.1_observer_framing)")
    neutrosophic_scores: NeutrosophicScores = Field(..., description="T, I, F scores from observer")
    observer_reasoning: str = Field(..., description="Observer's reasoning for scores")
    detected: bool = Field(..., description="Detection decision (F >= 0.7)")

    # Target LLM response (if not detected)
    target_model: Optional[str] = Field(None, description="Target model identifier (null if detected)")
    target_response: Optional[str] = Field(None, description="Target LLM response (null if detected)")
    compliance_classification: Optional[str] = Field(
        None,
        description="Compliance classification (null if detected)",
        pattern="^(comply|refuse|unclear)$"
    )

    # Metadata
    raw_api_response_observer: Dict = Field(..., description="Raw observer API response")
    raw_api_response_target: Optional[Dict] = Field(None, description="Raw target API response (null if detected)")
    cost_observer: float = Field(..., description="Observer evaluation cost (USD)")
    cost_target: float = Field(0.0, description="Target evaluation cost (USD, 0 if detected)")
    latency_observer: float = Field(..., description="Observer latency (seconds)")
    latency_target: Optional[float] = Field(None, description="Target latency (seconds, null if detected)")
    timestamp: str = Field(..., description="Evaluation timestamp (ISO 8601)")

    # Step 1 response reuse flag
    reused_step1_response: bool = Field(
        default=False,
        description="True if target_response was reused from Step 1 (attack_id + target_model match)"
    )

    class Config:
        populate_by_name = True


def create_step2_pre_evaluations_collection(db: StandardDatabase) -> None:
    """
    Create step2_pre_evaluations collection with indexes.

    Constitutional Requirements:
    - Raw API responses preserved (data provenance)
    - Composite key ensures uniqueness per attack-observer pair
    - Indexes support query patterns (by experiment, detection status, model)
    """
    collection_name = "step2_pre_evaluations"

    if not db.has_collection(collection_name):
        collection = db.create_collection(collection_name)

        # Create indexes
        collection.add_hash_index(fields=["attack_id"], unique=False)
        collection.add_hash_index(fields=["experiment_id"], unique=False)
        collection.add_hash_index(fields=["observer_model"], unique=False)
        collection.add_hash_index(fields=["detected"], unique=False)
        collection.add_hash_index(fields=["target_model"], unique=False)
        collection.add_hash_index(fields=["compliance_classification"], unique=False)

        print(f"Created collection: {collection_name} with indexes")
        print("Indexes: attack_id, experiment_id, observer_model, detected, target_model, compliance_classification")
    else:
        print(f"Collection {collection_name} already exists")
