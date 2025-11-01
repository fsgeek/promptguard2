"""
Attacks Collection Schema
Constitutional Principle VII: Data Architecture - Immutable reference dataset

Ground truth dataset of 762 labeled prompts for evaluation.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from arango.database import StandardDatabase
from arango.exceptions import CollectionCreateError


class Attack(BaseModel):
    """
    Attack document schema.

    Represents a labeled prompt from the ground truth dataset.
    """
    key: str = Field(..., alias="_key", description="Attack identifier (e.g., 'attack_001')")
    prompt_text: str = Field(..., description="The prompt text to evaluate")
    ground_truth: str = Field(
        ...,
        description="Ground truth label",
        pattern="^(manipulative|extractive|reciprocal|borderline)$"
    )
    encoding_technique: Optional[str] = Field(None, description="Attack encoding technique")
    dataset_source: str = Field(..., description="Source dataset identifier")
    attack_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Attack-specific metadata")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="General metadata")

    class Config:
        populate_by_name = True


def create_attacks_collection(db: StandardDatabase) -> None:
    """
    Create attacks collection with indexes.

    Args:
        db: ArangoDB database instance

    Raises:
        CollectionCreateError: If collection creation fails
    """
    collection_name = "attacks"

    # Create collection if it doesn't exist
    if not db.has_collection(collection_name):
        collection = db.create_collection(collection_name)

        # Create indexes
        collection.add_hash_index(fields=["ground_truth"], unique=False)
        collection.add_hash_index(fields=["dataset_source"], unique=False)
        collection.add_hash_index(fields=["encoding_technique"], unique=False)

        print(f"Created collection: {collection_name} with indexes")
    else:
        print(f"Collection {collection_name} already exists")


def validate_attack_distribution(db: StandardDatabase, expected_total: int = 762) -> Dict[str, Any]:
    """
    Validate attacks collection has expected distribution.

    Expected distribution (from spec.md FR1):
    - 337 manipulative
    - 90 extractive
    - 330 reciprocal
    - 5 borderline
    - Total: 762

    Args:
        db: ArangoDB database instance
        expected_total: Expected total attack count

    Returns:
        Validation results with counts and status
    """
    collection = db.collection("attacks")

    # Count by ground_truth
    aql = """
    FOR doc IN attacks
        COLLECT label = doc.ground_truth WITH COUNT INTO count
        RETURN {label: label, count: count}
    """

    cursor = db.aql.execute(aql)
    distribution = {item["label"]: item["count"] for item in cursor}

    total = sum(distribution.values())

    return {
        "total": total,
        "distribution": distribution,
        "expected_total": expected_total,
        "valid": total == expected_total,
        "missing": expected_total - total if total < expected_total else 0,
    }
