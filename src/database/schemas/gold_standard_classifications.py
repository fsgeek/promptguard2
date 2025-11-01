"""
Gold Standard Classifications Collection Schema
FR3: Compliance Classification
Constitutional Principle VII: Immutable reference dataset

Stores 50-sample gold standard for compliance classifier validation.
"""

from typing import Optional
from pydantic import BaseModel, Field
from arango.database import StandardDatabase


class GoldStandardClassification(BaseModel):
    """Gold standard classification document schema."""
    key: str = Field(..., alias="_key", description="Attack ID from stratified sample")
    attack_id: str = Field(..., description="Attack identifier → attacks._key")
    prompt_text: str = Field(..., description="Attack prompt text")
    response_text: str = Field(..., description="LLM response from step1_baseline_responses")
    ground_truth: str = Field(..., description="Attack ground truth label")
    target_model: str = Field(..., description="Model that generated response")
    claude_classification: str = Field(
        ...,
        description="Claude's classification",
        pattern="^(comply|refuse|unclear)$"
    )
    claude_reasoning: str = Field(..., description="Claude's reasoning for classification")
    tony_review_status: str = Field(
        default="pending",
        description="Review status",
        pattern="^(approved|rejected|pending)$"
    )
    tony_override: Optional[str] = Field(
        None,
        description="Tony's override classification if rejected",
        pattern="^(comply|refuse|unclear)$"
    )
    final_classification: str = Field(
        ...,
        description="Final classification (Claude's or Tony's override)",
        pattern="^(comply|refuse|unclear)$"
    )
    created: str = Field(..., description="Creation timestamp (ISO 8601)")
    reviewed: Optional[str] = Field(None, description="Review timestamp (ISO 8601)")

    class Config:
        populate_by_name = True


def create_gold_standard_classifications_collection(db: StandardDatabase) -> None:
    """
    Create gold_standard_classifications collection.

    Constitutional Principle VII: IMMUTABLE - Once created and reviewed, never updated.
    """
    collection_name = "gold_standard_classifications"

    if not db.has_collection(collection_name):
        collection = db.create_collection(collection_name)

        # Create indexes
        collection.add_hash_index(fields=["ground_truth"], unique=False)
        collection.add_hash_index(fields=["final_classification"], unique=False)
        collection.add_hash_index(fields=["tony_review_status"], unique=False)

        print(f"Created collection: {collection_name} with indexes")
        print("NOTE: This collection is IMMUTABLE after review - preserves validation baseline")
    else:
        print(f"Collection {collection_name} already exists")
