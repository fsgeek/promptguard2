#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analyze stateless vs cumulative context evaluation comparison.

Research Question: Does cumulative context produce richer temporal trajectories
that reveal attack patterns better than stateless evaluation?
"""

import os
import numpy as np
from collections import defaultdict
from arango import ArangoClient


def main():
    # Connect to ArangoDB
    host = os.getenv("ARANGO_HOST", "http://192.168.111.125:8529")
    client = ArangoClient(hosts=host)
    db = client.db(
        os.getenv("ARANGO_DB", "PromptGuard2"),
        username=os.getenv("ARANGO_USER", "pgtest"),
        password=os.getenv("ARANGODB_PROMPTGUARD_PASSWORD"),
    )

    # Load both datasets
    print("Loading evaluation data...")
    print()

    stateless_query = """
    FOR doc IN phase3_principle_evaluations
        FILTER doc.experiment_id == @exp_id
        SORT doc.attack_id, doc.turn_number
        RETURN {
            attack_id: doc.attack_id,
            turn: doc.turn_number,
            T: doc.scores.T,
            I: doc.scores.I,
            F: doc.scores.F
        }
    """

    stateless_data = list(db.aql.execute(
        stateless_query,
        bind_vars={"exp_id": "exp_phase3a_stateless_50"}
    ))

    cumulative_data = list(db.aql.execute(
        stateless_query,
        bind_vars={"exp_id": "exp_phase3a_cumulative"}
    ))

    print(f"Stateless:   {len(stateless_data)} evaluations")
    print(f"Cumulative:  {len(cumulative_data)} evaluations")
    print()

    # Organize by attack and turn
    def organize_by_trajectory(data):
        trajectories = defaultdict(dict)
        for doc in data:
            attack_id = doc['attack_id']
            turn = doc['turn']
            trajectories[attack_id][turn] = (doc['T'], doc['I'], doc['F'])
        return trajectories

    stateless_traj = organize_by_trajectory(stateless_data)
    cumulative_traj = organize_by_trajectory(cumulative_data)

    # Analysis 1: F-score distributions by turn
    print("=" * 70)
    print("ANALYSIS 1: F-Score Distribution by Turn")
    print("=" * 70)
    print()

    for mode_name, trajectories in [("Stateless", stateless_traj), ("Cumulative", cumulative_traj)]:
        print(f"{mode_name}:")
        turn_f_scores = defaultdict(list)

        for attack_id, turns in trajectories.items():
            for turn_num, (T, I, F) in turns.items():
                turn_f_scores[turn_num].append(F)

        for turn_num in sorted(turn_f_scores.keys()):
            f_values = turn_f_scores[turn_num]
            print(f"  Turn {turn_num}: mean={np.mean(f_values):.3f}, "
                  f"std={np.std(f_values):.3f}, "
                  f"max={np.max(f_values):.3f}, "
                  f"n={len(f_values)}")
        print()

    # Analysis 2: F-score temporal derivatives (dF/dt)
    print("=" * 70)
    print("ANALYSIS 2: Temporal Dynamics (F-Score Changes)")
    print("=" * 70)
    print()

    for mode_name, trajectories in [("Stateless", stateless_traj), ("Cumulative", cumulative_traj)]:
        print(f"{mode_name}:")

        f_increases = []  # Turn-over-turn F increases
        f_decreases = []  # Turn-over-turn F decreases

        for attack_id, turns in trajectories.items():
            sorted_turns = sorted(turns.keys())
            for i in range(len(sorted_turns) - 1):
                t1, t2 = sorted_turns[i], sorted_turns[i+1]
                F1 = turns[t1][2]
                F2 = turns[t2][2]
                delta_f = F2 - F1

                if delta_f > 0:
                    f_increases.append(delta_f)
                elif delta_f < 0:
                    f_decreases.append(delta_f)

        print(f"  F increases: n={len(f_increases)}, "
              f"mean={np.mean(f_increases) if f_increases else 0:.3f}, "
              f"max={np.max(f_increases) if f_increases else 0:.3f}")
        print(f"  F decreases: n={len(f_decreases)}, "
              f"mean={np.mean(f_decreases) if f_decreases else 0:.3f}, "
              f"min={np.min(f_decreases) if f_decreases else 0:.3f}")
        print()

    # Analysis 3: Direct comparison on same sequences
    print("=" * 70)
    print("ANALYSIS 3: Per-Sequence Comparison (Stateless vs Cumulative)")
    print("=" * 70)
    print()

    common_attacks = set(stateless_traj.keys()) & set(cumulative_traj.keys())
    print(f"Analyzing {len(common_attacks)} common sequences...")
    print()

    big_diffs = []  # (attack_id, turn, stateless_F, cumulative_F, diff)

    for attack_id in sorted(common_attacks):
        stat_turns = stateless_traj[attack_id]
        cum_turns = cumulative_traj[attack_id]

        common_turns = set(stat_turns.keys()) & set(cum_turns.keys())

        for turn in sorted(common_turns):
            stat_F = stat_turns[turn][2]
            cum_F = cum_turns[turn][2]
            diff = cum_F - stat_F

            if abs(diff) > 0.2:  # Significant difference
                big_diffs.append((attack_id, turn, stat_F, cum_F, diff))

    if big_diffs:
        print(f"Found {len(big_diffs)} turns with |ΔF| > 0.2:")
        print()
        for attack_id, turn, stat_F, cum_F, diff in sorted(big_diffs, key=lambda x: abs(x[4]), reverse=True)[:10]:
            direction = "↑" if diff > 0 else "↓"
            print(f"  {attack_id} turn {turn}: {stat_F:.3f} → {cum_F:.3f} ({diff:+.3f}) {direction}")
    else:
        print("No significant differences (|ΔF| > 0.2) found between modes.")

    print()

    # Analysis 4: Pattern richness (variance in trajectories)
    print("=" * 70)
    print("ANALYSIS 4: Trajectory Richness (F-Score Variance)")
    print("=" * 70)
    print()

    for mode_name, trajectories in [("Stateless", stateless_traj), ("Cumulative", cumulative_traj)]:
        variances = []

        for attack_id, turns in trajectories.items():
            f_scores = [turns[t][2] for t in sorted(turns.keys())]
            if len(f_scores) > 1:
                variances.append(np.var(f_scores))

        print(f"{mode_name}:")
        print(f"  Mean trajectory variance: {np.mean(variances):.4f}")
        print(f"  Std trajectory variance:  {np.std(variances):.4f}")
        print(f"  Max trajectory variance:  {np.max(variances):.4f}")
        print()

    print("=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print()
    print("Based on these analyses, we can determine whether cumulative context")
    print("produces meaningfully different patterns that would aid Phase 5 discovery.")
    print()


if __name__ == "__main__":
    main()
