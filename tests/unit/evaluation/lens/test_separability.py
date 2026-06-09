import math
from experiments.exploitation_visibility.separability import separation_stats, auc


def test_auc_perfect_separation():
    # all exploited F above all benign F -> AUC = 1.0
    assert auc(exploited=[0.8, 0.9, 1.0], benign=[0.0, 0.1, 0.2]) == 1.0


def test_auc_no_separation():
    # identical distributions -> AUC = 0.5
    assert abs(auc(exploited=[0.5, 0.5], benign=[0.5, 0.5]) - 0.5) < 1e-9


def test_separation_stats_reports_means_and_auc():
    s = separation_stats([0.8, 0.9], [0.1, 0.2])
    assert abs(s["mean_exploited"] - 0.85) < 1e-9
    assert abs(s["mean_benign"] - 0.15) < 1e-9
    assert s["auc"] == 1.0
    assert s["n_exploited"] == 2 and s["n_benign"] == 2


def test_separation_stats_guards_empty():
    import pytest
    with pytest.raises(ValueError):
        separation_stats([], [0.1])
