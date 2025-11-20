#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create unique index on phase3_principle_evaluations to prevent duplicate experiments."""

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

    coll = db.collection("phase3_principle_evaluations")

    # Create unique hash index on the logical uniqueness constraint
    print("Creating unique index on (experiment_id, attack_id, principle, turn_number)...")

    try:
        index = coll.add_hash_index(
            fields=["experiment_id", "attack_id", "principle", "turn_number"],
            unique=True,
            name="unique_evaluation",
        )
        print(f"✓ Index created: {index}")
        print(f"  Fields: experiment_id, attack_id, principle, turn_number")
        print(f"  Unique: True")
        print(f"  Name: unique_evaluation")
    except Exception as e:
        if "duplicate" in str(e).lower() or "already exists" in str(e).lower():
            print(f"✓ Index already exists (this is fine)")
        else:
            print(f"✗ Error creating index: {e}")
            raise

    # List all indexes to verify
    print("\nAll indexes on phase3_principle_evaluations:")
    for idx in coll.indexes():
        if idx["type"] != "primary":  # Skip the automatic _key index
            print(f"  - {idx.get('name', idx['type'])}: {idx.get('fields', [])} (unique={idx.get('unique', False)})")


if __name__ == "__main__":
    main()
