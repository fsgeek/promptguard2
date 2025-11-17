"""
Phase 2 Validation Evaluations Collection Schema

Constitutional Principle VI: Data Provenance
Phase: Phase 2 - Context Integrity Validation

Stores factorial validation results for three observer variants tested on
alignment_lab false negatives.
"""

from typing import Dict, Optional
from pydantic import BaseModel, Field
from arango.database import StandardDatabase


class NeutrosophicScores(BaseModel):
    """Neutrosophic logic scores (T, I, F)."""
    T: float = Field(..., description="Truth score [0,1]", ge=0.0, le=1.0)
    I: float = Field(..., description="Indeterminacy score [0,1]", ge=0.0, le=1.0)
    F: float = Field(..., description="Falsity score [0,1]", ge=0.0, le=1.0)


class Phase2ValidationEvaluation(BaseModel):
    """Phase 2 factorial validation evaluation schema."""
    key: str = Field(
        ...,
        alias="_key",
        description="Composite key: <attack_id>_<variant>_<observer_model_slug>"
    )
    attack_id: str = Field(..., description="Attack identifier → attacks._key")
    experiment_id: str = Field(..., description="Experiment identifier (e.g., exp_phase2_v2.1-a_turn_number)")

    # Variant tracking
    variant: str = Field(..., description="Observer variant (v2.1-a, v2.1-b, v2.1-c)", pattern="^v2\\.1-[abc]$")
    variant_type: str = Field(
        ...,
        description="Variant type classification",
        pattern="^(turn-number-only|context-integrity-only|combined)$"
    )
    observer_prompt_key: str = Field(..., description="Observer prompt key in observer_prompts collection")

    # Observer evaluation
    observer_model: str = Field(..., description="Observer model identifier")
    neutrosophic_scores: NeutrosophicScores = Field(..., description="T, I, F scores from observer")
    observer_reasoning: str = Field(..., description="Observer's reasoning for scores")
    detected: bool = Field(..., description="Detection decision (F >= 0.7)")

    # Baseline comparison (v2.1 scores from Phase 1)
    baseline_f_score: float = Field(..., description="Baseline v2.1 F score for this attack", ge=0.0, le=1.0)
    delta_f: float = Field(..., description="Change in F score from baseline (variant_F - baseline_F)")
    improvement: bool = Field(..., description="True if variant detected AND baseline didn't (F crossed 0.7 threshold)")

    # Turn-number parameter (for v2.1-a and v2.1-c)
    turn_number: Optional[int] = Field(None, description="Turn number parameter (null for v2.1-b, 0 for others)")

    # Metadata
    raw_api_response: Dict = Field(..., description="Raw observer API response")
    cost: float = Field(..., description="Evaluation cost (USD)")
    latency: float = Field(..., description="Observer latency (seconds)")
    timestamp: str = Field(..., description="Evaluation timestamp (ISO 8601)")

    class Config:
        populate_by_name = True


def create_phase2_validation_evaluations_collection(db: StandardDatabase) -> None:
    """
    Create phase2_validation_evaluations collection with indexes.

    Constitutional Requirements:
    - Raw API responses preserved (data provenance)
    - Composite key ensures uniqueness per attack-variant-observer tuple
    - Indexes support factorial analysis queries
    """
    collection_name = "phase2_validation_evaluations"

    if not db.has_collection(collection_name):
        collection = db.create_collection(collection_name)

        # Create indexes for factorial analysis
        collection.add_hash_index(fields=["attack_id"], unique=False)
        collection.add_hash_index(fields=["experiment_id"], unique=False)
        collection.add_hash_index(fields=["variant"], unique=False)
        collection.add_hash_index(fields=["variant_type"], unique=False)
        collection.add_hash_index(fields=["detected"], unique=False)
        collection.add_hash_index(fields=["improvement"], unique=False)

        print(f"Created collection: {collection_name} with indexes")
        print("Indexes: attack_id, experiment_id, variant, variant_type, detected, improvement")
    else:
        print(f"Collection {collection_name} already exists")
