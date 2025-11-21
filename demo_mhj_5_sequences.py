#!/usr/bin/env python3
"""Demonstration: Load 5 MHJ sequences as requested."""

from src.pipeline.sequence_loader import SequenceLoader

def main():
    """Load and display 5 MHJ sequences."""
    print("Loading 5 MHJ sequences...")
    print("=" * 80)

    loader = SequenceLoader()
    sequences = loader.load(dataset="mhj", sample=5)

    for i, seq in enumerate(sequences, 1):
        print(f"\nSEQUENCE {i}:")
        print(f"  attack_id: {seq.attack_id}")
        print(f"  label: {seq.label.value}")
        print(f"  source_dataset: {seq.source_dataset.value}")
        print(f"  turns: {len(seq.turns)}")
        print(f"  metadata: {seq.metadata}")
        print(f"\n  User turns:")
        for j, turn in enumerate(seq.turns, 1):
            # Show first 80 chars of each turn
            preview = turn[:80] + "..." if len(turn) > 80 else turn
            print(f"    [{j}] {preview}")
        print("-" * 80)

    print(f"\nSuccessfully loaded {len(sequences)} sequences from MHJ dataset")

if __name__ == "__main__":
    main()
