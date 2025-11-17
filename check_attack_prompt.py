"""Check what an attack prompt actually looks like."""

import sys
from src.database.client import get_client


def main():
    db_client = get_client()
    db = db_client.get_database()

    attack_id = 'alignment_lab_extract_12'

    query = """
    FOR attack IN attacks
      FILTER attack._key == @attack_id
      RETURN attack.prompt_text
    """
    results = list(db.aql.execute(query, bind_vars={'attack_id': attack_id}))

    if results:
        print(f"Attack ID: {attack_id}")
        print("="*80)
        print(results[0])
        print("="*80)
        print(f"Length: {len(results[0])} chars")
    else:
        print(f"Attack {attack_id} not found")


if __name__ == '__main__':
    sys.exit(main())
