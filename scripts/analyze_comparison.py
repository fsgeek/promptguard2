#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analyze stateless vs cumulative context comparison results."""

import os
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

    print("\n" + "=" * 60)
    print("Context Mode Comparison Analysis")
    print("=" * 60)
    print()

    # Get evaluations for both experiments
    coll = db.collection("phase3_principle_evaluations")

    stateless_evals = list(coll.find({"experiment_id": "exp_phase3a_stateless_50"}))
    cumulative_evals = list(coll.find({"experiment_id": "exp_phase3a_cumulative"}))

    print(f"Stateless evaluations: {len(stateless_evals)}")
    print(f"Cumulative evaluations: {len(cumulative_evals)}")
    print()

    # Compare F scores
    comparison_count = 0
    f_score_increases = 0
    f_score_decreases = 0
    total_f_delta = 0.0

    # Group by attack_id and turn_number
    stateless_by_turn = {}
    for eval in stateless_evals:
        key = (eval["attack_id"], eval["turn_number"])
        stateless_by_turn[key] = eval

    cumulative_by_turn = {}
    for eval in cumulative_evals:
        key = (eval["attack_id"], eval["turn_number"])
        cumulative_by_turn[key] = eval

    # Compare
    for key, stateless in stateless_by_turn.items():
        if key in cumulative_by_turn:
            cumulative = cumulative_by_turn[key]
            f_delta = cumulative["scores"]["F"] - stateless["scores"]["F"]
            total_f_delta += f_delta
            comparison_count += 1

            if f_delta > 0.05:  # Meaningful increase
                f_score_increases += 1
            elif f_delta < -0.05:  # Meaningful decrease
                f_score_decreases += 1

    if comparison_count > 0:
        avg_f_delta = total_f_delta / comparison_count
        print(f">> Comparisons: {comparison_count} turn evaluations")
        print(f">> Average ΔF: {avg_f_delta:+.3f}")
        print(f">> F increased: {f_score_increases} ({f_score_increases/comparison_count*100:.1f}%)")
        print(f">> F decreased: {f_score_decreases} ({f_score_decreases/comparison_count*100:.1f}%)")
        print(f">> F unchanged: {comparison_count - f_score_increases - f_score_decreases}")
        print()

        # Interpretation
        print("=" * 60)
        print("INTERPRETATION")
        print("=" * 60)
        if avg_f_delta > 0.1:
            print("✓ Cumulative context SIGNIFICANTLY increases F scores")
            print("  → Use cumulative context for full validation")
        elif avg_f_delta > 0.05:
            print("? Cumulative context MODERATELY increases F scores")
            print("  → Consider cumulative context, but effect is modest")
        elif avg_f_delta < -0.05:
            print("✗ Cumulative context DECREASES F scores (unexpected)")
            print("  → Use stateless evaluation")
        else:
            print("○ Cumulative context has NO SIGNIFICANT EFFECT")
            print("  → Use stateless evaluation (simpler, faster)")
        print("=" * 60)
        print()


if __name__ == "__main__":
    main()
