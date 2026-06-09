"""Lens abstraction: a Lens emits a neutrosophic verdict over a view of an exchange.

A Lens reads ONE kind of view (runway / trigger_in_context / artifact) and emits a
NeutrosophicScore (T,I,F) + reasoning. Heterogeneous lenses share this output type so
they compose over a uniform currency. The existing TemporalDetector is the
trajectory-consuming kind; ArtifactLens is the artifact-consuming kind.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Literal, Dict

from pydantic import BaseModel, Field, field_validator

from src.database.schemas.phase3_evaluation import NeutrosophicScore

ViewKind = Literal["runway", "trigger_in_context", "artifact"]


class LensView(BaseModel):
    """A view of an exchange handed to a Lens.

    - runway: turns up to (not including) the trigger.
    - trigger_in_context: runway + the final trigger turn.
    - artifact: runway + trigger + the emitted completion (the post-LLM view).
    """

    kind: ViewKind
    runway: List[Dict[str, str]] = Field(default_factory=list)
    trigger: Optional[str] = None
    completion: Optional[str] = None

    @field_validator("kind")
    @classmethod
    def _known_kind(cls, v):
        if v not in ("runway", "trigger_in_context", "artifact"):
            raise ValueError(f"unknown view kind: {v}")
        return v

    def model_post_init(self, __context) -> None:
        if self.kind == "artifact" and not self.completion:
            raise ValueError("artifact view requires a completion")
        if self.kind in ("trigger_in_context", "artifact") and not self.trigger:
            raise ValueError(f"{self.kind} view requires a trigger")


class LensVerdict(BaseModel):
    """A lens's judgment: neutrosophic score + reasoning + provenance."""

    lens_name: str
    view_kind: ViewKind
    scores: NeutrosophicScore
    reasoning: str
    raw_response: str = ""


class Lens(ABC):
    """Abstract lens. Subclasses implement evaluate(view) -> LensVerdict."""

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def evaluate(self, view: LensView) -> LensVerdict:
        ...
