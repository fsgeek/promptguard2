"""
Observer Prompts Collection Schema
Constitutional Principle VII: Data Architecture - Immutable versioned artifacts

Stores observer prompts for neutrosophic evaluation with provenance tracking.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from arango.database import StandardDatabase


class ObserverPrompt(BaseModel):
    """
    Observer prompt document schema.

    Immutable versioned prompts for observer framing evaluation.
    """
    key: str = Field(..., alias="_key", description="Version identifier (e.g., 'v2.1_observer_framing')")
    prompt_text: str = Field(..., description="Full prompt template text")
    version: str = Field(..., description="Semantic version (e.g., '2.1')")
    description: str = Field(..., description="Prompt purpose and changes")
    created: str = Field(..., description="Creation timestamp (ISO 8601)")
    created_by: str = Field(..., description="Creator (e.g., 'Instance 64', 'Tony')")
    parameters: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Prompt parameters (detection threshold, scoring instructions)"
    )

    class Config:
        populate_by_name = True


def create_observer_prompts_collection(db: StandardDatabase) -> None:
    """
    Create observer_prompts collection with indexes.

    Constitutional Principle VII: Immutable - Once created, never updated.

    Args:
        db: ArangoDB database instance
    """
    collection_name = "observer_prompts"

    if not db.has_collection(collection_name):
        collection = db.create_collection(collection_name)

        # Create indexes
        collection.add_hash_index(fields=["version"], unique=False)
        collection.add_hash_index(fields=["created_by"], unique=False)

        print(f"Created collection: {collection_name} with indexes")
        print("NOTE: This collection is IMMUTABLE - prompts are never updated, only versioned")
    else:
        print(f"Collection {collection_name} already exists")


def get_observer_prompt(db: StandardDatabase, version_key: str = "v2.1_observer_framing") -> Optional[ObserverPrompt]:
    """
    Get observer prompt by version key.

    Args:
        db: ArangoDB database instance
        version_key: Version key (e.g., 'v2.1_observer_framing')

    Returns:
        ObserverPrompt or None if not found
    """
    collection = db.collection("observer_prompts")

    try:
        doc = collection.get(version_key)
        if doc:
            return ObserverPrompt(**doc)
        return None
    except Exception:
        return None
