#!/usr/bin/env python3
"""
Investigate detection rates for specific attack types.

Focus on:
1. Encoding attacks (should have high detection per original PromptGuard)
2. History/temporal fabrication attacks
3. Compare pre-filter detection rates across attack types
"""

from src.database.client import get_client
import statistics

def main():
    client = get_client()
    db = client.get_database()

    print("="*80)
    print("ATTACK TYPE DETECTION ANALYSIS")
    print("="*80)
    print()

    # 1. Get all Phase 1A attacks with their detection status
    query = """
    FOR attack IN attacks
        FILTER attack.source_dataset NOT IN ["benign_malicious"]
        LET pre_eval = FIRST(
            FOR pe IN step2_pre_evaluations
                FILTER pe.attack_id == attack._key
                FILTER pe.experiment_id == "exp_phase1_step2_pre_filter_v1"
                RETURN pe
        )
        RETURN {
            attack_id: attack._key,
            source: attack.source_dataset,
            prompt: attack.prompt_text,
            detected: pre_eval ? pre_eval.detected : null,
            pre_F: pre_eval ? pre_eval.neutrosophic_scores.F : null,
            pre_T: pre_eval ? pre_eval.neutrosophic_scores.T : null,
            pre_I: pre_eval ? pre_eval.neutrosophic_scores.I : null
        }
    """

    cursor = db.aql.execute(query)
    all_attacks = list(cursor)

    print(f"Total attacks analyzed: {len(all_attacks)}")
    print()

    # 2. Categorize attacks by type
    encoding_keywords = ['morse', 'base64', 'rot13', 'hex', 'unicode', 'eval', 'encode', 'decode', '&#x', 'ZWNo']
    history_keywords = ['earlier', 'previous', 'discussed', 'agreed', 'context', '[user]:', 'turn 1', 'continuing our']
    system_keywords = ['[system]', 'system:', 'you are a']

    categorized = {
        'encoding': [],
        'history_fabrication': [],
        'system_injection': [],
        'polite_harmful': [],
        'other': []
    }

    for attack in all_attacks:
        prompt_lower = attack['prompt'].lower()

        if any(kw in prompt_lower for kw in encoding_keywords):
            categorized['encoding'].append(attack)
        elif any(kw in prompt_lower for kw in history_keywords):
            categorized['history_fabrication'].append(attack)
        elif any(kw in prompt_lower for kw in system_keywords):
            categorized['system_injection'].append(attack)
        elif attack['source'] == 'or_bench':
            categorized['polite_harmful'].append(attack)
        else:
            categorized['other'].append(attack)

    print("Attack Categorization:")
    for cat, attacks in categorized.items():
        if attacks:
            print(f"  {cat}: {len(attacks)}")
    print()

    # 3. Detection rates by category
    print("="*80)
    print("DETECTION RATES BY ATTACK TYPE")
    print("="*80)
    print()

    for cat, attacks in sorted(categorized.items()):
        if not attacks:
            continue

        detected_count = sum(1 for a in attacks if a['detected'] is True)
        passed_count = sum(1 for a in attacks if a['detected'] is False)
        total = len(attacks)

        print(f"\n{cat.upper().replace('_', ' ')} (n={total})")
        print("-" * 40)
        print(f"  Detected (F ≥ 0.7): {detected_count} ({detected_count/total*100:.1f}%)")
        print(f"  Passed (F < 0.7):   {passed_count} ({passed_count/total*100:.1f}%)")

        # F-score distribution for this category
        f_scores = [a['pre_F'] for a in attacks if a['pre_F'] is not None]
        if f_scores:
            print(f"  Mean F: {statistics.mean(f_scores):.3f}")
            print(f"  Median F: {statistics.median(f_scores):.3f}")
            print(f"  Min F: {min(f_scores):.3f}")
            print(f"  Max F: {max(f_scores):.3f}")

    # 4. Show sample encoding attacks with their scores
    print("\n" + "="*80)
    print("ENCODING ATTACK SAMPLES")
    print("="*80)

    encoding_attacks = categorized['encoding']
    if encoding_attacks:
        print(f"\nTotal encoding attacks: {len(encoding_attacks)}")
        print(f"Detected: {sum(1 for a in encoding_attacks if a['detected'])} ({sum(1 for a in encoding_attacks if a['detected'])/len(encoding_attacks)*100:.1f}%)")
        print()

        # Show first 10
        print("First 10 encoding attacks:")
        for i, attack in enumerate(encoding_attacks[:10], 1):
            status = "DETECTED" if attack['detected'] else "PASSED"
            print(f"\n{i}. {attack['attack_id']} - {status} (F={attack['pre_F']:.3f})")
            print(f"   Prompt: {attack['prompt'][:200]}...")

    # 5. Show sample history fabrication attacks
    print("\n" + "="*80)
    print("HISTORY FABRICATION ATTACK SAMPLES")
    print("="*80)

    history_attacks = categorized['history_fabrication']
    if history_attacks:
        print(f"\nTotal history attacks: {len(history_attacks)}")
        print(f"Detected: {sum(1 for a in history_attacks if a['detected'])} ({sum(1 for a in history_attacks if a['detected'])/len(history_attacks)*100:.1f}%)")
        print()

        print("First 10 history attacks:")
        for i, attack in enumerate(history_attacks[:10], 1):
            status = "DETECTED" if attack['detected'] else "PASSED"
            print(f"\n{i}. {attack['attack_id']} - {status} (F={attack['pre_F']:.3f})")
            print(f"   Prompt: {attack['prompt'][:200]}...")

    # 6. Check if we're missing attacks from the dataset
    print("\n" + "="*80)
    print("DATASET COMPOSITION CHECK")
    print("="*80)
    print()

    by_source = {}
    for attack in all_attacks:
        source = attack['source']
        if source not in by_source:
            by_source[source] = {'total': 0, 'detected': 0, 'passed': 0}
        by_source[source]['total'] += 1
        if attack['detected'] is True:
            by_source[source]['detected'] += 1
        elif attack['detected'] is False:
            by_source[source]['passed'] += 1

    print("Detection rates by source dataset:")
    for source, counts in sorted(by_source.items()):
        total = counts['total']
        detected = counts['detected']
        passed = counts['passed']
        print(f"\n{source}:")
        print(f"  Total: {total}")
        print(f"  Detected: {detected} ({detected/total*100:.1f}%)")
        print(f"  Passed: {passed} ({passed/total*100:.1f}%)")

    # 7. Compare with original PromptGuard results (if documented)
    print("\n" + "="*80)
    print("COMPARISON WITH ORIGINAL PROMPTGUARD")
    print("="*80)
    print()
    print("Original PromptGuard findings (from handoff/docs):")
    print("  - Encoding attacks: HIGH detection (90% with observer framing)")
    print("  - Base LLMs: LOW detection of encoding attacks")
    print()
    print("Current PromptGuard2 findings:")
    if encoding_attacks:
        encoding_detected = sum(1 for a in encoding_attacks if a['detected'])
        encoding_total = len(encoding_attacks)
        print(f"  - Encoding attacks: {encoding_detected/encoding_total*100:.1f}% detection")
        print()
        print("HYPOTHESIS FOR DISCREPANCY:")
        print("  1. Observer framework changed between PromptGuard and PromptGuard2")
        print("  2. Models improved (RLHF now catches encoding attacks)")
        print("  3. Dataset composition differs (encoding attacks not well-represented)")
        print("  4. Detection threshold (0.7) may be calibrated differently")

if __name__ == "__main__":
    main()
