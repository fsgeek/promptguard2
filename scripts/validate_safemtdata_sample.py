#!/usr/bin/env python3
"""
Validate SafeMTData sample for synthetic artifacts and labeling quality.

Phase 2 lesson: benign_malicious had flawed synthetic labeling.
This script checks for common synthetic data issues before extensive use.
"""

import pandas as pd
import json

print("="*80)
print("SafeMTData Synthetic Data Validation")
print("="*80)
print()

# Load Attack_600
print("Loading Attack_600 dataset...")
attack_600 = pd.read_parquet('data/raw_datasets/safemtdata/attack_600.parquet')

print(f"Total sequences: {len(attack_600)}")
print()
print("Columns:", attack_600.columns.tolist())
print()

# Inspect first sequence
print("="*80)
print("SAMPLE SEQUENCE 1 (Full Detail)")
print("="*80)
sample = attack_600.iloc[0]

for col in attack_600.columns:
    print(f"\n{col}:")
    print("-" * 40)
    value = sample[col]
    if isinstance(value, (list, dict)):
        print(json.dumps(value, indent=2)[:500] + ("..." if len(str(value)) > 500 else ""))
    else:
        print(str(value)[:500] + ("..." if len(str(value)) > 500 else ""))

# Check for multi-turn structure
print("\n" + "="*80)
print("MULTI-TURN STRUCTURE VALIDATION")
print("="*80)

# Try to identify conversation columns
conversation_cols = [col for col in attack_600.columns if 'conversation' in col.lower() or 'turn' in col.lower() or 'message' in col.lower()]
print(f"\nConversation-related columns: {conversation_cols}")

if conversation_cols:
    for col in conversation_cols:
        sample_val = attack_600[col].iloc[0]
        if isinstance(sample_val, list):
            print(f"\n{col}: {len(sample_val)} turns in first sequence")
            if len(sample_val) > 0:
                print(f"  Turn 1: {str(sample_val[0])[:200]}...")

# Statistics
print("\n" + "="*80)
print("DATASET STATISTICS")
print("="*80)

# Check for turn counts if we can identify them
for col in attack_600.columns:
    sample_val = attack_600[col].iloc[0]
    if isinstance(sample_val, list):
        turn_counts = attack_600[col].apply(lambda x: len(x) if isinstance(x, list) else 0)
        print(f"\n{col}:")
        print(f"  Mean turns: {turn_counts.mean():.2f}")
        print(f"  Min turns: {turn_counts.min()}")
        print(f"  Max turns: {turn_counts.max()}")

# Sample 5 random sequences for manual review
print("\n" + "="*80)
print("5 RANDOM SEQUENCES FOR MANUAL REVIEW")
print("="*80)

samples = attack_600.sample(5, random_state=42)

for idx, (i, row) in enumerate(samples.iterrows(), 1):
    print(f"\n--- Sample {idx} (Index {i}) ---")

    # Try to show conversation if exists
    for col in conversation_cols:
        if col in row.index:
            conv = row[col]
            if isinstance(conv, list) and len(conv) > 0:
                print(f"\n{col} ({len(conv)} turns):")
                for turn_idx, turn in enumerate(conv[:3], 1):  # Show first 3 turns
                    print(f"  Turn {turn_idx}: {str(turn)[:150]}...")
                if len(conv) > 3:
                    print(f"  ... ({len(conv) - 3} more turns)")

print("\n" + "="*80)
print("VALIDATION CHECKLIST")
print("="*80)
print("""
Manual Review Required:

[ ] Do conversations look natural or formulaic?
[ ] Are turn transitions realistic (gradual escalation)?
[ ] Do ground truth labels make sense?
[ ] Any obvious synthetic artifacts (repetitive patterns)?
[ ] Are harmful goals clearly defined?
[ ] Do attack paths vary or follow templates?

Compare with Phase 2 Issues:
- benign_malicious: Had borderline cases mislabeled as benign
- Check: Are attack sequences genuinely adversarial?

Next Steps:
1. Review 10-20 sequences manually
2. Compare with MHJ (real-world) when available
3. If validation passes, use for Phase 3 TrustEMA testing
""")
