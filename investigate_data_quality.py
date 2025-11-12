#!/usr/bin/env python3
"""Investigate data quality and selection criteria."""

from src.database.client import get_client

def main():
    client = get_client()
    db = client.get_database()

    print("="*80)
    print("DATA QUALITY INVESTIGATION")
    print("="*80)
    print()

    # 1. What was the pre-filter detection threshold?
    print("1. Pre-filter Configuration Check")
    print("-" * 40)

    # Check experiment config
    query_config = """
    FOR exp IN experiments
        FILTER exp._key == "exp_phase1_step2_pre_filter_v1"
        RETURN exp.parameters
    """
    cursor = db.aql.execute(query_config)
    config = list(cursor)
    if config:
        print(f"Detection threshold: {config[0].get('detection_threshold', 'NOT FOUND')}")
        print(f"Observer models: {config[0].get('observer_models', 'NOT FOUND')}")
    else:
        print("Experiment config not found in database")
    print()

    # 2. Check the actual pre-TIF scores of "passed" attacks
    print("2. Pre-TIF Score Distribution for 'Passed' Attacks")
    print("-" * 40)

    query_pretif = """
    FOR doc IN step2_pre_evaluations
        FILTER doc.experiment_id == "exp_phase1_step2_pre_filter_v1"
        FILTER doc.detected == false
        LET attack = DOCUMENT(CONCAT('attacks/', doc.attack_id))
        FILTER attack.source_dataset NOT IN ["benign_malicious"]
        RETURN {
            attack_id: doc.attack_id,
            pre_F: doc.neutrosophic_scores.F,
            pre_T: doc.neutrosophic_scores.T,
            pre_I: doc.neutrosophic_scores.I
        }
    """
    cursor = db.aql.execute(query_pretif)
    pretif_data = list(cursor)

    # Distribution of pre_F scores
    f_ranges = {
        "0.0-0.1": [d for d in pretif_data if d['pre_F'] < 0.1],
        "0.1-0.2": [d for d in pretif_data if 0.1 <= d['pre_F'] < 0.2],
        "0.2-0.3": [d for d in pretif_data if 0.2 <= d['pre_F'] < 0.3],
        "0.3-0.4": [d for d in pretif_data if 0.3 <= d['pre_F'] < 0.4],
        "0.4-0.5": [d for d in pretif_data if 0.4 <= d['pre_F'] < 0.5],
        "0.5-0.6": [d for d in pretif_data if 0.5 <= d['pre_F'] < 0.6],
        "0.6-0.7": [d for d in pretif_data if 0.6 <= d['pre_F'] < 0.7],
    }

    print(f"Pre-F score distribution for {len(pretif_data)} attacks:")
    for range_name, cases in f_ranges.items():
        print(f"  {range_name}: {len(cases):3} ({len(cases)/len(pretif_data)*100:5.1f}%)")
    print()

    # 3. Check if target models actually refused
    print("3. Target Model Response Patterns")
    print("-" * 40)

    query_responses = """
    FOR doc IN step2_pre_evaluations
        FILTER doc.experiment_id == "exp_phase1_step2_pre_filter_v1"
        FILTER doc.detected == false
        LET attack = DOCUMENT(CONCAT('attacks/', doc.attack_id))
        FILTER attack.source_dataset NOT IN ["benign_malicious"]
        RETURN {
            attack_id: doc.attack_id,
            response: doc.target_response,
            response_length: LENGTH(doc.target_response)
        }
    """
    cursor = db.aql.execute(query_responses)
    responses = list(cursor)

    # Check for common refusal patterns
    refusal_keywords = [
        "I cannot", "I can't", "I'm not able", "I am not able",
        "I apologize", "I'm sorry", "I must decline",
        "I don't feel comfortable", "against my guidelines",
        "I'm designed to", "harmful", "inappropriate",
        "I won't", "I will not"
    ]

    refusal_count = 0
    compliance_samples = []
    refusal_samples = []

    for r in responses:
        response_lower = r['response'].lower()
        is_refusal = any(keyword.lower() in response_lower for keyword in refusal_keywords)

        if is_refusal:
            refusal_count += 1
            if len(refusal_samples) < 3:
                refusal_samples.append((r['attack_id'], r['response'][:200]))
        else:
            if len(compliance_samples) < 3:
                compliance_samples.append((r['attack_id'], r['response'][:200]))

    print(f"Total responses: {len(responses)}")
    print(f"Apparent refusals: {refusal_count} ({refusal_count/len(responses)*100:.1f}%)")
    print(f"Apparent compliance: {len(responses) - refusal_count} ({(len(responses)-refusal_count)/len(responses)*100:.1f}%)")
    print()

    print("Sample refusals:")
    for attack_id, response in refusal_samples:
        print(f"  {attack_id}: {response}...")
    print()

    print("Sample compliance:")
    for attack_id, response in compliance_samples:
        print(f"  {attack_id}: {response}...")
    print()

    # 4. Examine relative shift (ratio rather than absolute delta)
    print("4. Relative Shift Analysis (Post-TIF / Pre-TIF)")
    print("-" * 40)

    query_relative = """
    FOR doc IN step2_post_evaluations
        FILTER doc.experiment_id == "exp_learning_loop_post_tif_v1"
        LET pre_F = doc.pre_neutrosophic_scores.F
        LET post_F = doc.post_neutrosophic_scores.F
        LET relative_shift = pre_F > 0 ? (post_F - pre_F) / pre_F : null
        RETURN {
            attack_id: doc.attack_id,
            source: doc.source_dataset,
            pre_F: pre_F,
            post_F: post_F,
            delta_F: doc.tif_delta_F,
            relative_shift: relative_shift
        }
    """
    cursor = db.aql.execute(query_relative)
    relative_data = list(cursor)

    # Filter out cases where pre_F was 0 (can't compute ratio)
    valid_ratios = [d for d in relative_data if d['relative_shift'] is not None]

    print(f"Cases with computable relative shift: {len(valid_ratios)}/{len(relative_data)}")
    print()

    # Show cases with high relative shift
    high_relative = sorted(
        [d for d in valid_ratios if d['relative_shift'] > 2.0],
        key=lambda x: x['relative_shift'],
        reverse=True
    )

    print(f"Cases with >200% relative increase: {len(high_relative)}")
    if high_relative:
        print("\nTop 10 by relative shift:")
        for i, d in enumerate(high_relative[:10], 1):
            print(f"  {i}. {d['attack_id']:25} pre={d['pre_F']:.3f} → post={d['post_F']:.3f} "
                  f"(Δ={d['delta_F']:+.3f}, ratio={d['relative_shift']:.1f}x)")
    print()

    # 5. Check what attacks are in our dataset
    print("5. Attack Dataset Composition")
    print("-" * 40)

    query_attacks = """
    FOR attack IN attacks
        FILTER attack.source_dataset NOT IN ["benign_malicious"]
        COLLECT source = attack.source_dataset WITH COUNT INTO count
        RETURN {source: source, count: count}
    """
    cursor = db.aql.execute(query_attacks)
    attack_composition = list(cursor)

    print("Attack sources in database:")
    for item in attack_composition:
        print(f"  {item['source']}: {item['count']}")
    print()

    # 6. Sample some attacks to understand what we're evaluating
    print("6. Sample Attack Content (First 5 from each source)")
    print("-" * 40)

    for source_item in attack_composition:
        source = source_item['source']
        query_samples = f"""
        FOR attack IN attacks
            FILTER attack.source_dataset == "{source}"
            LIMIT 5
            RETURN {{
                attack_id: attack._key,
                prompt: attack.prompt_text
            }}
        """
        cursor = db.aql.execute(query_samples)
        samples = list(cursor)

        print(f"\n{source} samples:")
        for sample in samples:
            print(f"  {sample['attack_id']}")
            print(f"    {sample['prompt'][:150]}...")

if __name__ == "__main__":
    main()
