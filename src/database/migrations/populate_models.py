"""
Populate Models Collection from Old PromptGuard
Task T020a: Migrate model metadata from old PromptGuard models collection

Constitutional Principle VII: Data Architecture
Constitutional Principle IV: Fail-Fast

Migrates 7+ models with required metadata. Halts if insufficient models configured.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any
from arango.database import StandardDatabase
from arango.exceptions import DocumentInsertError

from src.database.client import get_client
from src.database.schemas.models import create_models_collection, validate_model_registry


def migrate_models(
    old_db: StandardDatabase,
    new_db: StandardDatabase,
    required_metadata: List[str] = None
) -> Dict[str, Any]:
    """
    Migrate models from old PromptGuard to PromptGuard2.

    Args:
        old_db: Old PromptGuard database
        new_db: PromptGuard2 database
        required_metadata: Required metadata fields

    Returns:
        Migration results

    Raises:
        ValueError: If insufficient models or missing required metadata
    """
    if required_metadata is None:
        required_metadata = [
            "frontier",
            "testing",
            # observer_framing_compatible and rlhf can be null - don't require
            # cost fields come from pricing.prompt/completion
        ]

    print("Starting models migration from old PromptGuard...")

    # Ensure collection exists in new database
    create_models_collection(new_db)

    # Query old models collection
    aql = """
    FOR model IN models
        RETURN model
    """

    try:
        cursor = old_db.aql.execute(aql)
        old_models = list(cursor)
    except Exception as e:
        raise ValueError(
            f"Failed to query old PromptGuard models collection: {e}. "
            "Ensure old database is accessible."
        )

    if len(old_models) < 7:
        raise ValueError(
            f"Insufficient models in old PromptGuard: {len(old_models)} found, 7 required. "
            "Manual validation required. Check old PromptGuard models collection."
        )

    print(f"Found {len(old_models)} models in old PromptGuard")

    # Validate required metadata
    migrated = []
    skipped = []

    for old_model in old_models:
        # Check for required metadata
        missing_fields = [
            field for field in required_metadata
            if field not in old_model or old_model[field] is None
        ]

        if missing_fields:
            skipped.append({
                "_key": old_model.get("_key"),
                "reason": f"Missing required fields: {missing_fields}"
            })
            continue

        # Transform to new schema
        new_model = _transform_model_schema(old_model)

        # Insert to new database
        try:
            new_db.collection("models").insert(new_model, overwrite=False)
            migrated.append(new_model["_key"])
            print(f"  ✓ Migrated: {new_model['_key']}")

        except DocumentInsertError:
            # Already exists - skip
            print(f"  - Skipped (already exists): {new_model['_key']}")

    print(f"\nMigration complete: {len(migrated)} models migrated, {len(skipped)} skipped")

    # Validate registry
    validation = validate_model_registry(new_db, min_models=7)

    if not validation["valid"]:
        error_msg = "\n".join([
            "Model registry validation FAILED after migration:",
            f"  Total models: {validation['total_models']}",
            f"  Testing models: {validation['testing_models']}",
            f"  Observer-compatible models: {validation['observer_compatible_models']}",
            "Errors:",
        ] + [f"  - {err}" for err in validation["errors"]])

        raise ValueError(error_msg + "\n\nManual validation required.")

    print("\n✓ Model registry validation PASSED")
    print(f"  Total models: {validation['total_models']}")
    print(f"  Testing models: {validation['testing_models']}")
    print(f"  Observer-compatible models: {validation['observer_compatible_models']}")

    return {
        "migrated_count": len(migrated),
        "skipped_count": len(skipped),
        "migrated_keys": migrated,
        "skipped": skipped,
        "validation": validation,
    }


def _transform_model_schema(old_model: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform old model schema to new schema.

    Old schema may have:
    - cost_per_1m_tokens (single field)

    New schema has:
    - cost_per_1m_input_tokens
    - cost_per_1m_output_tokens

    Args:
        old_model: Model document from old PromptGuard

    Returns:
        Transformed model document for PromptGuard2
    """
    # Extract provider from openrouter_id if family not present
    family = old_model.get("family") or old_model.get("provider", "unknown")

    new_model = {
        "_key": old_model["_key"],
        "name": old_model.get("name", old_model["_key"]),
        "family": family,
        "frontier": old_model.get("frontier", False),
        "testing": old_model.get("testing", False),
        "observer_framing_compatible": old_model.get("observer_framing_compatible"),
        "architecture_family": old_model.get("architecture_family"),
        "instruct": old_model.get("instruct"),
        "rlhf": old_model.get("rlhf"),
        "context_length": old_model.get("context_length"),
        "capabilities": old_model.get("capabilities", []),
        "deprecated": old_model.get("deprecated", False),
        "notes": old_model.get("notes"),
        "added": old_model.get("last_synced", datetime.now(timezone.utc).isoformat()),
    }

    # Handle cost fields from pricing object
    pricing = old_model.get("pricing", {})
    if pricing:
        # Convert from string to float (pricing values are strings in old schema)
        try:
            prompt_cost = float(pricing.get("prompt", 0))
            completion_cost = float(pricing.get("completion", 0))
            # Convert to per-1M tokens (old pricing is per-token)
            new_model["cost_per_1m_input_tokens"] = prompt_cost * 1_000_000 if prompt_cost else None
            new_model["cost_per_1m_output_tokens"] = completion_cost * 1_000_000 if completion_cost else None
        except (ValueError, TypeError):
            new_model["cost_per_1m_input_tokens"] = None
            new_model["cost_per_1m_output_tokens"] = None
    else:
        # Fallback to old schema if pricing object doesn't exist
        if "cost_per_1m_input_tokens" in old_model:
            new_model["cost_per_1m_input_tokens"] = old_model["cost_per_1m_input_tokens"]
        elif "cost_per_1m_tokens" in old_model:
            new_model["cost_per_1m_input_tokens"] = old_model["cost_per_1m_tokens"]

        if "cost_per_1m_output_tokens" in old_model:
            new_model["cost_per_1m_output_tokens"] = old_model["cost_per_1m_output_tokens"]
        elif "cost_per_1m_tokens" in old_model:
            new_model["cost_per_1m_output_tokens"] = old_model["cost_per_1m_tokens"]

    return new_model


def main():
    """CLI entry point for models migration."""
    client = get_client()

    try:
        old_db = client.get_old_database()
        new_db = client.get_database()

        results = migrate_models(old_db, new_db)

        print("\n" + "="*60)
        print("MODELS MIGRATION SUMMARY")
        print("="*60)
        print(f"Migrated: {results['migrated_count']} models")
        print(f"Skipped: {results['skipped_count']} models")
        print(f"\nValidation: {'PASSED ✓' if results['validation']['valid'] else 'FAILED ✗'}")

        if results['skipped']:
            print("\nSkipped models:")
            for skip in results['skipped']:
                print(f"  - {skip['_key']}: {skip['reason']}")

    except Exception as e:
        print(f"\n✗ Migration FAILED: {e}")
        raise


if __name__ == "__main__":
    main()
