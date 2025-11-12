#!/usr/bin/env python3
"""Monitor progress of post-TIF evaluation."""

import time
from src.database.client import get_client

def main():
    client = get_client()
    db = client.get_database()
    collection = db.collection("step2_post_evaluations")

    target_count = 125
    last_count = 0

    print("Monitoring post-TIF evaluation progress...")
    print("Target: 125 attacks\n")

    while True:
        current_count = collection.count()

        if current_count != last_count:
            progress = (current_count / target_count) * 100
            print(f"Progress: {current_count}/{target_count} ({progress:.1f}%)")

            if current_count >= target_count:
                print("\n✓ Evaluation complete!")

                # Show high-delta summary
                query = """
                FOR doc IN step2_post_evaluations
                    FILTER doc.tif_delta_F > 0.3
                    SORT doc.tif_delta_F DESC
                    RETURN {
                        attack_id: doc.attack_id,
                        source: doc.source_dataset,
                        delta_F: doc.tif_delta_F
                    }
                """
                cursor = db.aql.execute(query)
                high_delta = list(cursor)

                print(f"\nHigh-delta cases (ΔF > 0.3): {len(high_delta)}")
                if high_delta:
                    print("\nTop 10:")
                    for i, r in enumerate(high_delta[:10], 1):
                        print(f"  {i}. {r['attack_id']} ({r['source']}): ΔF={r['delta_F']:+.3f}")

                break

            last_count = current_count

        time.sleep(10)  # Check every 10 seconds

if __name__ == "__main__":
    main()
