"""
Migration CLI Command
Provides commands for database migrations with --verify flag.
"""

import sys
from src.database.migrations.migrate_attacks import main as migrate_attacks_main
from src.database.migrations.populate_models import main as populate_models_main
from src.database.schemas.attacks import validate_attack_distribution
from src.database.schemas.models import validate_model_registry
from src.database.client import get_client


def run_migrations():
    """Run all migrations in order."""
    print("Running all migrations...\n")

    print("="*60)
    print("MIGRATION 1: Populate Models")
    print("="*60)
    populate_models_main()

    print("\n" + "="*60)
    print("MIGRATION 2: Migrate Attacks")
    print("="*60)
    migrate_attacks_main()

    print("\n✓ All migrations complete")


def verify_migrations():
    """Verify all migrations completed successfully."""
    print("Verifying migrations...\n")

    client = get_client()
    db = client.get_database()

    # Verify attacks
    print("Verifying attacks collection...")
    attack_validation = validate_attack_distribution(db, expected_total=762)

    if attack_validation["valid"]:
        print(f"✓ Attacks: {attack_validation['total']} (expected 762)")
        print(f"  Distribution: {attack_validation['distribution']}")
    else:
        print(f"✗ Attacks validation FAILED:")
        print(f"  Found: {attack_validation['total']}, Expected: 762")
        print(f"  Missing: {attack_validation['missing']}")
        return False

    # Verify models
    print("\nVerifying models collection...")
    model_validation = validate_model_registry(db, min_models=7)

    if model_validation["valid"]:
        print(f"✓ Models: {model_validation['total_models']} (minimum 7)")
        print(f"  Testing models: {model_validation['testing_models']}")
        print(f"  Observer-compatible: {model_validation['observer_compatible_models']}")
    else:
        print(f"✗ Models validation FAILED:")
        for error in model_validation["errors"]:
            print(f"  - {error}")
        return False

    print("\n✓ All migrations verified successfully")
    return True


def main():
    """CLI entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        success = verify_migrations()
        sys.exit(0 if success else 1)
    else:
        run_migrations()


if __name__ == "__main__":
    main()
