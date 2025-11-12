#!/usr/bin/env python3
"""Verify that 125 clean Phase 1A attacks are accessible for post-TIF evaluation."""

from src.database.client import get_client

def main():
    client = get_client()
    db = client.get_database()

    # Query from handoff document
    query = """
    FOR doc IN step2_pre_evaluations
        FILTER doc.experiment_id == "exp_phase1_step2_pre_filter_v1"
        FILTER doc.detected == false
        LET attack = DOCUMENT(CONCAT('attacks/', doc.attack_id))
        FILTER attack.source_dataset NOT IN ["benign_malicious"]
        RETURN {
            attack_id: doc.attack_id,
            source: attack.source_dataset,
            pre_F: doc.neutrosophic_scores.F,
            pre_T: doc.neutrosophic_scores.T,
            pre_I: doc.neutrosophic_scores.I,
            has_response: doc.target_response != null,
            target_model: doc.target_model,
            prompt_text: attack.prompt_text
        }
    """

    cursor = db.aql.execute(query)
    results = list(cursor)

    print(f"Total clean attacks that passed pre-filter: {len(results)}")
    print()

    # Group by source
    by_source = {}
    for r in results:
        source = r['source']
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(r)

    print("Distribution by source:")
    for source, attacks in sorted(by_source.items()):
        print(f"  {source}: {len(attacks)}")
    print()

    # Check for missing responses
    missing_responses = [r for r in results if not r['has_response']]
    print(f"Attacks with missing target_response: {len(missing_responses)}")

    if missing_responses:
        print("  Attack IDs:", [r['attack_id'] for r in missing_responses[:5]])

    # Show sample
    print("\nSample attack (first or_bench):")
    or_bench_attacks = by_source.get('or_bench', [])
    if or_bench_attacks:
        sample = or_bench_attacks[0]
        print(f"  attack_id: {sample['attack_id']}")
        print(f"  source: {sample['source']}")
        print(f"  pre-TIF: T={sample['pre_T']:.3f}, I={sample['pre_I']:.3f}, F={sample['pre_F']:.3f}")
        print(f"  target_model: {sample['target_model']}")
        print(f"  has_response: {sample['has_response']}")
        print(f"  prompt_text (first 100 chars): {sample['prompt_text'][:100]}")

    return len(results)

if __name__ == "__main__":
    count = main()
    print(f"\n✓ Verification complete: {count} attacks ready for post-TIF evaluation")
