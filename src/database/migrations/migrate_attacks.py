"""
Migration 001: Migrate Attacks from Old PromptGuard
Constitutional Principle VII: Data Architecture - Immutable reference dataset
Constitutional Principle VI: Data Provenance

Migrates 762 labeled attacks with complete metadata preservation.
"""

from typing import Dict, Any, List
from arango.database import StandardDatabase
from arango.exceptions import DocumentInsertError

from src.database.client import get_client
from src.database.schemas.attacks import create_attacks_collection, validate_attack_distribution


def migrate_attacks(old_db: StandardDatabase, new_db: StandardDatabase) -> Dict[str, Any]:
    """
    Migrate attacks from old PromptGuard to PromptGuard2.

    Expected:
    - 762 total attacks
    - 337 manipulative
    - 90 extractive
    - 330 reciprocal
    - 5 borderline

    Args:
        old_db: Old PromptGuard database
        new_db: PromptGuard2 database

    Returns:
        Migration results with counts and validation

    Raises:
        ValueError: If attack count/distribution doesn't match expected
    """
    print("Starting attacks migration from old PromptGuard...")

    # Ensure collection exists in new database
    create_attacks_collection(new_db)

    # Query old attacks collection
    aql = """
    FOR attack IN attacks
        RETURN attack
    """

    try:
        cursor = old_db.aql.execute(aql)
        old_attacks = list(cursor)
    except Exception as e:
        raise ValueError(
            f"Failed to query old PromptGuard attacks collection: {e}. "
            "Ensure old database is accessible and contains attacks collection."
        )

    print(f"Found {len(old_attacks)} attacks in old PromptGuard")

    if len(old_attacks) != 762:
        raise ValueError(
            f"Unexpected attack count: {len(old_attacks)} found, 762 expected. "
            "Migration halted - verify old database integrity."
        )

    # Migrate attacks
    migrated_count = 0
    skipped_count = 0
    errors = []

    for attack in old_attacks:
        try:
            # Validate required fields
            if not attack.get("prompt_text"):
                errors.append(f"Attack {attack.get('_key')} missing prompt_text")
                continue

            if not attack.get("ground_truth"):
                errors.append(f"Attack {attack.get('_key')} missing ground_truth")
                continue

            # Insert to new database (preserve _key for ID consistency)
            new_db.collection("attacks").insert(attack, overwrite=False)
            migrated_count += 1

            if migrated_count % 100 == 0:
                print(f"  Migrated {migrated_count}/{len(old_attacks)}...")

        except DocumentInsertError:
            # Already exists - skip
            skipped_count += 1
        except Exception as e:
            errors.append(f"Failed to migrate attack {attack.get('_key')}: {e}")

    print(f"\nMigration complete: {migrated_count} migrated, {skipped_count} skipped")

    if errors:
        print(f"\n⚠ {len(errors)} errors occurred:")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")

    # Validate distribution
    print("\nValidating attack distribution...")
    validation = validate_attack_distribution(new_db, expected_total=762)

    if not validation["valid"]:
        error_msg = (
            f"Attack distribution validation FAILED:\n"
            f"  Expected: 762 attacks\n"
            f"  Found: {validation['total']} attacks\n"
            f"  Distribution: {validation['distribution']}\n"
            f"  Missing: {validation['missing']} attacks"
        )
        raise ValueError(error_msg)

    print("✓ Distribution validation PASSED")
    print(f"  Total: {validation['total']}")
    print(f"  Distribution: {validation['distribution']}")

    return {
        "migrated_count": migrated_count,
        "skipped_count": skipped_count,
        "total_in_new_db": validation["total"],
        "distribution": validation["distribution"],
        "validation_passed": validation["valid"],
        "errors": errors,
    }


def main():
    """CLI entry point for attacks migration."""
    client = get_client()

    try:
        # Connect to both databases
        print("Connecting to databases...")
        old_db = client.get_old_database()
        new_db = client.get_database()

        # Verify connections
        pg2_ok, old_ok = client.verify_connections()

        if not pg2_ok:
            raise ConnectionError(
                "Cannot connect to PromptGuard2 database. "
                "Check config/database.yaml and ARANGODB_PROMPTGUARD_PASSWORD"
            )

        if not old_ok:
            raise ConnectionError(
                "Cannot connect to old PromptGuard database. "
                "Check config/database.yaml settings for old_database"
            )

        print("✓ Database connections verified\n")

        # Run migration
        results = migrate_attacks(old_db, new_db)

        # Summary
        print("\n" + "="*60)
        print("MIGRATION SUMMARY")
        print("="*60)
        print(f"Total migrated: {results['migrated_count']}")
        print(f"Skipped (already exists): {results['skipped_count']}")
        print(f"Total in PromptGuard2: {results['total_in_new_db']}")
        print(f"Distribution: {results['distribution']}")
        print(f"Validation: {'PASSED ✓' if results['validation_passed'] else 'FAILED ✗'}")

        if results['errors']:
            print(f"\n⚠ Errors: {len(results['errors'])}")

    except Exception as e:
        print(f"\n✗ Migration FAILED: {e}")
        raise


if __name__ == "__main__":
    main()
