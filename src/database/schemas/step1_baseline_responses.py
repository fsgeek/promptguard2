"""
Step 1 Baseline Responses Collection Schema
FR2: Step 1 Baseline Collection

Stores LLM responses to attacks without filtering (RLHF baseline behavior).
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from arango.database import StandardDatabase


class Step1BaselineResponse(BaseModel):
    """Step 1 baseline response document schema."""
    key: str = Field(..., alias="_key", description="<attack_id>_<model_slug>")
    attack_id: str = Field(..., description="Attack identifier → attacks._key")
    experiment_id: str = Field(default="exp_phase1_step1_baseline_v1", description="Experiment identifier")
    target_model: str = Field(..., description="Original model identifier")
    prompt_text: str = Field(..., description="Attack prompt text")
    ground_truth: str = Field(..., description="Ground truth label")
    raw_api_response: Dict[str, Any] = Field(..., description="Complete raw API response")
    response_text: str = Field(..., description="LLM response text")
    compliance_classification: Optional[str] = Field(
        None,
        description="Compliance classification",
        pattern="^(comply|refuse|unclear)$"
    )
    classification_method: Optional[str] = Field(
        None,
        description="Classification method",
        pattern="^(manual|automated|hybrid)$"
    )
    cost_usd: Optional[float] = Field(None, description="API cost in USD")
    latency_ms: Optional[int] = Field(None, description="Response latency in milliseconds")
    timestamp: str = Field(..., description="Response timestamp (ISO 8601)")
    error: Optional[str] = Field(None, description="Error message if evaluation failed")

    class Config:
        populate_by_name = True


def create_step1_baseline_responses_collection(db: StandardDatabase) -> None:
    """Create step1_baseline_responses collection with indexes."""
    collection_name = "step1_baseline_responses"

    if not db.has_collection(collection_name):
        collection = db.create_collection(collection_name)

        # Create indexes
        collection.add_hash_index(fields=["experiment_id"], unique=False)
        collection.add_hash_index(fields=["attack_id"], unique=False)
        collection.add_hash_index(fields=["target_model"], unique=False)
        collection.add_hash_index(fields=["ground_truth"], unique=False)
        collection.add_hash_index(fields=["compliance_classification"], unique=False)

        print(f"Created collection: {collection_name} with indexes")
    else:
        print(f"Collection {collection_name} already exists")
