#!/usr/bin/env python3
"""
Download SafeMTData (XGuard-Train) multi-turn attack dataset.

Caution: Synthetic data - validate sample before using extensively.
Phase 2 lesson: benign_malicious had flawed synthetic labeling.
"""

from datasets import load_dataset
import os

print("Downloading SafeMTData (XGuard-Train)...")
print("This is synthetic data - manual validation required.")
print()

# Download Attack_600 subset (600 harmful behaviors, 3 attack paths each)
print("Downloading Attack_600 subset...")
attack_600 = load_dataset("SafeMTData/SafeMTData", 'Attack_600')

# Download SafeMTData_1K subset (1K safety alignment conversations)
print("Downloading SafeMTData_1K subset...")
safemtdata_1k = load_dataset("SafeMTData/SafeMTData", 'SafeMTData_1K')

# Save locally
os.makedirs('data/raw_datasets/safemtdata', exist_ok=True)

print("\nSaving Attack_600 to parquet...")
attack_600['Attack_600'].to_parquet('data/raw_datasets/safemtdata/attack_600.parquet')

print("Saving SafeMTData_1K to parquet...")
safemtdata_1k['SafeMTData_1K'].to_parquet('data/raw_datasets/safemtdata/safemtdata_1k.parquet')

print("\n" + "="*60)
print("DOWNLOAD COMPLETE")
print("="*60)
print(f"Attack_600: {len(attack_600['Attack_600'])} sequences")
print(f"SafeMTData_1K: {len(safemtdata_1k['SafeMTData_1K'])} sequences")
print()
print("⚠️  VALIDATION REQUIRED:")
print("  1. Manual review of 10-20 sample sequences")
print("  2. Check for synthetic artifacts")
print("  3. Verify ground truth labels make sense")
print("  4. Compare with real-world MHJ when available")
print()
print("Files saved to: data/raw_datasets/safemtdata/")
