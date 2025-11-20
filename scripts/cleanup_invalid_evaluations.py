#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Delete evaluations that used incorrect observer model.

These experiment_ids used anthropic/claude-3.5-haiku instead of approved
anthropic/claude-haiku-4.5:
- exp_phase3a_mvp (10 sequences, stateless)
- exp_phase3a_cumulative (50 sequences, cumulative context)
- exp_phase3a_stateless_50 (partial, killed before completion)
"""

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

    invalid_experiment_ids = [
        "exp_phase3a_mvp",
        "exp_phase3a_cumulative",
        "exp_phase3a_stateless_50",
    ]

    print("\n" + "=" * 60)
    print("Cleanup: Delete Invalid Evaluations")
    print("=" * 60)
    print("\nReason: Used anthropic/claude-3.5-haiku instead of")
    print("        approved anthropic/claude-haiku-4.5\n")

    # Delete from phase3_principle_evaluations
    eval_coll = db.collection("phase3_principle_evaluations")

    total_deleted = 0
    for exp_id in invalid_experiment_ids:
        # Use AQL to delete documents
        query = """
        FOR doc IN phase3_principle_evaluations
            FILTER doc.experiment_id == @exp_id
            REMOVE doc IN phase3_principle_evaluations
            RETURN OLD
        """
        cursor = db.aql.execute(query, bind_vars={"exp_id": exp_id})
        deleted = list(cursor)

        if deleted:
            count = len(deleted)
            total_deleted += count
            print(f">> Deleted {count} evaluations from {exp_id}")
        else:
            print(f">> No evaluations found for {exp_id}")

    # Delete from phase3_evaluation_sequences (sequence-level records)
    print()
    for exp_id in invalid_experiment_ids:
        query = """
        FOR doc IN phase3_evaluation_sequences
            FILTER doc.experiment_id == @exp_id
            REMOVE doc IN phase3_evaluation_sequences
            RETURN OLD
        """
        cursor = db.aql.execute(query, bind_vars={"exp_id": exp_id})
        deleted = list(cursor)

        if deleted:
            print(f">> Deleted {len(deleted)} sequences from {exp_id}")
        else:
            print(f">> No sequences found for {exp_id}")

    print("\n" + "=" * 60)
    print("Cleanup complete")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
