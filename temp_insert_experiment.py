"""
Create experiment configuration for v2.1-d validation
"""

from src.database.client import get_client

def insert_experiment():
    """Insert experiment configuration for v2.1-d"""
    db = get_client().get_database()

    experiment = {
        '_key': 'exp_phase2b_v2.1-d_composition_aware',
        'experiment_id': 'exp_phase2b_v2.1-d_composition_aware',
        'variant': 'v2.1-d',
        'phase': 'phase2b',
        'description': 'Test v2.1-d (context integrity + explicit composition rules) on 4 attacks where v2.1-c showed negative interaction',
        'observer_model': 'anthropic/claude-haiku-4.5',
        'hypothesis': 'Explicit composition rules will prevent negative interaction seen in v2.1-c',
        'test_set': ['alignment_lab_extract_2', 'alignment_lab_extract_26', 'alignment_lab_extract_27', 'alignment_lab_extract_16'],
        'created_date': '2025-11-12',
        'status': 'pending'
    }

    print(f"Inserting experiment configuration...")

    try:
        db.collection('experiments').insert(experiment)
        print(f"✓ Successfully inserted {experiment['_key']}")
    except Exception as e:
        if 'unique constraint violated' in str(e).lower():
            print(f"⚠ {experiment['_key']} already exists, updating...")
            db.collection('experiments').update({'_key': experiment['_key']}, experiment)
            print(f"✓ Updated {experiment['_key']}")
        else:
            raise

    # Verify
    result = db.aql.execute('''
        FOR doc IN experiments
          FILTER doc._key == 'exp_phase2b_v2.1-d_composition_aware'
          RETURN doc
    ''')

    exps = list(result)
    if exps:
        print(f"\n✓ Verification successful:")
        print(f"  Experiment ID: {exps[0]['experiment_id']}")
        print(f"  Variant: {exps[0]['variant']}")
        print(f"  Observer model: {exps[0]['observer_model']}")
        print(f"  Test set size: {len(exps[0]['test_set'])}")
    else:
        print(f"\n✗ Verification failed")

if __name__ == '__main__':
    insert_experiment()
