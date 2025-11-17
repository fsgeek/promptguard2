"""
Heal Gold Standard Provenance Break

Root Cause:
- gold_standard_classifications sampled from phase1b_curated_prompts (950 docs)
- References stored as attack_id pointing to phase1b_curated_prompts._key
- attacks collection only has 762 docs (never imported phase1b data)
- Result: 50/100 gold_standard_classifications have broken attack_id references

Solution:
- Create corresponding documents in attacks collection for the 50 broken references
- Migrate data from phase1b_curated_prompts (source of truth)
- Add metadata indicating this is a provenance healing migration
- Preserve referential integrity going forward

Constitutional Principle VI: Data Provenance
- Document where data came from (phase1b_curated_prompts)
- Preserve original_id for audit trail
- Mark as backfilled to distinguish from original attacks

Usage:
    uv run python -m src.database.migrations.heal_gold_standard_provenance --dry-run
    uv run python -m src.database.migrations.heal_gold_standard_provenance --execute
"""

import argparse
from datetime import datetime, timezone
from typing import List, Dict, Set
from src.database.client import get_client


def find_broken_references(db) -> Set[str]:
    """Find gold_standard attack_ids that don't exist in attacks collection."""

    # Get all gold_standard attack_ids
    gold_result = db.aql.execute('''
        FOR doc IN gold_standard_classifications
          RETURN doc.attack_id
    ''')
    gold_ids = set(list(gold_result))

    # Get all attacks keys
    attack_result = db.aql.execute('''
        FOR doc IN attacks
          RETURN doc._key
    ''')
    attack_keys = set(list(attack_result))

    # Find broken references
    broken = gold_ids - attack_keys

    return broken


def get_phase1b_source_data(db, attack_ids: Set[str]) -> List[Dict]:
    """
    Get source data from phase1b_curated_prompts for broken references.

    Returns documents ready for insertion into attacks collection.
    """

    result = db.aql.execute('''
        FOR doc IN phase1b_curated_prompts
          FILTER doc._key IN @attack_ids
          RETURN {
              _key: doc._key,
              prompt_text: doc.prompt,
              ground_truth: doc.ground_truth,
              source_dataset: doc.source_dataset,
              dataset_source: "phase1b_curated_prompts",
              metadata: {
                  migration: "provenance_healing_2025-11-13",
                  original_collection: "phase1b_curated_prompts",
                  original_id: doc._key,
                  reason: "Referenced by gold_standard_classifications but missing from attacks",
                  migrated_at: @migrated_at,
                  phase1b_fields: {
                      raw_record_id: doc.raw_record_id,
                      raw_record_link: doc.raw_record_link,
                      source_file: doc.source_file,
                      domain: doc.domain,
                      attack_type: doc.attack_type,
                      curated_at: doc.curated_at
                  }
              },
              attack_metadata: {
                  is_adversarial: doc.is_adversarial,
                  attack_objectives: doc.attack_objectives,
                  attack_type: doc.attack_type,
                  domain: doc.domain
              }
          }
    ''', bind_vars={
        'attack_ids': list(attack_ids),
        'migrated_at': datetime.now(timezone.utc).isoformat()
    })

    return list(result)


def verify_no_duplicates(db, documents: List[Dict]) -> Dict[str, str]:
    """
    Check if any of these prompts already exist in attacks under different keys.

    Returns dict of {new_key: existing_key} for any duplicates found.
    """

    duplicates = {}

    for doc in documents:
        result = db.aql.execute('''
            FOR attack IN attacks
              FILTER attack.prompt_text == @prompt_text
              RETURN attack._key
        ''', bind_vars={'prompt_text': doc['prompt_text']})

        existing_keys = list(result)
        if existing_keys:
            duplicates[doc['_key']] = existing_keys[0]

    return duplicates


def heal_provenance(db, dry_run: bool = True) -> Dict:
    """
    Main healing function.

    Args:
        db: ArangoDB database connection
        dry_run: If True, only report what would be done

    Returns:
        Summary dict with counts and actions taken
    """

    print("=" * 70)
    print("Gold Standard Provenance Healing")
    print("=" * 70)
    print()

    # Step 1: Find broken references
    print("Step 1: Finding broken references...")
    broken_ids = find_broken_references(db)
    print(f"  Found {len(broken_ids)} broken references")

    if not broken_ids:
        print("  ✓ No broken references - provenance is intact")
        return {'status': 'clean', 'broken_count': 0}

    print(f"  Sample broken IDs: {list(broken_ids)[:5]}")
    print()

    # Step 2: Get source data
    print("Step 2: Retrieving source data from phase1b_curated_prompts...")
    source_docs = get_phase1b_source_data(db, broken_ids)
    print(f"  Retrieved {len(source_docs)} source documents")

    if len(source_docs) != len(broken_ids):
        missing = broken_ids - {doc['_key'] for doc in source_docs}
        print(f"  ⚠️  WARNING: {len(missing)} IDs not found in phase1b_curated_prompts:")
        for mid in list(missing)[:5]:
            print(f"    - {mid}")
    print()

    # Step 3: Check for duplicates
    print("Step 3: Checking for duplicate prompts...")
    duplicates = verify_no_duplicates(db, source_docs)

    if duplicates:
        print(f"  ⚠️  WARNING: {len(duplicates)} prompts already exist in attacks:")
        for new_key, existing_key in list(duplicates.items())[:5]:
            print(f"    - {new_key} duplicates {existing_key}")
        print()
        print("  These indicate the prompts exist but with different keys.")
        print("  gold_standard_classifications should be updated to reference existing keys.")
        print()
    else:
        print(f"  ✓ No duplicates found")
    print()

    # Step 4: Preview or execute migration
    docs_to_insert = [doc for doc in source_docs if doc['_key'] not in duplicates]

    if dry_run:
        print("=" * 70)
        print("DRY RUN - No changes will be made")
        print("=" * 70)
        print()
        print(f"Would insert {len(docs_to_insert)} documents into attacks collection")

        if docs_to_insert:
            print("\nSample document preview:")
            print(f"  _key: {docs_to_insert[0]['_key']}")
            print(f"  ground_truth: {docs_to_insert[0]['ground_truth']}")
            print(f"  prompt_text: {docs_to_insert[0]['prompt_text'][:100]}...")
            print(f"  metadata: {docs_to_insert[0]['metadata']}")

        if duplicates:
            print(f"\nWould also need to update {len(duplicates)} gold_standard_classifications")
            print("  to reference existing attack keys instead of phase1b keys")

        print()
        print("To execute migration, run with --execute flag")

        return {
            'status': 'dry_run',
            'broken_count': len(broken_ids),
            'to_insert': len(docs_to_insert),
            'duplicates': len(duplicates)
        }

    else:
        print("=" * 70)
        print("EXECUTING MIGRATION")
        print("=" * 70)
        print()

        # Insert documents
        if docs_to_insert:
            print(f"Inserting {len(docs_to_insert)} documents into attacks...")

            collection = db.collection('attacks')
            inserted = 0
            errors = []

            for doc in docs_to_insert:
                try:
                    collection.insert(doc)
                    inserted += 1
                    if inserted % 10 == 0:
                        print(f"  Inserted {inserted}/{len(docs_to_insert)}...")
                except Exception as e:
                    errors.append((doc['_key'], str(e)))

            print(f"  ✓ Inserted {inserted} documents")

            if errors:
                print(f"  ✗ {len(errors)} errors:")
                for key, error in errors[:5]:
                    print(f"    - {key}: {error}")

        # Update gold_standard_classifications for duplicates
        if duplicates:
            print(f"\n⚠️  Manual update needed for {len(duplicates)} gold_standard docs")
            print("  These reference phase1b keys that duplicate existing attacks")
            print("  Recommendation: Update attack_id to reference existing attack keys")

        print()
        print("=" * 70)
        print("Migration complete")
        print("=" * 70)

        return {
            'status': 'executed',
            'broken_count': len(broken_ids),
            'inserted': inserted,
            'duplicates': len(duplicates),
            'errors': len(errors)
        }


def main():
    parser = argparse.ArgumentParser(description="Heal gold standard provenance break")
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    parser.add_argument('--execute', action='store_true',
                       help='Execute the migration')

    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        print("Error: Must specify either --dry-run or --execute")
        parser.print_help()
        return

    db = get_client().get_database()

    result = heal_provenance(db, dry_run=args.dry_run)

    print("\nSummary:")
    for key, value in result.items():
        print(f"  {key}: {value}")


if __name__ == '__main__':
    main()
