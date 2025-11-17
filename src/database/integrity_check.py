"""
Database Referential Integrity Checker

Constitutional Principle VI: Data Provenance

Validates that all foreign key references are intact:
- gold_standard_classifications.attack_id → attacks._key
- step1_baseline_responses.attack_id → attacks._key
- step2_pre_evaluations.attack_id → attacks._key
- step2_post_evaluations.attack_id → attacks._key
- phase2_validation_evaluations.attack_id → attacks._key

Usage:
    uv run python -m src.database.integrity_check
    uv run python -m src.database.integrity_check --verbose
    uv run python -m src.database.integrity_check --collection gold_standard_classifications

Exit codes:
    0: All integrity checks passed
    1: Integrity violations found
"""

import argparse
import sys
from typing import Dict, List, Set, Tuple
from src.database.client import get_client


# Define foreign key relationships
FOREIGN_KEYS = {
    'gold_standard_classifications': {
        'field': 'attack_id',
        'references': ('attacks', '_key'),
        'description': 'Gold standard attack references'
    },
    'step1_baseline_responses': {
        'field': 'attack_id',
        'references': ('attacks', '_key'),
        'description': 'Baseline response attack references'
    },
    'step2_pre_evaluations': {
        'field': 'attack_id',
        'references': ('attacks', '_key'),
        'description': 'Pre-evaluation attack references'
    },
    'step2_post_evaluations': {
        'field': 'attack_id',
        'references': ('attacks', '_key'),
        'description': 'Post-evaluation attack references'
    },
    'phase2_validation_evaluations': {
        'field': 'attack_id',
        'references': ('attacks', '_key'),
        'description': 'Phase 2 validation attack references'
    }
}


def check_foreign_keys(db, collection_name: str, verbose: bool = False) -> Tuple[bool, Dict]:
    """
    Check foreign key integrity for a collection.

    Returns:
        (passed, details_dict)
    """

    if collection_name not in FOREIGN_KEYS:
        return True, {'status': 'skipped', 'reason': 'no foreign keys defined'}

    fk_config = FOREIGN_KEYS[collection_name]
    field = fk_config['field']
    ref_collection, ref_field = fk_config['references']

    # Get all foreign key values
    fk_result = db.aql.execute(f'''
        FOR doc IN {collection_name}
          RETURN doc.{field}
    ''')
    fk_values = set(list(fk_result))

    # Get all referenced keys
    ref_result = db.aql.execute(f'''
        FOR doc IN {ref_collection}
          RETURN doc.{ref_field}
    ''')
    ref_keys = set(list(ref_result))

    # Find broken references
    broken = fk_values - ref_keys

    passed = len(broken) == 0

    details = {
        'collection': collection_name,
        'description': fk_config['description'],
        'field': field,
        'references': f'{ref_collection}.{ref_field}',
        'total_docs': len(fk_values),
        'unique_refs': len(fk_values),
        'broken_refs': len(broken),
        'passed': passed
    }

    if verbose and broken:
        details['sample_broken'] = list(broken)[:10]

    return passed, details


def check_all_integrity(db, verbose: bool = False, target_collection: str = None) -> Dict:
    """
    Run all integrity checks.

    Returns:
        Summary dict with results
    """

    collections_to_check = (
        [target_collection] if target_collection
        else list(FOREIGN_KEYS.keys())
    )

    results = {}
    total_passed = 0
    total_failed = 0

    for collection in collections_to_check:
        # Check if collection exists
        if not db.has_collection(collection):
            results[collection] = {
                'status': 'skipped',
                'reason': 'collection does not exist'
            }
            continue

        passed, details = check_foreign_keys(db, collection, verbose)

        results[collection] = details

        if passed:
            total_passed += 1
        else:
            total_failed += 1

    return {
        'total_checks': total_passed + total_failed,
        'passed': total_passed,
        'failed': total_failed,
        'results': results
    }


def print_report(summary: Dict, verbose: bool = False):
    """Print integrity check report."""

    print("=" * 70)
    print("Database Referential Integrity Check")
    print("=" * 70)
    print()

    all_passed = summary['failed'] == 0

    for collection, details in summary['results'].items():
        if details.get('status') == 'skipped':
            print(f"⊘ {collection}")
            print(f"  {details['reason']}")
            print()
            continue

        status = "✓" if details['passed'] else "✗"
        print(f"{status} {collection}")
        print(f"  {details['description']}")
        print(f"  {details['field']} → {details['references']}")
        print(f"  Total docs: {details['total_docs']}")

        if details['passed']:
            print(f"  ✓ All references valid")
        else:
            print(f"  ✗ Broken references: {details['broken_refs']}")

            if verbose and 'sample_broken' in details:
                print(f"  Sample broken IDs:")
                for bid in details['sample_broken'][:5]:
                    print(f"    - {bid}")

        print()

    print("=" * 70)
    print(f"Summary: {summary['passed']}/{summary['total_checks']} checks passed")

    if all_passed:
        print("✓ All integrity checks PASSED")
    else:
        print(f"✗ {summary['failed']} integrity check(s) FAILED")

    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Check database referential integrity"
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output including broken reference samples'
    )
    parser.add_argument(
        '--collection', '-c',
        type=str,
        help='Check only specific collection'
    )

    args = parser.parse_args()

    db = get_client().get_database()

    summary = check_all_integrity(
        db,
        verbose=args.verbose,
        target_collection=args.collection
    )

    print_report(summary, verbose=args.verbose)

    # Exit with error code if any checks failed
    sys.exit(0 if summary['failed'] == 0 else 1)


if __name__ == '__main__':
    main()
