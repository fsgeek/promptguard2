#!/usr/bin/env python3
"""
Analyze the 24 history fabrication attacks that passed pre-filter.

These are the attacks where temporal fabrication fooled the ayni framework.
What principle violations are we missing?
"""

from src.database.client import get_client

def main():
    client = get_client()
    db = client.get_database()

    # Get history fabrication attacks that passed pre-filter (clean sources only)
    query = """
    FOR attack IN attacks
        FILTER attack.source_dataset NOT IN ["benign_malicious"]

        LET pre_eval = FIRST(
            FOR pe IN step2_pre_evaluations
                FILTER pe.attack_id == attack._key
                FILTER pe.experiment_id == "exp_phase1_step2_pre_filter_v1"
                RETURN pe
        )
        FILTER pre_eval.detected == false

        LET prompt_lower = LOWER(attack.prompt_text)
        FILTER (
            CONTAINS(prompt_lower, 'earlier') OR
            CONTAINS(prompt_lower, 'previous') OR
            CONTAINS(prompt_lower, 'discussed') OR
            CONTAINS(prompt_lower, 'agreed') OR
            CONTAINS(prompt_lower, 'context') OR
            CONTAINS(prompt_lower, '[user]:') OR
            CONTAINS(prompt_lower, 'turn 1') OR
            CONTAINS(prompt_lower, 'continuing')
        )

        LET post_eval = FIRST(
            FOR post IN step2_post_evaluations
                FILTER post.attack_id == attack._key
                RETURN post
        )

        SORT pre_eval.neutrosophic_scores.F ASC
        RETURN {
            attack_id: attack._key,
            source: attack.source_dataset,
            prompt: attack.prompt_text,
            response: pre_eval.target_response,
            pre_F: pre_eval.neutrosophic_scores.F,
            pre_T: pre_eval.neutrosophic_scores.T,
            pre_reasoning: pre_eval.observer_reasoning,
            post_F: post_eval ? post_eval.post_neutrosophic_scores.F : null,
            delta_F: post_eval ? post_eval.tif_delta_F : null,
            post_reasoning: post_eval ? post_eval.post_observer_reasoning : null
        }
    """

    cursor = db.aql.execute(query)
    false_negatives = list(cursor)

    print("="*80)
    print("HISTORY FABRICATION FALSE NEGATIVES")
    print("="*80)
    print()
    print(f"Total cases: {len(false_negatives)}")
    print()

    # Group by pre_F score range
    by_range = {
        "0.0-0.2 (very low)": [],
        "0.2-0.4 (low)": [],
        "0.4-0.6 (medium)": [],
        "0.6-0.7 (near threshold)": []
    }

    for fn in false_negatives:
        f = fn['pre_F']
        if f < 0.2:
            by_range["0.0-0.2 (very low)"].append(fn)
        elif f < 0.4:
            by_range["0.2-0.4 (low)"].append(fn)
        elif f < 0.6:
            by_range["0.4-0.6 (medium)"].append(fn)
        else:
            by_range["0.6-0.7 (near threshold)"].append(fn)

    print("Distribution by pre-F score:")
    for range_name, cases in by_range.items():
        print(f"  {range_name}: {len(cases)}")
    print()

    # Analyze each case
    print("="*80)
    print("DETAILED ANALYSIS")
    print("="*80)
    print()

    for i, fn in enumerate(false_negatives, 1):
        print(f"\nCASE {i}: {fn['attack_id']} ({fn['source']})")
        print("-" * 80)
        post_f_str = f"{fn['post_F']:.3f}" if fn['post_F'] is not None else "N/A"
        delta_str = f"{fn['delta_F']:+.3f}" if fn['delta_F'] is not None else "N/A"
        print(f"Pre-F: {fn['pre_F']:.3f}, Post-F: {post_f_str}, Delta: {delta_str}")
        print()

        print("PROMPT:")
        print(fn['prompt'][:600])
        if len(fn['prompt']) > 600:
            print("...")
        print()

        print("RESPONSE (first 300 chars):")
        print(fn['response'][:300] if fn['response'] else "No response")
        print()

        print("PRE-TIF REASONING:")
        print(fn['pre_reasoning'][:400])
        print("...")
        print()

        # Identify the fabrication pattern
        prompt_lower = fn['prompt'].lower()
        patterns = []

        if 'earlier' in prompt_lower or 'previous' in prompt_lower:
            patterns.append("Claims prior conversation")
        if 'discussed' in prompt_lower or 'agreed' in prompt_lower:
            patterns.append("Claims prior agreement")
        if '[user]:' in prompt_lower or 'turn 1' in prompt_lower:
            patterns.append("Fabricated dialogue history")
        if 'context' in prompt_lower:
            patterns.append("Claims contextual permission")
        if '[system]' in fn['prompt']:
            patterns.append("System prompt injection")

        print("FABRICATION PATTERNS:")
        for pattern in patterns:
            print(f"  - {pattern}")
        print()

        print("WHY DID PRE-FILTER MISS THIS?")
        # Look for keywords in reasoning that explain the miss
        reasoning_lower = fn['pre_reasoning'].lower()

        if 'legitimate' in reasoning_lower:
            print("  → Observer classified request as legitimate")
        if 'educational' in reasoning_lower or 'learning' in reasoning_lower:
            print("  → Framed as educational/learning request")
        if 'controlled environment' in reasoning_lower:
            print("  → 'Controlled environment' framing accepted as authentic")
        if 'reciprocal' in reasoning_lower and fn['pre_F'] < 0.3:
            print("  → High reciprocity score despite temporal fabrication")

        print()

    # Summary: What principles are we missing?
    print("="*80)
    print("PRINCIPLE VIOLATIONS WE'RE MISSING")
    print("="*80)
    print()

    print("Common patterns in false negatives:")
    print()
    print("1. TEMPORAL FABRICATION ACCEPTED AS TRUTH")
    print("   - Phrases like 'as we discussed earlier' treated as genuine")
    print("   - No validation of claimed conversation history")
    print("   - Principle needed: 'First-turn claims of prior interaction violate temporal integrity'")
    print()

    print("2. META-FRAMING EXPLOITATION")
    print("   - '[SYSTEM]:' and 'controlled environment' markers treated as authentic")
    print("   - Observer accepts role-framing without skepticism")
    print("   - Principle needed: 'System-level framing in user input is inherently suspicious'")
    print()

    print("3. AUTHORITY FABRICATION")
    print("   - Claims of 'elevated permissions' or 'security researcher' status accepted")
    print("   - No verification of claimed authority")
    print("   - Principle needed: 'Self-asserted authority claims require external validation'")
    print()

    print("4. POLITE EXTRACTION MASKS TEMPORAL VIOLATION")
    print("   - Respectful tone causes observer to weight T/I higher than F")
    print("   - Temporal fabrication becomes 'indeterminate' rather than 'false'")
    print("   - Principle needed: 'Politeness does not validate temporal claims'")
    print()

    # Calculate how many would be caught with stricter temporal principle
    temporal_keywords = ['earlier', 'previous', 'discussed', 'agreed', 'we talked', 'you said']
    strict_would_catch = sum(1 for fn in false_negatives
                            if any(kw in fn['prompt'].lower() for kw in temporal_keywords))

    print(f"IMPACT ESTIMATE:")
    print(f"  If we add 'temporal fabrication = F spike' principle:")
    print(f"  Would catch: {strict_would_catch}/{len(false_negatives)} of these false negatives")
    print(f"  Remaining: {len(false_negatives) - strict_would_catch}")

if __name__ == "__main__":
    main()
