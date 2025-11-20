#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check status of comparison experiments."""

import os
from arango import ArangoClient
from collections import Counter


def main():
    # Connect to ArangoDB
    host = os.getenv("ARANGO_HOST", "http://192.168.111.125:8529")
    client = ArangoClient(hosts=host)
    db = client.db(
        os.getenv("ARANGO_DB", "PromptGuard2"),
        username=os.getenv("ARANGO_USER", "pgtest"),
        password=os.getenv("ARANGODB_PROMPTGUARD_PASSWORD"),
    )

    coll = db.collection("phase3_principle_evaluations")

    for exp_id in ["exp_phase3a_stateless_50", "exp_phase3a_cumulative"]:
        evals = list(coll.find({"experiment_id": exp_id}))
        print(f"\n{exp_id}:")
        print(f"  Total evaluations: {len(evals)}")

        if evals:
            # Count by attack_id
            attack_counts = Counter(e["attack_id"] for e in evals)
            print(f"  Unique sequences: {len(attack_counts)}")
            print(f"  Sequences with 5 turns: {sum(1 for c in attack_counts.values() if c == 5)}")
            print(f"  Sequences with 4 turns: {sum(1 for c in attack_counts.values() if c == 4)}")
            print(f"  Sequences with < 4 turns: {sum(1 for c in attack_counts.values() if c < 4)}")


if __name__ == "__main__":
    main()
