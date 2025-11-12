"""
Migration: Fix missing source_dataset fields in attacks collection
Constitutional Principle VI: Data Provenance

All 762 attack documents must have source_dataset values for proper provenance
tracking. This migration infers missing source_dataset values from attack_id
patterns and updates documents with both the value and an audit timestamp.

Pattern mappings:
  benign_malicious_* → "benign_malicious"
  alignment_lab_* → "alignment_lab"
  system_prompt_* → "system_prompt_leak"
  external_* → "external"
  history_* → "history"
  or_bench_* → "or_bench"

Expected results:
  - 762 total documents updated
  - 0 null/empty source_dataset values
  - All documents have source_dataset_updated_at timestamp for audit
  - 100% pattern match rate
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

from src.database.client import get_client


def infer_source_from_id(attack_id: str) -> str:
    """
    Infer source_dataset from attack_id pattern.

    Args:
        attack_id: The attack identifier (e.g., 'benign_malicious_123')

    Returns:
        Source dataset name or None if pattern doesn't match
    """
    if not attack_id:
        return None

    prefixes = {
        "benign_malicious": "benign_malicious",
        "alignment_lab": "alignment_lab",
        "system_prompt": "system_prompt_leak",
        "external": "external",
        "history": "history",
        "or_bench": "or_bench",
    }

    for prefix, source in prefixes.items():
        if attack_id.startswith(prefix):
            return source

    return None


def fix_source_dataset():
    """
    Fix missing source_dataset fields in attacks collection.

    Returns:
        Migration results with counts and validation

    Raises:
        ValueError: If validation fails
    """
    client = get_client()
    db = client.get_database()

    print("Starting source_dataset migration...")

    # Query documents with missing/null source_dataset
    fetch_aql = """
    FOR doc IN attacks
        FILTER doc.source_dataset == null OR doc.source_dataset == ""
        RETURN {
            _key: doc._key,
            attack_id: doc.attack_id
        }
    """

    cursor = db.aql.execute(fetch_aql)
    docs = list(cursor)

    print(f"Found {len(docs)} documents with missing source_dataset")

    # Categorize by inferred source
    updates_by_source = {}
    unmatchable = []

    for doc in docs:
        attack_id = doc.get("attack_id") or doc.get("_key")
        inferred_source = infer_source_from_id(attack_id)

        if inferred_source:
            if inferred_source not in updates_by_source:
                updates_by_source[inferred_source] = []
            updates_by_source[inferred_source].append(doc["_key"])
        else:
            unmatchable.append({
                "_key": doc["_key"],
                "attack_id": attack_id
            })

    print(f"\nCategorized documents:")
    for source, keys in updates_by_source.items():
        print(f"  {source}: {len(keys)} documents")

    if unmatchable:
        print(f"\nWARNING: {len(unmatchable)} unmatchable documents")
        for doc in unmatchable[:5]:
            print(f"  {doc['_key']}")
        raise ValueError(
            f"{len(unmatchable)} documents have unmatchable attack_id patterns. "
            "Manual review required."
        )

    # Perform bulk updates via AQL
    timestamp = datetime.now(timezone.utc).isoformat()
    total_updated = 0
    errors = []

    for source, keys in updates_by_source.items():
        # Build AQL update query
        update_aql = """
        FOR key IN @keys
            UPDATE {"_key": key, "source_dataset": @source, "source_dataset_updated_at": @timestamp}
            IN attacks
        """

        try:
            db.aql.execute(
                update_aql,
                bind_vars={
                    "keys": keys,
                    "source": source,
                    "timestamp": timestamp
                }
            )
            total_updated += len(keys)
            print(f"  ✓ Updated {len(keys)} documents with source '{source}'")
        except Exception as e:
            error_msg = f"Error updating {source}: {e}"
            errors.append(error_msg)
            print(f"  ✗ {error_msg}")

    if errors:
        raise ValueError(f"Migration had {len(errors)} errors: {errors}")

    # Verify no nulls remain
    print("\nVerifying fixes...")
    verify_aql = """
    RETURN COUNT(FOR doc IN attacks
        FILTER doc.source_dataset == null OR doc.source_dataset == ""
        RETURN doc)
    """

    cursor = db.aql.execute(verify_aql)
    remaining_nulls = list(cursor)[0]

    if remaining_nulls > 0:
        raise ValueError(
            f"Verification FAILED: {remaining_nulls} documents still have null/empty source_dataset"
        )

    print("✓ Verification passed: No null/empty source_dataset values")

    # Show final distribution
    print("\nFinal source_dataset distribution:")
    dist_aql = """
    FOR doc IN attacks
        COLLECT source = doc.source_dataset WITH COUNT INTO count
        RETURN {source: source, count: count}
    """

    cursor = db.aql.execute(dist_aql)
    distribution = list(cursor)

    for item in sorted(distribution, key=lambda x: x.get("count", 0), reverse=True):
        source = item.get("source") or "NULL"
        count = item.get("count", 0)
        print(f"  {source}: {count}")

    return {
        "total_documents": 762,
        "documents_fixed": total_updated,
        "remaining_nulls": remaining_nulls,
        "distribution": {item.get("source"): item.get("count") for item in distribution},
        "validation_passed": remaining_nulls == 0 and total_updated == 762,
        "timestamp": timestamp,
    }


def main():
    """CLI entry point for source_dataset fix."""
    try:
        # Connect to database
        print("Connecting to database...")
        client = get_client()
        pg2_ok, _ = client.verify_connections()

        if not pg2_ok:
            raise ConnectionError(
                "Cannot connect to PromptGuard2 database. "
                "Check config/database.yaml and ARANGODB_PROMPTGUARD_PASSWORD"
            )

        print("✓ Database connection verified\n")

        # Run migration
        results = fix_source_dataset()

        # Summary
        print("\n" + "="*60)
        print("MIGRATION SUMMARY")
        print("="*60)
        print(f"Total documents: {results['total_documents']}")
        print(f"Documents fixed: {results['documents_fixed']}")
        print(f"Remaining nulls: {results['remaining_nulls']}")
        print(f"Validation: {'PASSED ✓' if results['validation_passed'] else 'FAILED ✗'}")
        print(f"Timestamp: {results['timestamp']}")

        if not results['validation_passed']:
            print("\n✗ Migration FAILED")
            sys.exit(1)
        else:
            print("\n✓ Migration PASSED")

    except Exception as e:
        print(f"\n✗ Migration FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
