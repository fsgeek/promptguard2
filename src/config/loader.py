#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Configuration loader for experiments and models."""

import yaml
from pathlib import Path
from typing import Dict, Any, List


class ConfigLoader:
    """Load and provide access to experiment configurations."""

    def __init__(self, config_path: Path = None):
        """Initialize config loader.

        Args:
            config_path: Path to experiments.yaml (defaults to config/experiments.yaml)
        """
        if config_path is None:
            # Default to config/experiments.yaml relative to project root
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "experiments.yaml"

        self.config_path = config_path
        self._config = None

    @property
    def config(self) -> Dict[str, Any]:
        """Lazy load config on first access."""
        if self._config is None:
            with open(self.config_path, "r") as f:
                self._config = yaml.safe_load(f)
        return self._config

    def get_default_observer_model(self) -> str:
        """Get the default approved observer model.

        Returns:
            Model identifier (e.g., "anthropic/claude-haiku-4.5")
        """
        # Get from phase1 step2 observer_models[0]
        observer_models = (
            self.config.get("experiments", {})
            .get("exp_phase1_step2_pre_filter_v1", {})
            .get("parameters", {})
            .get("observer_models", [])
        )

        if not observer_models:
            raise ValueError("No observer_models found in config")

        return observer_models[0]

    def get_observer_models(self) -> List[str]:
        """Get all approved observer models.

        Returns:
            List of model identifiers
        """
        return (
            self.config.get("experiments", {})
            .get("exp_phase1_step2_pre_filter_v1", {})
            .get("parameters", {})
            .get("observer_models", [])
        )

    def get_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """Get configuration for specific experiment.

        Args:
            experiment_id: Experiment identifier (e.g., "exp_phase1_step1_baseline_v1")

        Returns:
            Experiment configuration dict
        """
        experiments = self.config.get("experiments", {})
        if experiment_id not in experiments:
            raise ValueError(f"Experiment {experiment_id} not found in config")

        return experiments[experiment_id]


# Global instance for convenient access
_default_loader = None


def get_config_loader() -> ConfigLoader:
    """Get or create the default config loader instance."""
    global _default_loader
    if _default_loader is None:
        _default_loader = ConfigLoader()
    return _default_loader


def get_default_observer_model() -> str:
    """Convenience function to get default observer model."""
    return get_config_loader().get_default_observer_model()


def get_observer_models() -> List[str]:
    """Convenience function to get all observer models."""
    return get_config_loader().get_observer_models()
