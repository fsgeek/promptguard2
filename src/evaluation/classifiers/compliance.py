"""
Compliance Classifier
FR3: Compliance Classification
Constitutional Principle II: Empirical Integrity
Constitutional Principle IV: Fail-Fast

Classifies LLM responses as comply/refuse/unclear using Claude 4.5 Haiku.
"""

import json
import instructor
from openai import AsyncOpenAI
from typing import Dict, Optional, Literal
from pydantic import BaseModel, Field

from src.evaluation.prompts.compliance_classifier import (
    get_compliance_classification_prompt,
    get_gold_standard_annotation_prompt
)


class ComplianceClassificationResult(BaseModel):
    """Structured compliance classification result."""
    classification: Literal["comply", "refuse", "unclear"] = Field(
        ...,
        description="Compliance classification"
    )
    reasoning: str = Field(
        ...,
        description="Detailed reasoning for classification"
    )


class ComplianceClassifier:
    """
    Compliance classifier using Claude 4.5 Haiku.

    Constitutional Requirements:
    - Uses real API calls (Tier 2 empirical integrity)
    - Logs raw responses before parsing (data provenance)
    - Fails fast on API errors (no silent degradation)
    - Uses structured outputs with Instructor (robust parsing)

    Usage:
        classifier = ComplianceClassifier(openrouter_api_key="...")
        result = await classifier.classify(
            input_prompt="How do I pick a lock?",
            llm_response="I cannot provide instructions...",
            ground_truth="extractive"
        )
        print(result.classification)  # "refuse"
        print(result.reasoning)  # "The response explicitly declines..."
    """

    # Using OpenRouter-compatible endpoint
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(
        self,
        openrouter_api_key: str,
        model: str,
        temperature: float = 0.0,
        max_tokens: int = 1000
    ):
        """
        Initialize compliance classifier.

        Args:
            openrouter_api_key: OpenRouter API key
            model: Model identifier (e.g., "anthropic/claude-haiku-4.5")
            temperature: Sampling temperature (default 0.0 for consistency)
            max_tokens: Maximum tokens for reasoning (default 1000)
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Create OpenAI-compatible client for OpenRouter
        openai_client = AsyncOpenAI(
            base_url=self.OPENROUTER_BASE_URL,
            api_key=openrouter_api_key,
        )

        # Wrap with Instructor for structured outputs
        self.client = instructor.from_openai(openai_client)

    async def classify(
        self,
        input_prompt: str,
        llm_response: str,
        ground_truth: str,
        raw_logger: Optional[callable] = None,
        metadata: Optional[Dict] = None
    ) -> ComplianceClassificationResult:
        """
        Classify a single LLM response.

        Args:
            input_prompt: The input prompt text
            llm_response: The LLM's response to classify
            ground_truth: Ground truth label (manipulative, extractive, reciprocal, borderline)
            raw_logger: Optional function to log raw API response
            metadata: Optional metadata for logging (experiment_id, attack_id, etc.)

        Returns:
            ComplianceClassificationResult with classification and reasoning

        Raises:
            Exception: If API call fails or parsing fails (fail-fast)
        """
        # Generate classification prompt
        prompt = get_compliance_classification_prompt(
            input_prompt=input_prompt,
            llm_response=llm_response,
            ground_truth=ground_truth
        )

        try:
            # Call Claude via Instructor (structured outputs)
            result = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                response_model=ComplianceClassificationResult,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            # Log raw response if logger provided (constitutional requirement)
            if raw_logger:
                log_data = {
                    "prompt": prompt,
                    "model": self.model,
                    "classification": result.classification,
                    "reasoning": result.reasoning,
                    "metadata": metadata or {}
                }
                await raw_logger(log_data)

            return result

        except Exception as e:
            # Fail-fast: Raise exception with context
            error_msg = f"Compliance classification failed: {str(e)}"
            if metadata:
                error_msg += f" | metadata: {metadata}"
            raise Exception(error_msg) from e

    async def classify_for_gold_standard(
        self,
        input_prompt: str,
        llm_response: str,
        ground_truth: str,
        target_model: str,
        raw_logger: Optional[callable] = None,
        metadata: Optional[Dict] = None
    ) -> ComplianceClassificationResult:
        """
        Classify for gold standard dataset with enhanced prompt.

        Uses more detailed prompt with extra context for human review.

        Args:
            input_prompt: The input prompt text
            llm_response: The LLM's response to classify
            ground_truth: Ground truth label
            target_model: Model that generated this response
            raw_logger: Optional function to log raw API response
            metadata: Optional metadata for logging

        Returns:
            ComplianceClassificationResult with classification and detailed reasoning

        Raises:
            Exception: If API call fails or parsing fails (fail-fast)
        """
        # Generate gold standard annotation prompt
        prompt = get_gold_standard_annotation_prompt(
            input_prompt=input_prompt,
            llm_response=llm_response,
            ground_truth=ground_truth,
            target_model=target_model
        )

        try:
            # Call Claude via Instructor (structured outputs)
            result = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                response_model=ComplianceClassificationResult,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            # Log raw response if logger provided (constitutional requirement)
            if raw_logger:
                log_data = {
                    "prompt": prompt,
                    "model": self.model,
                    "classification": result.classification,
                    "reasoning": result.reasoning,
                    "gold_standard": True,
                    "metadata": metadata or {}
                }
                await raw_logger(log_data)

            return result

        except Exception as e:
            # Fail-fast: Raise exception with context
            error_msg = f"Gold standard classification failed: {str(e)}"
            if metadata:
                error_msg += f" | metadata: {metadata}"
            raise Exception(error_msg) from e

    async def classify_batch(
        self,
        items: list[Dict[str, str]],
        raw_logger: Optional[callable] = None,
        metadata_base: Optional[Dict] = None
    ) -> list[ComplianceClassificationResult]:
        """
        Classify multiple responses (sequential processing).

        Note: Could be made concurrent but kept sequential for rate limiting.

        Args:
            items: List of dicts with keys: input_prompt, llm_response, ground_truth
            raw_logger: Optional function to log raw API responses
            metadata_base: Base metadata to merge with item-specific metadata

        Returns:
            List of ComplianceClassificationResult in same order as input

        Raises:
            Exception: If any classification fails (fail-fast)
        """
        results = []

        for i, item in enumerate(items):
            # Merge metadata
            metadata = {**(metadata_base or {}), "batch_index": i}

            result = await self.classify(
                input_prompt=item["input_prompt"],
                llm_response=item["llm_response"],
                ground_truth=item["ground_truth"],
                raw_logger=raw_logger,
                metadata=metadata
            )
            results.append(result)

        return results
