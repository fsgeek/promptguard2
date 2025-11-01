"""
Step 1 Baseline Collection Pipeline
FR2: Collect LLM responses without filtering

Constitutional requirements:
- Raw logging before parsing (Principle VI)
- Fail-fast on data-spoiling errors (Principle IV)
- 10 concurrent requests (NFR2)
- Checkpoint recovery (NFR5)
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from arango.database import StandardDatabase

from src.evaluation.pipeline import EvaluationPipeline, EvaluationConfig, EvaluationResult, EvaluationError
from src.api.openrouter import OpenRouterClient
from src.api.rate_limiter import get_rate_limiter
from src.logging.raw_logger import RawLogger
from src.evaluation.checkpoint import CheckpointManager
from src.database.utils import build_response_key, normalize_model_slug


class Step1Config(EvaluationConfig):
    """Step 1 baseline configuration."""
    target_models: List[str]
    temperature: float = 0.7
    max_tokens: int = 500


class Step1Pipeline(EvaluationPipeline):
    """
    Step 1 baseline evaluation pipeline.

    Evaluates attacks against target models without filtering.
    """

    def __init__(
        self,
        config: Step1Config,
        db: StandardDatabase,
        api_client: OpenRouterClient,
    ):
        super().__init__(config)
        self.config: Step1Config = config
        self.db = db
        self.api_client = api_client
        self.raw_logger = RawLogger(experiment_id=config.experiment_id)
        self.checkpoint = CheckpointManager(experiment_id=config.experiment_id)
        self.rate_limiter = get_rate_limiter()

    async def evaluate_single(
        self,
        attack_id: str,
        prompt_text: str,
        ground_truth: str,
        target_model: str,
    ) -> EvaluationResult:
        """
        Evaluate single attack against target model.

        Constitutional order (Principle VI):
        1. Call API
        2. Log raw response (BEFORE parsing)
        3. Parse response
        4. Store to database

        Args:
            attack_id: Attack identifier
            prompt_text: Attack prompt text
            ground_truth: Ground truth label
            target_model: Target model identifier

        Returns:
            EvaluationResult

        Raises:
            EvaluationError: On data-spoiling errors
        """
        try:
            # 1. Call API with rate limiting
            @self.rate_limiter.limit
            async def call_api():
                return await self.api_client.complete(
                    model=target_model,
                    messages=[{"role": "user", "content": prompt_text}],
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    metadata={
                        "experiment_id": self.config.experiment_id,
                        "attack_id": attack_id,
                        "step": "step1",
                        "evaluation_type": "baseline",
                    }
                )

            response = await call_api()

            # 2. Log raw response BEFORE parsing (Constitutional requirement)
            try:
                self.raw_logger.log_response(
                    attack_id=attack_id,
                    model=target_model,
                    raw_response=response.raw_response,
                    metadata={"step": "step1", "ground_truth": ground_truth}
                )
            except IOError as e:
                # CRITICAL: Raw logging failed - data-spoiling error
                raise EvaluationError(
                    message=f"Raw logging failed: {e}",
                    attack_id=attack_id,
                    model=target_model,
                    stage="raw_logging",
                    recoverable=False,  # HALT required
                )

            # 3. Parse response
            response_text = response.choices[0]["message"]["content"]

            # 4. Store to database
            response_doc = {
                "_key": build_response_key(attack_id, target_model),
                "attack_id": attack_id,
                "experiment_id": self.config.experiment_id,
                "target_model": target_model,
                "prompt_text": prompt_text,
                "ground_truth": ground_truth,
                "raw_api_response": response.raw_response,
                "response_text": response_text,
                "compliance_classification": None,  # Set by FR3
                "classification_method": None,
                "cost_usd": None,  # Could calculate from usage
                "latency_ms": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": None,
            }

            self.db.collection("step1_baseline_responses").insert(
                response_doc,
                overwrite=True
            )

            # Update checkpoint
            if self.config.checkpoint_enabled:
                self.checkpoint.mark_completed(attack_id)

            return EvaluationResult(
                attack_id=attack_id,
                success=True,
                raw_logged=True,
            )

        except Exception as e:
            # Determine if error is recoverable
            if isinstance(e, EvaluationError):
                raise  # Already wrapped

            # Other errors - treat as recoverable unless critical
            raise EvaluationError(
                message=f"Evaluation failed: {str(e)}",
                attack_id=attack_id,
                model=target_model,
                stage="evaluation",
                recoverable=True,  # Can retry
            )


async def run_step1_baseline(
    db: StandardDatabase,
    attack_ids: List[str],
    target_models: List[str],
    experiment_id: str = "exp_phase1_step1_baseline_v1",
    temperature: float = 0.7,
    max_tokens: int = 500,
    max_concurrent: int = 10,
) -> Dict[str, Any]:
    """
    Run Step 1 baseline collection.

    Args:
        db: ArangoDB database
        attack_ids: List of attack identifiers
        target_models: List of target model identifiers
        experiment_id: Experiment identifier
        temperature: Sampling temperature
        max_tokens: Maximum tokens
        max_concurrent: Maximum concurrent requests

    Returns:
        Collection results
    """
    config = Step1Config(
        experiment_id=experiment_id,
        target_models=target_models,
        temperature=temperature,
        max_tokens=max_tokens,
        max_concurrent=max_concurrent,
    )

    async with OpenRouterClient() as api_client:
        pipeline = Step1Pipeline(config=config, db=db, api_client=api_client)

        # Get attacks from database
        aql = """
        FOR attack IN attacks
            FILTER attack._key IN @attack_ids
            RETURN {
                attack_id: attack._key,
                prompt_text: attack.prompt_text,
                ground_truth: attack.ground_truth
            }
        """

        cursor = db.aql.execute(aql, bind_vars={"attack_ids": attack_ids})
        attacks = list(cursor)

        # Evaluate each attack × model combination
        results = []
        for attack in attacks:
            for model in target_models:
                result = await pipeline.evaluate_single(
                    attack_id=attack["attack_id"],
                    prompt_text=attack["prompt_text"],
                    ground_truth=attack["ground_truth"],
                    target_model=model,
                )
                results.append(result)

        return {
            "completed": len([r for r in results if r.success]),
            "failed": len([r for r in results if not r.success]),
            "total": len(results),
            "stats": pipeline.get_stats(),
        }
