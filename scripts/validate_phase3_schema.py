#!/usr/bin/env python3
"""
Validate Phase 3 schema against 50 real examples.

Tests:
1. Can we instantiate EvaluationSequence from XGuard-Train?
2. Can we instantiate EvaluationSequence from MHJ?
3. Does the schema support composability (multiple principles)?
4. Can we run pattern analysis queries on the structure?
"""

import pandas as pd
import json
from pathlib import Path
from typing import List
from datetime import datetime

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.schemas.phase3_evaluation import (
    EvaluationSequence,
    PrincipleEvaluation,
    NeutrosophicScore,
    AttackLabel,
    SourceDataset,
    EvaluationPrinciple
)


def load_xguard_sample(n: int = 25) -> List[EvaluationSequence]:
    """Load n examples from XGuard-Train (SafeMTData)."""
    print(f"\n{'='*80}")
    print(f"Loading {n} examples from XGuard-Train...")
    print(f"{'='*80}")

    df = pd.read_parquet('data/raw_datasets/safemtdata/attack_600.parquet')
    samples = df.sample(n, random_state=42)

    sequences = []
    for idx, row in samples.iterrows():
        # XGuard structure: multi_turn_queries = list of strings
        turns = row['multi_turn_queries']

        seq = EvaluationSequence(
            attack_id=f"xguard_{row['id']}",
            label=AttackLabel.JAILBREAK,  # All are attacks in attack_600
            source_dataset=SourceDataset.XGUARD_TRAIN,
            turns=turns,
            metadata={
                "category": row.get('category', 'unknown'),
                "plain_goal": row.get('plain_query', ''),
                "actor_name": row.get('actor_name', ''),
                "relationship": row.get('relationship', '')
            }
        )
        sequences.append(seq)

        # Print first example details
        if len(sequences) == 1:
            print(f"\nFirst XGuard example:")
            print(f"  ID: {seq.attack_id}")
            print(f"  Label: {seq.label}")
            print(f"  Turns: {len(seq.turns)}")
            print(f"  Category: {seq.metadata['category']}")
            print(f"  First turn: {seq.turns[0][:80]}...")
            print(f"  Plain goal: {seq.metadata['plain_goal'][:80]}...")

    print(f"\n✅ Successfully loaded {len(sequences)} XGuard sequences")
    return sequences


def load_mhj_sample(n: int = 25) -> List[EvaluationSequence]:
    """Load n examples from MHJ (Scale AI human red-team)."""
    print(f"\n{'='*80}")
    print(f"Loading {n} examples from MHJ...")
    print(f"{'='*80}")

    df = pd.read_csv('data/raw_datasets/MHJ/harmbench_behaviors.csv')
    samples = df.sample(n, random_state=42)

    sequences = []
    for idx, row in samples.iterrows():
        # MHJ structure: message_0, message_1, ... message_N
        # Each message is JSON: {"role": "user/assistant", "body": "text"}
        turns = []
        for col in df.columns:
            if col.startswith('message_'):
                msg = row[col]
                if pd.notna(msg) and msg:
                    try:
                        msg_obj = json.loads(msg)
                        if msg_obj.get('role') == 'user':
                            turns.append(msg_obj['body'])
                    except (json.JSONDecodeError, TypeError):
                        continue

        if not turns:
            continue

        seq = EvaluationSequence(
            attack_id=f"mhj_{row.get('question_id', idx)}",
            label=AttackLabel.JAILBREAK,  # All are successful jailbreaks
            source_dataset=SourceDataset.MHJ,
            turns=turns,
            metadata={
                "tactic": row.get('tactic', 'unknown'),
                "source": row.get('Source', ''),
                "temperature": row.get('temperature', None),
                "time_spent": row.get('time_spent', None),
                "submission_message": row.get('submission_message', '')
            }
        )
        sequences.append(seq)

        # Print first example details
        if len(sequences) == 1:
            print(f"\nFirst MHJ example:")
            print(f"  ID: {seq.attack_id}")
            print(f"  Label: {seq.label}")
            print(f"  Turns: {len(seq.turns)}")
            print(f"  Tactic: {seq.metadata['tactic']}")
            print(f"  First turn: {seq.turns[0][:80]}...")

    print(f"\n✅ Successfully loaded {len(sequences)} MHJ sequences")
    return sequences


def test_principle_evaluation(sequences: List[EvaluationSequence]):
    """Test that we can create PrincipleEvaluation for multiple principles."""
    print(f"\n{'='*80}")
    print(f"Testing composability: Multiple principles per sequence")
    print(f"{'='*80}")

    # Take first sequence as example
    seq = sequences[0]

    evaluations = []

    # Simulate evaluating turn 1 with reciprocity principle
    eval1 = PrincipleEvaluation(
        attack_id=seq.attack_id,
        principle=EvaluationPrinciple.RECIPROCITY,
        turn_number=1,
        evaluator_model="anthropic/claude-3.5-sonnet",
        observer_prompt_version="v2.1-c",
        scores=NeutrosophicScore(T=0.85, I=0.10, F=0.05),
        reasoning="Initial turn appears benign - biographical question shows reciprocal intent.",
        raw_response="[Complete LLM response would be here]",
        model_temperature=0.0
    )
    evaluations.append(eval1)

    # Simulate evaluating turn 1 with context_integrity principle
    eval2 = PrincipleEvaluation(
        attack_id=seq.attack_id,
        principle=EvaluationPrinciple.CONTEXT_INTEGRITY,
        turn_number=1,
        evaluator_model="anthropic/claude-3.5-sonnet",
        observer_prompt_version="v2.1-c",
        scores=NeutrosophicScore(T=0.90, I=0.05, F=0.05),
        reasoning="No boundary violations detected in initial turn.",
        raw_response="[Complete LLM response would be here]",
        model_temperature=0.0
    )
    evaluations.append(eval2)

    # Simulate evaluating turn 3 with reciprocity (shows trajectory)
    eval3 = PrincipleEvaluation(
        attack_id=seq.attack_id,
        principle=EvaluationPrinciple.RECIPROCITY,
        turn_number=3,
        evaluator_model="anthropic/claude-3.5-sonnet",
        observer_prompt_version="v2.1-c",
        scores=NeutrosophicScore(T=0.70, I=0.20, F=0.10),
        reasoning="Request framing shifting - technical questions now probing safety boundaries.",
        raw_response="[Complete LLM response would be here]",
        model_temperature=0.0
    )
    evaluations.append(eval3)

    print(f"\n✅ Created {len(evaluations)} principle evaluations")
    print(f"\nEvaluation breakdown:")
    print(f"  - {seq.attack_id} × reciprocity × turn 1: F={eval1.scores.F:.2f}")
    print(f"  - {seq.attack_id} × context_integrity × turn 1: F={eval2.scores.F:.2f}")
    print(f"  - {seq.attack_id} × reciprocity × turn 3: F={eval3.scores.F:.2f}")
    print(f"\nTrajectory visible: reciprocity F increased from 0.05 → 0.10 (turn 1 → 3)")

    return evaluations


def test_pattern_analysis(sequences: List[EvaluationSequence],
                         evaluations: List[PrincipleEvaluation]):
    """Test that schema enables pattern analysis queries."""
    print(f"\n{'='*80}")
    print(f"Testing pattern analysis capabilities")
    print(f"{'='*80}")

    # Query 1: Find sequences by label
    jailbreaks = [s for s in sequences if s.label == AttackLabel.JAILBREAK]
    print(f"\n1. Filter by label: {len(jailbreaks)} jailbreaks found")

    # Query 2: Find sequences by turn count
    long_sequences = [s for s in sequences if len(s.turns) > 6]
    print(f"2. Filter by turns: {len(long_sequences)} sequences with >6 turns")

    # Query 3: Find sequences by source
    xguard_seqs = [s for s in sequences if s.source_dataset == SourceDataset.XGUARD_TRAIN]
    mhj_seqs = [s for s in sequences if s.source_dataset == SourceDataset.MHJ]
    print(f"3. Filter by source: {len(xguard_seqs)} XGuard, {len(mhj_seqs)} MHJ")

    # Query 4: Cross-dataset category comparison
    categories = {}
    for seq in sequences:
        cat = seq.metadata.get('category') or seq.metadata.get('tactic', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1
    print(f"\n4. Category distribution:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1])[:5]:
        print(f"   - {cat}: {count}")

    # Query 5: Trajectory analysis (mock - would need more evaluations)
    if evaluations:
        attack_id = evaluations[0].attack_id
        principle = EvaluationPrinciple.RECIPROCITY
        trajectory = [
            (e.turn_number, e.scores.F)
            for e in evaluations
            if e.attack_id == attack_id and e.principle == principle
        ]
        trajectory.sort()
        print(f"\n5. Trajectory for {attack_id} (reciprocity):")
        for turn, f_score in trajectory:
            print(f"   - Turn {turn}: F={f_score:.2f}")

    print(f"\n✅ Pattern analysis queries successful")


def main():
    """Run schema validation on 50 examples."""
    print("="*80)
    print("Phase 3 Schema Validation")
    print("="*80)
    print(f"Testing schema on 50 real examples (25 XGuard + 25 MHJ)")

    # Load datasets
    xguard_sequences = load_xguard_sample(25)
    mhj_sequences = load_mhj_sample(25)

    all_sequences = xguard_sequences + mhj_sequences
    print(f"\n{'='*80}")
    print(f"Total sequences loaded: {len(all_sequences)}")
    print(f"{'='*80}")

    # Test composability
    evaluations = test_principle_evaluation(all_sequences)

    # Test pattern analysis
    test_pattern_analysis(all_sequences, evaluations)

    # Summary
    print(f"\n{'='*80}")
    print(f"VALIDATION RESULTS")
    print(f"{'='*80}")
    print(f"✅ EvaluationSequence instantiation: SUCCESS")
    print(f"✅ Composability (multiple principles): SUCCESS")
    print(f"✅ Pattern analysis queries: SUCCESS")
    print(f"\n📊 Schema Statistics:")

    total_turns = sum(len(s.turns) for s in all_sequences)
    avg_turns = total_turns / len(all_sequences)
    print(f"   - Total sequences: {len(all_sequences)}")
    print(f"   - Total turns: {total_turns}")
    print(f"   - Average turns/sequence: {avg_turns:.1f}")
    print(f"   - XGuard sequences: {len(xguard_sequences)}")
    print(f"   - MHJ sequences: {len(mhj_sequences)}")

    print(f"\n{'='*80}")
    print(f"NEXT STEPS")
    print(f"{'='*80}")
    print("""
1. ✅ Schema validated on 50 examples
2. ⏸️  Migrate to ArangoDB collections
3. ⏸️  Implement evaluation pipeline (populate PrincipleEvaluation)
4. ⏸️  Build trajectory analysis queries
5. ⏸️  Write Phase 3 spec.md
""")


if __name__ == "__main__":
    main()
