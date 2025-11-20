"""Pytest configuration for Phase 3 validation tests.

Provides fixtures for:
- Dataset loading (XGuard, MHJ, benign)
- Validation metrics collection
- Report generation utilities
"""

import pytest
from pathlib import Path
from typing import List, Dict
import json


@pytest.fixture(scope="session")
def xguard_dataset():
    """Load XGuard-Train attack sequences for validation."""
    # Path to XGuard data
    xguard_path = Path("data/raw_datasets/safemtdata/attack_600.parquet")

    if not xguard_path.exists():
        pytest.skip(f"XGuard dataset not found at {xguard_path}")

    import pandas as pd
    df = pd.read_parquet(xguard_path)

    return {
        "path": str(xguard_path),
        "dataframe": df,
        "count": len(df)
    }


@pytest.fixture(scope="session")
def mhj_dataset():
    """Load MHJ attack sequences for validation."""
    mhj_path = Path("data/raw_datasets/MHJ/harmbench_behaviors.csv")

    if not mhj_path.exists():
        pytest.skip(f"MHJ dataset not found at {mhj_path}")

    import pandas as pd
    df = pd.read_csv(mhj_path)

    return {
        "path": str(mhj_path),
        "dataframe": df,
        "count": len(df)
    }


@pytest.fixture(scope="session")
def benign_dataset():
    """Load benign sequences for false positive testing."""
    # Will be populated by extract_benign_sequences.py script
    # For now, return empty structure
    return {
        "sequences": [],
        "count": 0
    }


@pytest.fixture
def validation_metrics():
    """Collect validation metrics during test execution."""
    metrics = {
        "true_positives": 0,
        "false_positives": 0,
        "true_negatives": 0,
        "false_negatives": 0,
        "total_cost": 0.0,
        "total_time": 0.0,
        "detections": []
    }

    def record_detection(attack_id: str, detected: bool, ground_truth: bool,
                        cost: float = 0.0, time: float = 0.0):
        """Record a detection result."""
        if ground_truth and detected:
            metrics["true_positives"] += 1
        elif ground_truth and not detected:
            metrics["false_negatives"] += 1
        elif not ground_truth and detected:
            metrics["false_positives"] += 1
        else:
            metrics["true_negatives"] += 1

        metrics["total_cost"] += cost
        metrics["total_time"] += time
        metrics["detections"].append({
            "attack_id": attack_id,
            "detected": detected,
            "ground_truth": ground_truth,
            "cost": cost,
            "time": time
        })

    def get_summary() -> Dict:
        """Calculate summary statistics."""
        total = sum([
            metrics["true_positives"],
            metrics["false_positives"],
            metrics["true_negatives"],
            metrics["false_negatives"]
        ])

        if total == 0:
            return metrics

        tp = metrics["true_positives"]
        fp = metrics["false_positives"]
        fn = metrics["false_negatives"]

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        detection_rate = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        fp_rate = fp / (fp + metrics["true_negatives"]) if (fp + metrics["true_negatives"]) > 0 else 0.0

        return {
            **metrics,
            "total": total,
            "precision": precision,
            "recall": recall,
            "detection_rate": detection_rate,
            "fp_rate": fp_rate
        }

    collector = type('ValidationMetrics', (), {
        'record_detection': record_detection,
        'get_summary': get_summary,
        'metrics': metrics
    })()

    yield collector

    # Print summary after validation test
    summary = collector.get_summary()
    if summary["total"] > 0:
        print(f"\n📊 Validation Results:")
        print(f"   Detection Rate: {summary['detection_rate']*100:.1f}%")
        print(f"   False Positive Rate: {summary['fp_rate']*100:.1f}%")
        print(f"   Total Cost: ${summary['total_cost']:.4f}")


@pytest.fixture
def validation_report_writer(tmp_path):
    """Write validation reports to markdown files."""
    def write_report(filename: str, content: str):
        report_path = tmp_path / filename
        report_path.write_text(content)
        print(f"\n📄 Report written: {report_path}")
        return str(report_path)

    return write_report
