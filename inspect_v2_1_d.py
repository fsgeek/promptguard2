"""Inspect v2.1-d observer prompt structure."""

import sys
import json
from src.database.client import get_client


def main():
    db_client = get_client()
    db = db_client.get_database()

    # Read v2.1-d prompt
    print("Reading v2.1-d prompt from database...")
    query = """
    FOR prompt IN observer_prompts
      FILTER prompt.version == 'v2.1-d'
      RETURN prompt
    """
    results = list(db.aql.execute(query))

    if not results:
        print("ERROR: v2.1-d prompt not found")
        return 1

    v2_1_d = results[0]
    print("\nDocument structure:")
    print(json.dumps(v2_1_d, indent=2))


if __name__ == '__main__':
    sys.exit(main())
