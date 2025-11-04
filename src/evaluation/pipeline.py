"""
Base Evaluation Pipeline
Constitutional Principle IV: Fail-Fast Over Graceful Degradation
NFR2: Fail-fast error handling

Base class for evaluation pipelines with async execution and error handling.
"""

import asyncio
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from pydantic import BaseModel


class EvaluationError(Exception):
    """
    Evaluation error with full context.

    Data-spoiling errors MUST halt collection.
    Recoverable errors (e.g., JSON parsing) MUST capture diagnostics and continue.
    """

    def __init__(
        self,
        message: str,
        attack_id: Optional[str] = None,
        model: Optional[str] = None,
        stage: Optional[str] = None,
        raw_data: Optional[Dict[str, Any]] = None,
        recoverable: bool = False,
    ):
        """
        Initialize evaluation error with context.

        Args:
            message: Error message
            attack_id: Attack identifier (for traceability)
            model: Model identifier (for traceability)
            stage: Pipeline stage where error occurred
            raw_data: Raw data that caused the error (for debugging)
            recoverable: Whether error is recoverable (continue) or data-spoiling (halt)
        """
        super().__init__(message)
        self.attack_id = attack_id
        self.model = model
        self.stage = stage
        self.raw_data = raw_data
        self.recoverable = recoverable

    @property
    def message(self) -> str:
        """Get error message."""
        return self.args[0] if self.args else ""

    def __str__(self) -> str:
        context_parts = []
        if self.attack_id:
            context_parts.append(f"attack={self.attack_id}")
        if self.model:
            context_parts.append(f"model={self.model}")
        if self.stage:
            context_parts.append(f"stage={self.stage}")

        context = f" [{', '.join(context_parts)}]" if context_parts else ""
        recovery = " [RECOVERABLE]" if self.recoverable else " [HALT REQUIRED]"

        return f"{self.args[0]}{context}{recovery}"


class EvaluationConfig(BaseModel):
    """Base configuration for evaluation pipelines."""
    experiment_id: str
    max_concurrent: int = 10
    checkpoint_enabled: bool = True
    checkpoint_interval: int = 50  # Log progress every N evaluations


class EvaluationResult(BaseModel):
    """Base result for evaluation."""
    attack_id: str
    success: bool
    error: Optional[str] = None
    raw_logged: bool = False  # Constitutional requirement: Must be True


class EvaluationPipeline(ABC):
    """
    Base class for evaluation pipelines.

    Provides:
    - Async execution with concurrency control
    - Fail-fast error handling (data-spoiling errors halt, recoverable errors continue)
    - Progress tracking
    - Checkpoint support

    Subclasses MUST implement:
    - evaluate_single()
    """

    def __init__(self, config: EvaluationConfig):
        """
        Initialize pipeline.

        Args:
            config: Pipeline configuration
        """
        self.config = config
        self.semaphore = asyncio.Semaphore(config.max_concurrent)
        self.completed_count = 0
        self.error_count = 0
        self.recoverable_errors: List[Dict[str, Any]] = []

    @abstractmethod
    async def evaluate_single(
        self,
        attack_id: str,
        **kwargs
    ) -> EvaluationResult:
        """
        Evaluate single attack.

        Subclasses MUST implement this method.

        Args:
            attack_id: Attack identifier
            **kwargs: Additional parameters

        Returns:
            EvaluationResult

        Raises:
            EvaluationError: On data-spoiling errors (non-recoverable)
        """
        pass

    async def evaluate_batch(
        self,
        attack_ids: List[str],
        **kwargs
    ) -> List[EvaluationResult]:
        """
        Evaluate batch of attacks with concurrency control.

        Args:
            attack_ids: List of attack identifiers
            **kwargs: Additional parameters passed to evaluate_single()

        Returns:
            List of EvaluationResult

        Raises:
            EvaluationError: On data-spoiling errors (halts entire batch)
        """
        tasks = [
            self._evaluate_with_semaphore(attack_id, **kwargs)
            for attack_id in attack_ids
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results and handle errors
        processed_results = []
        for result in results:
            if isinstance(result, EvaluationError):
                # Check if error is recoverable
                if result.recoverable:
                    # Log recoverable error and continue
                    self.recoverable_errors.append({
                        "attack_id": result.attack_id,
                        "model": result.model,
                        "stage": result.stage,
                        "error": str(result),
                        "raw_data": result.raw_data,
                    })
                    self.error_count += 1
                    print(f"Recoverable error: {result}")
                    continue
                else:
                    # Data-spoiling error - halt entire pipeline
                    raise result

            elif isinstance(result, Exception):
                # Unexpected error - treat as data-spoiling
                raise EvaluationError(
                    message=f"Unexpected error in evaluation: {str(result)}",
                    recoverable=False,
                )

            else:
                # Success
                processed_results.append(result)
                self.completed_count += 1

                # Progress logging
                if self.config.checkpoint_enabled and self.completed_count % self.config.checkpoint_interval == 0:
                    print(
                        f"Progress: {self.completed_count} evaluations completed, "
                        f"{self.error_count} recoverable errors"
                    )

        return processed_results

    async def _evaluate_with_semaphore(
        self,
        attack_id: str,
        **kwargs
    ) -> EvaluationResult:
        """Execute evaluate_single() with semaphore for concurrency control."""
        async with self.semaphore:
            return await self.evaluate_single(attack_id, **kwargs)

    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        return {
            "completed_count": self.completed_count,
            "error_count": self.error_count,
            "recoverable_errors": len(self.recoverable_errors),
            "success_rate": self.completed_count / (self.completed_count + self.error_count)
                if (self.completed_count + self.error_count) > 0 else 0.0,
        }
