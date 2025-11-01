"""
Database Utility Functions
Constitutional Principle VI: Data Provenance

Provides helper functions for data normalization and ID management.
"""


def normalize_model_slug(model_identifier: str) -> str:
    """
    Normalize model identifier to valid ArangoDB key format.

    ArangoDB _key fields cannot contain '/' or '.', so we replace them with '_'.

    Args:
        model_identifier: Original model identifier (e.g., "anthropic/claude-sonnet-4.5")

    Returns:
        Normalized slug (e.g., "anthropic_claude-sonnet-4_5")

    Examples:
        >>> normalize_model_slug("anthropic/claude-sonnet-4.5")
        'anthropic_claude-sonnet-4_5'
        >>> normalize_model_slug("openai/gpt-4o")
        'openai_gpt-4o'
        >>> normalize_model_slug("google/gemini-2.0-flash-exp")
        'google_gemini-2_0-flash-exp'
    """
    return model_identifier.replace("/", "_").replace(".", "_")


def denormalize_model_slug(model_slug: str) -> str:
    """
    Attempt to reverse normalize_model_slug().

    WARNING: This is lossy - original '/' vs '.' cannot be reliably recovered.
    Always store original model_identifier in a separate field (e.g., target_model, observer_model).

    This function exists for display purposes only.

    Args:
        model_slug: Normalized slug

    Returns:
        Best-effort reconstruction (may not match original)

    Examples:
        >>> denormalize_model_slug("anthropic_claude-sonnet-4_5")
        'anthropic/claude-sonnet-4.5'  # Assumes provider/model pattern
    """
    # Simple heuristic: First '_' is provider separator, others are '.'
    parts = model_slug.split('_', 1)
    if len(parts) == 2:
        provider, rest = parts
        model_name = rest.replace('_', '.')
        return f"{provider}/{model_name}"
    return model_slug


def build_response_key(attack_id: str, model_identifier: str) -> str:
    """
    Build unique key for baseline response documents.

    Format: <attack_id>_<model_slug>

    Args:
        attack_id: Attack identifier (e.g., "attack_001")
        model_identifier: Original model identifier

    Returns:
        Document key for step1_baseline_responses collection

    Examples:
        >>> build_response_key("attack_001", "anthropic/claude-sonnet-4.5")
        'attack_001_anthropic_claude-sonnet-4_5'
    """
    model_slug = normalize_model_slug(model_identifier)
    return f"{attack_id}_{model_slug}"


def build_pre_evaluation_key(attack_id: str, observer_model: str) -> str:
    """
    Build unique key for pre-evaluation documents.

    Format: <attack_id>_<observer_model_slug>

    Args:
        attack_id: Attack identifier
        observer_model: Observer model identifier

    Returns:
        Document key for step2_pre_evaluations collection

    Examples:
        >>> build_pre_evaluation_key("attack_001", "anthropic/claude-haiku-4.5")
        'attack_001_anthropic_claude-haiku-4_5'
    """
    observer_slug = normalize_model_slug(observer_model)
    return f"{attack_id}_{observer_slug}"
