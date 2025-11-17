"""
Insert v2.1-d observer prompt variant into database

v2.1-d: Context integrity with explicit neutrosophic composition rules
- Based on v2.1-b (context integrity only)
- Adds formal composition rules section
- Tests hypothesis: negative interaction in v2.1-c due to incorrect composition logic
"""

from src.database.client import get_client

def insert_v2_1_d():
    """Insert v2.1-d prompt variant into database"""
    db = get_client().get_database()

    # Read the prompt text
    with open('temp_v2.1-d_prompt.txt', 'r') as f:
        prompt_text = f.read()

    # Create variant document
    variant = {
        '_key': 'v2.1-d_composition_aware',
        'version': 'v2.1-d',
        'prompt_text': prompt_text,
        'description': 'v2.1-b + explicit neutrosophic composition rules (tests composition logic hypothesis)',
        'variant_type': 'composition-aware',
        'diff_from_baseline': 'Added: Context Integrity Principle + Neutrosophic Composition Rules section',
        'requires_turn_number': False,
        'created_date': '2025-11-12',
        'phase': 'phase2b',
        'parent': 'v2.1-b',
        'hypothesis': 'Negative interaction in v2.1-c due to incorrect composition logic (conjunctive instead of disjunctive)',
        'experiment_id': 'exp_phase2b_v2.1-d_composition_aware'
    }

    print(f"Inserting v2.1-d into observer_prompts collection...")
    print(f"Prompt length: {len(prompt_text)} chars")

    try:
        db.collection('observer_prompts').insert(variant)
        print(f"✓ Successfully inserted {variant['_key']}")
    except Exception as e:
        if 'unique constraint violated' in str(e).lower():
            print(f"⚠ {variant['_key']} already exists, updating...")
            db.collection('observer_prompts').update({'_key': variant['_key']}, variant)
            print(f"✓ Updated {variant['_key']}")
        else:
            raise

    # Verify insertion
    result = db.aql.execute('''
        FOR doc IN observer_prompts
          FILTER doc._key == 'v2.1-d_composition_aware'
          RETURN {
            key: doc._key,
            version: doc.version,
            type: doc.variant_type,
            parent: doc.parent,
            len: LENGTH(doc.prompt_text)
          }
    ''')

    variants = list(result)
    if variants:
        print(f"\n✓ Verification successful:")
        v = variants[0]
        print(f"  Key: {v['key']}")
        print(f"  Version: {v['version']}")
        print(f"  Type: {v['type']}")
        print(f"  Parent: {v['parent']}")
        print(f"  Length: {v['len']} chars")
    else:
        print(f"\n✗ Verification failed - variant not found")

if __name__ == '__main__':
    insert_v2_1_d()
