#!/usr/bin/env python3
"""
Extract Benign Sequences from TensorTrust and ShareGPT

Task T006: Extract 100 benign multi-turn sequences (50 TensorTrust + 50 ShareGPT)

TensorTrust:
- Filter: output_is_access_granted==False AND no_extraction_keywords
- Stratified sampling: 20x 3-turn, 15x 4-turn, 10x 5-turn, 5x 6-8 turn
- Source: data/raw_datasets/tensortrust-data/raw-data/v2/raw_dump_attacks.jsonl.bz2

ShareGPT:
- Skip with message if not available (download required)

Constitutional Requirements:
- Provenance logging (source URLs, filter criteria, timestamp)
- Idempotent insertion via attack_id as _key

Date: 2025-11-18
Phase: Phase 3 - Session-Based Temporal Tracking
"""

import json
import bz2
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from src.database.client import get_client
from src.database.schemas.phase3_evaluation import (
    EvaluationSequence,
    AttackLabel,
    SourceDataset
)


# ===== EXTRACTION CONFIGURATION =====

TENSORTRUST_DATA_PATH = Path("data/raw_datasets/tensortrust-data/raw-data/v2/raw_dump_attacks.jsonl.bz2")

# Extraction keywords (from tensortrust_schema.md)
EXTRACTION_KEYWORDS = [
    'password', 'secret', 'access code', 'reveal', 'show',
    'instructions', 'ignore', 'override', 'bypass', 'tell me',
    'what is', 'repeat', 'print', 'output', 'code'
]

# Stratified sampling targets
SAMPLING_TARGETS = {
    3: 20,  # 20x 3-turn sequences
    4: 15,  # 15x 4-turn sequences
    5: 10,  # 10x 5-turn sequences
    6: 3,   # 3x 6-turn sequences
    7: 1,   # 1x 7-turn sequences
    8: 1    # 1x 8-turn sequences
}


def is_benign_sequence(attacks: List[Dict[str, Any]]) -> bool:
    """
    Check if multi-turn sequence is benign.

    Criteria:
    1. All defenses succeeded (output_is_access_granted == False)
    2. No extraction keywords in attacker inputs

    Args:
        attacks: List of attack records (sorted by timestamp)

    Returns:
        True if benign, False otherwise
    """
    # Criterion 1: All defenses succeeded
    if any(attack['output_is_access_granted'] for attack in attacks):
        return False

    # Criterion 2: No extraction attempts
    for attack in attacks:
        input_text = attack.get('attacker_input')
        if input_text is None:
            return False  # Skip null inputs

        input_lower = input_text.lower()
        if any(kw in input_lower for kw in EXTRACTION_KEYWORDS):
            return False

    return True


def extract_tensortrust_sequences(
    data_path: Path,
    sampling_targets: Dict[int, int]
) -> List[EvaluationSequence]:
    """
    Extract benign sequences from TensorTrust with stratified sampling.

    Args:
        data_path: Path to raw_dump_attacks.jsonl.bz2
        sampling_targets: Dict mapping turn_count -> num_sequences

    Returns:
        List of EvaluationSequence objects
    """
    print("=" * 80)
    print("EXTRACTING TENSORTRUST BENIGN SEQUENCES")
    print("=" * 80)
    print(f"Source: {data_path}")
    print(f"Sampling targets: {sampling_targets}")
    print()

    if not data_path.exists():
        raise FileNotFoundError(
            f"TensorTrust data not found at {data_path}. "
            "Please download the dataset first."
        )

    # Load and group attacks by defense_id
    print("Loading attacks...")
    attacks_by_defense = defaultdict(list)

    with bz2.open(data_path, 'rt') as f:
        for i, line in enumerate(f):
            attack = json.loads(line)

            # Filter out attacks without defense_id
            if attack['defense_id'] is not None:
                attacks_by_defense[attack['defense_id']].append(attack)

            # Progress indicator
            if (i + 1) % 100000 == 0:
                print(f"  Processed {i + 1} attacks...")

    print(f"✓ Loaded {len(attacks_by_defense)} unique defenses")
    print()

    # Sort attacks by timestamp within each defense
    for defense_id in attacks_by_defense:
        attacks_by_defense[defense_id].sort(key=lambda x: x['timestamp'])

    # Filter benign sequences with stratified sampling
    print("Filtering benign sequences...")
    benign_by_turn_count = defaultdict(list)
    total_target = sum(sampling_targets.values())

    for defense_id, attacks in attacks_by_defense.items():
        turn_count = len(attacks)

        # Only consider sequences in our target turn counts
        if turn_count not in sampling_targets:
            continue

        # Check if we've already collected enough for this turn count
        if len(benign_by_turn_count[turn_count]) >= sampling_targets[turn_count]:
            continue

        # Check benign criteria
        if not is_benign_sequence(attacks):
            continue

        # Add to benign collection
        benign_by_turn_count[turn_count].append({
            'defense_id': defense_id,
            'attacks': attacks
        })

        # Progress indicator
        total_collected = sum(len(seqs) for seqs in benign_by_turn_count.values())
        if total_collected % 10 == 0:
            print(f"  Collected {total_collected}/{total_target} sequences...")

        # Early exit if we've collected enough
        if total_collected >= total_target:
            break

    print()
    print("Stratified sampling results:")
    total_collected = 0
    for turn_count in sorted(benign_by_turn_count.keys()):
        collected = len(benign_by_turn_count[turn_count])
        target = sampling_targets[turn_count]
        total_collected += collected
        print(f"  {turn_count}-turn: {collected}/{target} sequences")

    print(f"  Total: {total_collected}/{total_target} sequences")
    print()

    # Convert to EvaluationSequence objects
    print("Converting to EvaluationSequence objects...")
    sequences = []

    for turn_count, sequence_list in sorted(benign_by_turn_count.items()):
        for seq_data in sequence_list:
            defense_id = seq_data['defense_id']
            attacks = seq_data['attacks']

            # Extract turns (user inputs only - this is what gets evaluated)
            turns = [attack['attacker_input'] for attack in attacks]

            # Create EvaluationSequence
            sequence = EvaluationSequence(
                attack_id=f"tensortrust_{defense_id}",
                label=AttackLabel.BENIGN,
                source_dataset=SourceDataset.TENSORTRUST,
                turns=turns,
                metadata={
                    'defense_id': defense_id,
                    'opening_defense': attacks[0]['opening_defense'],
                    'access_code': attacks[0]['access_code'],
                    'llm_model': attacks[0]['llm_choice'],
                    'extraction_keywords': EXTRACTION_KEYWORDS,
                    'filter_criteria': 'output_is_access_granted==False AND no_extraction_keywords',
                    'extraction_date': datetime.utcnow().isoformat(),
                    'source_file': str(data_path)
                }
            )

            sequences.append(sequence)

    print(f"✓ Created {len(sequences)} EvaluationSequence objects")
    print()

    return sequences


def extract_sharegpt_sequences() -> List[EvaluationSequence]:
    """
    Extract benign sequences from ShareGPT.

    Note: ShareGPT download not implemented. Returns empty list with message.

    Returns:
        Empty list (ShareGPT extraction not implemented)
    """
    print("=" * 80)
    print("EXTRACTING SHAREGPT BENIGN SEQUENCES")
    print("=" * 80)
    print("⚠ ShareGPT download not implemented - skipping")
    print("  Recommendation: Manually download ShareGPT subset if needed")
    print()

    return []


def insert_sequences_to_db(sequences: List[EvaluationSequence]) -> int:
    """
    Insert EvaluationSequence objects to ArangoDB.

    Idempotent via _key=attack_id (uses insert_ignore pattern).

    Args:
        sequences: List of EvaluationSequence objects

    Returns:
        Number of sequences inserted (excludes duplicates)
    """
    print("=" * 80)
    print("INSERTING SEQUENCES TO ARANGODB")
    print("=" * 80)

    db = get_client().get_database()
    collection = db.collection('phase3_evaluation_sequences')

    inserted = 0
    duplicates = 0

    for sequence in sequences:
        # Convert Pydantic model to dict
        doc = sequence.model_dump()

        # Use attack_id as _key for idempotency
        doc['_key'] = sequence.attack_id

        # Convert datetime to ISO string
        if 'created_at' in doc:
            doc['created_at'] = doc['created_at'].isoformat()

        try:
            collection.insert(doc)
            inserted += 1

            if inserted % 10 == 0:
                print(f"  Inserted {inserted} sequences...")

        except Exception as e:
            if 'unique constraint violated' in str(e).lower():
                duplicates += 1
            else:
                print(f"✗ Error inserting {sequence.attack_id}: {e}")
                raise

    print()
    print(f"✓ Inserted {inserted} sequences")
    if duplicates > 0:
        print(f"  ⚠ Skipped {duplicates} duplicates")
    print()

    return inserted


def verify_extraction():
    """Verify extraction results in ArangoDB."""
    print("=" * 80)
    print("VERIFICATION")
    print("=" * 80)

    db = get_client().get_database()

    # Query sequences by source and label
    result = db.aql.execute('''
        FOR doc IN phase3_evaluation_sequences
          FILTER doc.label == 'benign'
          COLLECT source = doc.source_dataset WITH COUNT INTO count
          SORT source
          RETURN {
            source: source,
            count: count
          }
    ''')

    sources = list(result)
    total = sum(s['count'] for s in sources)

    print(f"Total benign sequences: {total}")
    for source_data in sources:
        print(f"  {source_data['source']}: {source_data['count']}")

    print()

    # Query turn count distribution
    result = db.aql.execute('''
        FOR doc IN phase3_evaluation_sequences
          FILTER doc.label == 'benign'
          FILTER doc.source_dataset == 'tensortrust'
          LET turn_count = LENGTH(doc.turns)
          COLLECT turns = turn_count WITH COUNT INTO count
          SORT turns
          RETURN {
            turns: turns,
            count: count
          }
    ''')

    print("TensorTrust turn count distribution:")
    for turn_data in result:
        print(f"  {turn_data['turns']}-turn: {turn_data['count']} sequences")

    print()
    print("=" * 80)


def main():
    """Main extraction pipeline."""
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "BENIGN SEQUENCE EXTRACTION" + " " * 32 + "║")
    print("║" + " " * 28 + "Task T006" + " " * 42 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    # Provenance logging
    print("PROVENANCE")
    print("-" * 80)
    print(f"Extraction date: {datetime.utcnow().isoformat()}")
    print(f"TensorTrust source: {TENSORTRUST_DATA_PATH}")
    print(f"TensorTrust filter: output_is_access_granted==False AND no_extraction_keywords")
    print(f"Extraction keywords: {EXTRACTION_KEYWORDS}")
    print(f"Sampling strategy: Stratified by turn count")
    print(f"Sampling targets: {SAMPLING_TARGETS}")
    print()

    # Extract TensorTrust sequences
    tensortrust_sequences = extract_tensortrust_sequences(
        data_path=TENSORTRUST_DATA_PATH,
        sampling_targets=SAMPLING_TARGETS
    )

    # Extract ShareGPT sequences (not implemented)
    sharegpt_sequences = extract_sharegpt_sequences()

    # Combine sequences
    all_sequences = tensortrust_sequences + sharegpt_sequences

    # Insert to database
    inserted = insert_sequences_to_db(all_sequences)

    # Verify
    verify_extraction()

    # Summary
    print("=" * 80)
    print("✓ EXTRACTION COMPLETE")
    print("=" * 80)
    print(f"Total sequences extracted: {len(all_sequences)}")
    print(f"  TensorTrust: {len(tensortrust_sequences)}")
    print(f"  ShareGPT: {len(sharegpt_sequences)}")
    print(f"Total sequences inserted: {inserted}")
    print()


if __name__ == '__main__':
    main()
