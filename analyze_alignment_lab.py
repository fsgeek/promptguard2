#!/usr/bin/env python3
"""Analyze alignment_lab attack detection failures."""

from src.database.client import DatabaseClient
import json

def main():
    # Connect to database
    client = DatabaseClient()
    db = client.get_database()
    evals = db.collection('step2_pre_evaluations')
    attacks = db.collection('attacks')

    # Get all alignment_lab evaluations
    alignment_lab_evals = [e for e in evals.all()
                            if 'alignment_lab' in e.get('attack_id', '')]

    print(f"Total alignment_lab evaluations: {len(alignment_lab_evals)}")

    # Split by detection
    detected = [e for e in alignment_lab_evals if e.get('detected', False)]
    not_detected = [e for e in alignment_lab_evals if not e.get('detected', False)]

    print(f"Detected: {len(detected)}")
    print(f"Not detected: {len(not_detected)}")
    print(f"Detection rate: {len(detected)/len(alignment_lab_evals)*100:.1f}%")

    # Analyze not detected cases
    analysis_data = []

    for i, eval_doc in enumerate(not_detected[:15]):  # Sample 15 for thorough analysis
        attack_doc = attacks.get(eval_doc['attack_id'])

        analysis_entry = {
            'attack_id': eval_doc['attack_id'],
            'neutrosophic_scores': eval_doc.get('neutrosophic_scores', {}),
            'prompt_text': attack_doc.get('prompt_text', ''),
            'observer_reasoning': eval_doc.get('observer_reasoning', ''),
            'attack_metadata': attack_doc.get('metadata', {})
        }
        analysis_data.append(analysis_entry)

        print(f"\n{'='*80}")
        print(f"CASE {i+1}: {eval_doc['attack_id']}")
        print(f"{'='*80}")
        print(f"F score: {eval_doc.get('neutrosophic_scores', {}).get('F', 0):.3f}")
        print(f"T score: {eval_doc.get('neutrosophic_scores', {}).get('T', 0):.3f}")
        print(f"I score: {eval_doc.get('neutrosophic_scores', {}).get('I', 0):.3f}")
        print(f"\nPROMPT:")
        print(attack_doc.get('prompt_text', '')[:400])
        print(f"\nOBSERVER REASONING:")
        print(eval_doc.get('observer_reasoning', '')[:500])

    # Save detailed analysis data
    with open('alignment_lab_failures_data.json', 'w') as f:
        json.dump(analysis_data, f, indent=2)

    print(f"\n\nSaved detailed data to alignment_lab_failures_data.json")

    # Calculate average scores
    avg_F = sum(e.get('neutrosophic_scores', {}).get('F', 0) for e in not_detected) / len(not_detected)
    avg_T = sum(e.get('neutrosophic_scores', {}).get('T', 0) for e in not_detected) / len(not_detected)
    avg_I = sum(e.get('neutrosophic_scores', {}).get('I', 0) for e in not_detected) / len(not_detected)

    print(f"\n\nAVERAGE SCORES FOR UNDETECTED ATTACKS:")
    print(f"F (Falsity): {avg_F:.3f}")
    print(f"T (Truth): {avg_T:.3f}")
    print(f"I (Indeterminacy): {avg_I:.3f}")

if __name__ == '__main__':
    main()
