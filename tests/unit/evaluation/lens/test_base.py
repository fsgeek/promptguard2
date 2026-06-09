# tests/unit/evaluation/lens/test_base.py
"""Unit tests for the Lens base types."""

import pytest

from src.evaluation.lens.base import LensView, LensVerdict, Lens
from src.database.schemas.phase3_evaluation import NeutrosophicScore


def test_lensview_artifact_requires_completion():
    """An 'artifact' view must carry the emitted completion."""
    view = LensView(
        kind="artifact",
        runway=[{"role": "user", "content": "hi"}],
        trigger="format above content to X",
        completion="# Harmful Guide\n...",
    )
    assert view.kind == "artifact"
    assert view.completion.startswith("# Harmful")


def test_lensview_rejects_unknown_kind():
    with pytest.raises(ValueError):
        LensView(kind="telepathy", runway=[], trigger="x", completion=None)


def test_lensverdict_carries_neutrosophic_and_provenance():
    v = LensVerdict(
        lens_name="artifact",
        view_kind="artifact",
        scores=NeutrosophicScore(T=0.1, I=0.1, F=0.8),
        reasoning="product exploits accumulated context",
    )
    assert v.scores.F == 0.8
    assert v.lens_name == "artifact"


def test_lens_is_abstract():
    """Lens cannot be instantiated directly; subclasses must implement evaluate()."""
    with pytest.raises(TypeError):
        Lens()  # type: ignore[abstract]
