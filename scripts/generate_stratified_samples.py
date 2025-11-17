#!/usr/bin/env python3
"""
Generate stratified validation sample from attacks collection.

Sample allocation (revised for statistical adequacy):
- Category 1: Meta-framing (23 - already tested in factorial validation)
- Category 2: Jailbreak (40: 20 jailbreakbench + 20 dan_jailbreak)
- Category 3: Prompt Injection (30: bipia)
- Category 4: Harmful Requests (30: harmbench)
- Category 5: Extractive (30: mixed sources, ground_truth='extractive')
- Category 6: Benign (40: benign_malicious reciprocal for FP testing)

Total: 193 samples (23 existing + 170 new)
"""

import json
from pathlib import Path
from src.database.client import get_client

def get_already_tested_keys():
    """Get attack keys already tested in factorial validation."""
    client = get_client()
    db = client.get_database()

    result = db.aql.execute("""
        FOR eval IN phase2_validation_evaluations
          FILTER eval.experiment_id IN [
            'exp_phase2_v2.1-a_turn_number',
            'exp_phase2_v2.1-b_context_integrity',
            'exp_phase2_v2.1-c_combined'
          ]
          RETURN DISTINCT eval.attack_id
    """)

    return list(result)

def sample_jailbreakbench(exclude_keys, n=20):
    """Sample n attacks from jailbreakbench dataset."""
    client = get_client()
    db = client.get_database()

    result = db.aql.execute("""
        FOR doc IN attacks
          FILTER doc.source_dataset == 'jailbreakbench'
          FILTER doc.ground_truth == 'manipulative'
          FILTER doc._key NOT IN @exclude_keys
          SORT RAND()
          LIMIT @n
          RETURN doc._key
    """, bind_vars={'exclude_keys': exclude_keys, 'n': n})

    return list(result)

def sample_dan_jailbreak(exclude_keys, n=20):
    """Sample n attacks from dan_jailbreak dataset."""
    client = get_client()
    db = client.get_database()

    result = db.aql.execute("""
        FOR doc IN attacks
          FILTER doc.source_dataset == 'dan_jailbreak'
          FILTER doc.ground_truth == 'manipulative'
          FILTER doc._key NOT IN @exclude_keys
          SORT RAND()
          LIMIT @n
          RETURN doc._key
    """, bind_vars={'exclude_keys': exclude_keys, 'n': n})

    return list(result)

def sample_bipia(exclude_keys, n=30):
    """Sample n attacks from bipia dataset."""
    client = get_client()
    db = client.get_database()

    result = db.aql.execute("""
        FOR doc IN attacks
          FILTER doc.source_dataset == 'bipia'
          FILTER doc.ground_truth == 'manipulative'
          FILTER doc._key NOT IN @exclude_keys
          SORT RAND()
          LIMIT @n
          RETURN doc._key
    """, bind_vars={'exclude_keys': exclude_keys, 'n': n})

    return list(result)

def sample_harmbench(exclude_keys, n=30):
    """Sample n attacks from harmbench dataset."""
    client = get_client()
    db = client.get_database()

    result = db.aql.execute("""
        FOR doc IN attacks
          FILTER doc.source_dataset == 'harmbench'
          FILTER doc.ground_truth == 'manipulative'
          FILTER doc._key NOT IN @exclude_keys
          SORT RAND()
          LIMIT @n
          RETURN doc._key
    """, bind_vars={'exclude_keys': exclude_keys, 'n': n})

    return list(result)

def sample_extractive(exclude_keys, n=30):
    """Sample n extractive attacks from any source."""
    client = get_client()
    db = client.get_database()

    result = db.aql.execute("""
        FOR doc IN attacks
          FILTER doc.ground_truth == 'extractive'
          FILTER doc._key NOT IN @exclude_keys
          SORT RAND()
          LIMIT @n
          RETURN doc._key
    """, bind_vars={'exclude_keys': exclude_keys, 'n': n})

    return list(result)

def sample_benign(exclude_keys, n=40):
    """Sample n benign prompts for false positive testing."""
    client = get_client()
    db = client.get_database()

    result = db.aql.execute("""
        FOR doc IN attacks
          FILTER doc.ground_truth == 'reciprocal'
          FILTER doc.source_dataset == 'benign_malicious'
          FILTER doc._key NOT IN @exclude_keys
          SORT RAND()
          LIMIT @n
          RETURN doc._key
    """, bind_vars={'exclude_keys': exclude_keys, 'n': n})

    return list(result)

def main():
    print("Generating stratified validation samples...")
    print()

    # Get already-tested keys from factorial validation
    print("Fetching already-tested attack keys from factorial validation...")
    already_tested = get_already_tested_keys()
    print(f"Found {len(already_tested)} attacks already tested")
    print(f"Sample: {already_tested[:5]}")
    print()

    # Sample each category
    samples = {}

    print("Category 1: Meta-framing (alignment_lab)")
    print(f"  Already tested: {len(already_tested)} samples")
    samples['meta_framing'] = {
        'source': 'alignment_lab (factorial validation)',
        'attack_keys': already_tested,
        'count': len(already_tested),
        'ground_truth': 'manipulative',
        'expected_difficulty': 'meta-framing with embedded refusals'
    }
    print()

    print("Category 2a: Jailbreak - jailbreakbench (n=20)")
    jailbreakbench_keys = sample_jailbreakbench(already_tested, n=20)
    print(f"  Sampled: {len(jailbreakbench_keys)} attacks")
    samples['jailbreak_jailbreakbench'] = {
        'source': 'jailbreakbench',
        'attack_keys': jailbreakbench_keys,
        'count': len(jailbreakbench_keys),
        'ground_truth': 'manipulative',
        'expected_difficulty': 'role-play, hypotheticals'
    }
    print()

    print("Category 2b: Jailbreak - dan_jailbreak (n=20)")
    dan_keys = sample_dan_jailbreak(already_tested, n=20)
    print(f"  Sampled: {len(dan_keys)} attacks")
    samples['jailbreak_dan'] = {
        'source': 'dan_jailbreak',
        'attack_keys': dan_keys,
        'count': len(dan_keys),
        'ground_truth': 'manipulative',
        'expected_difficulty': 'role-play, hypotheticals'
    }
    print()

    print("Category 3: Prompt Injection - bipia (n=30)")
    bipia_keys = sample_bipia(already_tested, n=30)
    print(f"  Sampled: {len(bipia_keys)} attacks")
    samples['prompt_injection'] = {
        'source': 'bipia',
        'attack_keys': bipia_keys,
        'count': len(bipia_keys),
        'ground_truth': 'manipulative',
        'expected_difficulty': 'context confusion, legitimate-looking injections'
    }
    print()

    print("Category 4: Harmful Requests - harmbench (n=30)")
    harmbench_keys = sample_harmbench(already_tested, n=30)
    print(f"  Sampled: {len(harmbench_keys)} attacks")
    samples['harmful_requests'] = {
        'source': 'harmbench',
        'attack_keys': harmbench_keys,
        'count': len(harmbench_keys),
        'ground_truth': 'manipulative',
        'expected_difficulty': 'direct policy violations'
    }
    print()

    print("Category 5: Extractive - mixed sources (n=30)")
    extractive_keys = sample_extractive(already_tested, n=30)
    print(f"  Sampled: {len(extractive_keys)} attacks")
    samples['extractive'] = {
        'source': 'mixed (ground_truth=extractive)',
        'attack_keys': extractive_keys,
        'count': len(extractive_keys),
        'ground_truth': 'extractive',
        'expected_difficulty': 'polite extraction requests'
    }
    print()

    print("Category 6: Benign - FALSE POSITIVE TEST (n=40)")
    benign_keys = sample_benign(already_tested, n=40)
    print(f"  Sampled: {len(benign_keys)} attacks")
    samples['benign_reciprocal'] = {
        'source': 'benign_malicious (ground_truth=reciprocal)',
        'attack_keys': benign_keys,
        'count': len(benign_keys),
        'ground_truth': 'reciprocal',
        'expected_difficulty': 'should NOT detect (F < 0.7)'
    }
    print()

    # Calculate totals
    total_samples = sum(cat['count'] for cat in samples.values())
    new_samples = total_samples - len(already_tested)

    print("=" * 60)
    print("SAMPLE SUMMARY")
    print("=" * 60)
    for category, data in samples.items():
        print(f"{category}: {data['count']} samples from {data['source']}")
    print()
    print(f"Total samples: {total_samples}")
    print(f"  Existing (factorial validation): {len(already_tested)}")
    print(f"  New samples: {new_samples}")
    print()

    # Save to JSON file
    output_file = Path(__file__).parent.parent / 'stratified_validation_samples.json'

    output_data = {
        'metadata': {
            'total_samples': total_samples,
            'existing_samples': len(already_tested),
            'new_samples': new_samples,
            'sampling_date': '2025-11-16',
            'statistical_justification': 'See stratified_validation_statistical_justification.md'
        },
        'categories': samples
    }

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Saved sample allocation to: {output_file}")
    print()
    print("Next step: Run validation with v2.2 observer on new samples")
    print("  Command: uv run python scripts/run_stratified_validation.py")

if __name__ == '__main__':
    main()
