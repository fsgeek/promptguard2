#!/usr/bin/env python3
"""Test script for MHJ dataset loader."""

from src.pipeline.sequence_loader import SequenceLoader

def main():
    """Test loading MHJ sequences."""
    print("Testing MHJ loader with 5 sequences...")
    print("=" * 80)

    loader = SequenceLoader()
    sequences = loader.load(dataset="mhj", sample=5)

    print(f"\nLoaded {len(sequences)} sequences\n")

    for i, seq in enumerate(sequences, 1):
        print(f"Sequence {i}:")
        print(f"  attack_id: {seq.attack_id}")
        print(f"  label: {seq.label}")
        print(f"  source_dataset: {seq.source_dataset}")
        print(f"  num_turns: {len(seq.turns)}")
        print(f"  metadata: {seq.metadata}")
        print(f"\n  Turns:")
        for j, turn in enumerate(seq.turns, 1):
            # Truncate long turns for display
            display_turn = turn[:100] + "..." if len(turn) > 100 else turn
            print(f"    Turn {j}: {display_turn}")
        print("\n" + "-" * 80 + "\n")

    # Validation checks
    print("Validation:")
    print(f"  All sequences have attack_id starting with 'mhj_': {all(s.attack_id.startswith('mhj_') for s in sequences)}")
    print(f"  All sequences have JAILBREAK label: {all(s.label.value == 'jailbreak' for s in sequences)}")
    print(f"  All sequences have MHJ source: {all(s.source_dataset.value == 'mhj' for s in sequences)}")
    print(f"  All sequences have at least 1 turn: {all(len(s.turns) >= 1 for s in sequences)}")
    print(f"  All sequences have tactic metadata: {all('tactic' in s.metadata for s in sequences)}")
    print(f"  All sequences have source metadata: {all('source' in s.metadata for s in sequences)}")

    # Stats
    print(f"\nStatistics:")
    print(f"  Average turns per sequence: {sum(len(s.turns) for s in sequences) / len(sequences):.1f}")
    print(f"  Min turns: {min(len(s.turns) for s in sequences)}")
    print(f"  Max turns: {max(len(s.turns) for s in sequences)}")

    tactics = set(s.metadata['tactic'] for s in sequences)
    print(f"  Tactics: {tactics}")

    sources = set(s.metadata['source'] for s in sequences)
    print(f"  Sources: {sources}")

if __name__ == "__main__":
    main()
