"""
Models Collection Schema
Constitutional Principle VII: Data Architecture - Model metadata registry

Stores model metadata for capabilities tracking and selection.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from arango.database import StandardDatabase


class Model(BaseModel):
    """
    Model document schema.

    Stores model metadata for evaluation and analysis.
    """
    key: str = Field(..., alias="_key", description="Model identifier (e.g., 'anthropic/claude-haiku-4.5')")
    name: str = Field(..., description="Human-readable model name")
    family: str = Field(..., description="Provider/architecture family")
    frontier: bool = Field(..., description="Frontier model status")
    testing: bool = Field(..., description="Approved for testing/evaluation")
    observer_framing_compatible: bool = Field(..., description="Supports neutrosophic evaluation")
    architecture_family: Optional[str] = Field(None, description="Architecture (e.g., 'transformer', 'mamba')")
    instruct: bool = Field(default=False, description="Instruction-tuned")
    rlhf: bool = Field(default=False, description="RLHF-aligned")
    context_length: Optional[int] = Field(None, description="Context window size")
    capabilities: List[str] = Field(default_factory=list, description="Model capabilities")
    cost_per_1m_input_tokens: Optional[float] = Field(None, description="Cost per 1M input tokens (USD)")
    cost_per_1m_output_tokens: Optional[float] = Field(None, description="Cost per 1M output tokens (USD)")
    added: str = Field(..., description="Date added to registry (ISO 8601)")
    deprecated: bool = Field(default=False, description="Deprecated status")
    notes: Optional[str] = Field(None, description="Additional notes")

    class Config:
        populate_by_name = True


def create_models_collection(db: StandardDatabase) -> None:
    """
    Create models collection with indexes.

    Args:
        db: ArangoDB database instance
    """
    collection_name = "models"

    if not db.has_collection(collection_name):
        collection = db.create_collection(collection_name)

        # Create indexes
        collection.add_hash_index(fields=["frontier"], unique=False)
        collection.add_hash_index(fields=["testing"], unique=False)
        collection.add_hash_index(fields=["observer_framing_compatible"], unique=False)
        collection.add_hash_index(fields=["deprecated"], unique=False)
        collection.add_hash_index(fields=["family"], unique=False)

        print(f"Created collection: {collection_name} with indexes")
    else:
        print(f"Collection {collection_name} already exists")


def get_testing_models(db: StandardDatabase, deprecated: bool = False) -> List[Model]:
    """
    Get all models approved for testing.

    Args:
        db: ArangoDB database instance
        deprecated: Include deprecated models (default: False)

    Returns:
        List of Model objects approved for testing
    """
    collection = db.collection("models")

    aql = """
    FOR model IN models
        FILTER model.testing == true
        FILTER model.deprecated == @deprecated
        RETURN model
    """

    cursor = db.aql.execute(aql, bind_vars={"deprecated": deprecated})
    return [Model(**doc) for doc in cursor]


def get_observer_compatible_models(db: StandardDatabase) -> List[Model]:
    """
    Get models compatible with observer framing.

    Args:
        db: ArangoDB database instance

    Returns:
        List of observer-compatible Model objects
    """
    collection = db.collection("models")

    aql = """
    FOR model IN models
        FILTER model.observer_framing_compatible == true
        FILTER model.deprecated == false
        RETURN model
    """

    cursor = db.aql.execute(aql)
    return [Model(**doc) for doc in cursor]


def validate_model_registry(db: StandardDatabase, min_models: int = 7) -> Dict[str, Any]:
    """
    Validate models collection has sufficient models configured.

    Per T020a requirements:
    - At least 7 models required
    - Must have required metadata fields

    Args:
        db: ArangoDB database instance
        min_models: Minimum required model count

    Returns:
        Validation results
    """
    collection = db.collection("models")

    aql = """
    FOR model IN models
        RETURN {
            _key: model._key,
            testing: model.testing,
            observer_framing_compatible: model.observer_framing_compatible,
            deprecated: model.deprecated
        }
    """

    cursor = db.aql.execute(aql)
    models = list(cursor)

    testing_count = sum(1 for m in models if m.get("testing") and not m.get("deprecated"))
    observer_count = sum(1 for m in models if m.get("observer_framing_compatible") and not m.get("deprecated"))

    return {
        "total_models": len(models),
        "testing_models": testing_count,
        "observer_compatible_models": observer_count,
        "min_models_required": min_models,
        "valid": len(models) >= min_models and testing_count >= 5 and observer_count >= 2,
        "errors": _get_validation_errors(len(models), testing_count, observer_count, min_models),
    }


def _get_validation_errors(total: int, testing: int, observer: int, min_required: int) -> List[str]:
    """Generate validation error messages."""
    errors = []

    if total < min_required:
        errors.append(
            f"Insufficient models configured: {total} found, {min_required} required. "
            "Run migration T020a to populate models from old PromptGuard."
        )

    if testing < 5:
        errors.append(
            f"Insufficient testing models: {testing} found, 5 required (Phase 1 uses 5 target models)"
        )

    if observer < 2:
        errors.append(
            f"Insufficient observer-compatible models: {observer} found, 2 required "
            "(Haiku + Sonnet for comparison)"
        )

    return errors
