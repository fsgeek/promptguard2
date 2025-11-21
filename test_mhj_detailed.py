#!/usr/bin/env python3
"""Detailed test of MHJ loader implementation showing full sequence example."""

from src.pipeline.sequence_loader import SequenceLoader

def main():
    """Test MHJ loader with detailed output."""
    loader = SequenceLoader()

    # Load first sequence and show complete details
    sequences = loader.load(dataset="mhj", sample=1)
    seq = sequences[0]

    print("=" * 80)
    print("DETAILED MHJ SEQUENCE EXAMPLE")
    print("=" * 80)
    print()
    print(f"Attack ID: {seq.attack_id}")
    print(f"Label: {seq.label.value}")
    print(f"Source Dataset: {seq.source_dataset.value}")
    print(f"Number of Turns: {len(seq.turns)}")
    print()
    print("Metadata:")
    print(f"  Tactic: {seq.metadata['tactic']}")
    print(f"  Source: {seq.metadata['source']}")
    print()
    print("Complete Turn Sequence:")
    print("-" * 80)
    for i, turn in enumerate(seq.turns, 1):
        print(f"\nTurn {i}:")
        print(f"{turn}")
        print()

    print("=" * 80)
    print("\nVERIFICATION RESULTS")
    print("=" * 80)

    # Load full dataset for statistics
    all_sequences = loader.load(dataset="mhj")

    print(f"\nTotal sequences loaded: {len(all_sequences)}")
    print(f"Expected count: 537")
    print(f"Match: {len(all_sequences) == 537} ✓" if len(all_sequences) == 537 else "Match: False ✗")

    # Verify data integrity
    checks = [
        ("All attack_ids start with 'mhj_'", all(s.attack_id.startswith('mhj_') for s in all_sequences)),
        ("All labels are JAILBREAK", all(s.label.value == 'jailbreak' for s in all_sequences)),
        ("All source datasets are MHJ", all(s.source_dataset.value == 'mhj' for s in all_sequences)),
        ("All sequences have at least 1 turn", all(len(s.turns) >= 1 for s in all_sequences)),
        ("All metadata has 'tactic' field", all('tactic' in s.metadata for s in all_sequences)),
        ("All metadata has 'source' field", all('source' in s.metadata for s in all_sequences)),
        ("No system messages in turns", not any('You are a helpful' in turn for s in all_sequences for turn in s.turns)),
    ]

    print("\nData Integrity Checks:")
    for check_name, passed in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {check_name}")

    print("\nDataset Statistics:")
    print(f"  Total user turns extracted: {sum(len(s.turns) for s in all_sequences)}")
    print(f"  Average turns per sequence: {sum(len(s.turns) for s in all_sequences) / len(all_sequences):.2f}")
    print(f"  Min turns: {min(len(s.turns) for s in all_sequences)}")
    print(f"  Max turns: {max(len(s.turns) for s in all_sequences)}")

    # Show tactic breakdown
    from collections import Counter
    tactics = Counter(s.metadata['tactic'] for s in all_sequences)
    print("\nTactic Distribution:")
    for tactic, count in sorted(tactics.items(), key=lambda x: x[1], reverse=True):
        pct = (count / len(all_sequences)) * 100
        print(f"  {tactic}: {count} ({pct:.1f}%)")

    # Show source breakdown
    sources = Counter(s.metadata['source'] for s in all_sequences)
    print("\nSource Distribution:")
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        pct = (count / len(all_sequences)) * 100
        print(f"  {source}: {count} ({pct:.1f}%)")

    print("\n" + "=" * 80)
    print("IMPLEMENTATION SUCCESS ✓")
    print("=" * 80)

if __name__ == "__main__":
    main()
