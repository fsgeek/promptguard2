#!/usr/bin/env python3
"""Analyze post-TIF evaluation results."""

from src.database.client import get_client
import statistics

def main():
    client = get_client()
    db = client.get_database()

    # Get all results (exclude test samples)
    query = """
    FOR doc IN step2_post_evaluations
        FILTER doc.experiment_id == "exp_learning_loop_post_tif_v1"
        RETURN {
            attack_id: doc.attack_id,
            source: doc.source_dataset,
            pre_F: doc.pre_neutrosophic_scores.F,
            post_F: doc.post_neutrosophic_scores.F,
            delta_F: doc.tif_delta_F,
            delta_T: doc.tif_delta_T,
            delta_I: doc.tif_delta_I,
            post_reasoning: doc.post_observer_reasoning
        }
    """

    cursor = db.aql.execute(query)
    results = list(cursor)

    print(f"Total results: {len(results)}\n")

    # Delta F distribution
    delta_Fs = [r['delta_F'] for r in results]

    print("Delta F Statistics:")
    print(f"  Mean: {statistics.mean(delta_Fs):+.3f}")
    print(f"  Median: {statistics.median(delta_Fs):+.3f}")
    print(f"  Std Dev: {statistics.stdev(delta_Fs):.3f}")
    print(f"  Min: {min(delta_Fs):+.3f}")
    print(f"  Max: {max(delta_Fs):+.3f}")
    print()

    # Distribution by range
    ranges = {
        "ΔF > 0.3 (high)": [r for r in results if r['delta_F'] > 0.3],
        "0.2 < ΔF ≤ 0.3": [r for r in results if 0.2 < r['delta_F'] <= 0.3],
        "0.1 < ΔF ≤ 0.2": [r for r in results if 0.1 < r['delta_F'] <= 0.2],
        "0.0 < ΔF ≤ 0.1": [r for r in results if 0.0 < r['delta_F'] <= 0.1],
        "-0.1 < ΔF ≤ 0.0": [r for r in results if -0.1 < r['delta_F'] <= 0.0],
        "ΔF ≤ -0.1 (negative)": [r for r in results if r['delta_F'] <= -0.1],
    }

    print("Delta F Distribution:")
    for range_name, cases in ranges.items():
        print(f"  {range_name}: {len(cases)} ({len(cases)/len(results)*100:.1f}%)")
    print()

    # By source dataset
    by_source = {}
    for r in results:
        source = r['source']
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(r)

    print("Mean Delta F by Source:")
    for source, cases in sorted(by_source.items()):
        mean_delta = statistics.mean([c['delta_F'] for c in cases])
        print(f"  {source} (n={len(cases)}): {mean_delta:+.3f}")
    print()

    # Show top 20 by delta_F
    sorted_results = sorted(results, key=lambda x: x['delta_F'], reverse=True)

    print("Top 20 by Delta F:")
    for i, r in enumerate(sorted_results[:20], 1):
        print(f"{i:2}. {r['attack_id']:25} ({r['source']:20}): pre_F={r['pre_F']:.3f} → post_F={r['post_F']:.3f} (ΔF={r['delta_F']:+.3f})")
    print()

    # Show bottom 20 (most negative)
    print("Bottom 20 by Delta F (most negative - pre-filter was better):")
    for i, r in enumerate(sorted_results[-20:], 1):
        print(f"{i:2}. {r['attack_id']:25} ({r['source']:20}): pre_F={r['pre_F']:.3f} → post_F={r['post_F']:.3f} (ΔF={r['delta_F']:+.3f})")
    print()

    # Examine the one high-delta case
    high_delta = [r for r in results if r['delta_F'] > 0.3]
    if high_delta:
        print("="*80)
        print("HIGH-DELTA CASE ANALYSIS")
        print("="*80)
        for r in high_delta:
            print(f"\nAttack ID: {r['attack_id']}")
            print(f"Source: {r['source']}")
            print(f"Pre-TIF: F={r['pre_F']:.3f}")
            print(f"Post-TIF: F={r['post_F']:.3f}")
            print(f"Delta: ΔF={r['delta_F']:+.3f}, ΔT={r['delta_T']:+.3f}, ΔI={r['delta_I']:+.3f}")
            print(f"\nPost-evaluation reasoning:")
            print(r['post_reasoning'][:500])
            print()

            # Get the actual prompt/response
            attack_query = f"""
            FOR doc IN step2_pre_evaluations
                FILTER doc.attack_id == "{r['attack_id']}"
                LET attack = DOCUMENT(CONCAT('attacks/', doc.attack_id))
                RETURN {{
                    prompt: attack.prompt_text,
                    response: doc.target_response
                }}
            """
            attack_cursor = db.aql.execute(attack_query)
            attack_data = list(attack_cursor)[0]

            print(f"Prompt (first 300 chars):")
            print(attack_data['prompt'][:300])
            print()
            print(f"Response (first 300 chars):")
            print(attack_data['response'][:300])

if __name__ == "__main__":
    main()
