#!/usr/bin/env python3
"""Analyze the 6 alignment_lab attacks that WERE detected."""

from src.database.client import DatabaseClient
import json

def main():
    # Connect to database
    client = DatabaseClient()
    db = client.get_database()
    evals = db.collection('step2_pre_evaluations')
    attacks = db.collection('attacks')

    # Get detected alignment_lab evaluations
    alignment_lab_evals = [e for e in evals.all()
                            if 'alignment_lab' in e.get('attack_id', '')]

    detected = [e for e in alignment_lab_evals if e.get('detected', False)]

    print(f"Total detected: {len(detected)}\n")

    # Analyze detected cases
    for i, eval_doc in enumerate(detected):
        attack_doc = attacks.get(eval_doc['attack_id'])

        print(f"\n{'='*80}")
        print(f"DETECTED CASE {i+1}: {eval_doc['attack_id']}")
        print(f"{'='*80}")
        print(f"F score: {eval_doc.get('neutrosophic_scores', {}).get('F', 0):.3f}")
        print(f"T score: {eval_doc.get('neutrosophic_scores', {}).get('T', 0):.3f}")
        print(f"I score: {eval_doc.get('neutrosophic_scores', {}).get('I', 0):.3f}")
        print(f"\nPROMPT:")
        print(attack_doc.get('prompt_text', '')[:400])
        print(f"\nOBSERVER REASONING:")
        print(eval_doc.get('observer_reasoning', '')[:500])

if __name__ == '__main__':
    main()
