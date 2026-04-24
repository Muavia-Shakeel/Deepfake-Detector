"""
src/utils/config_loader.py
Loads config.yaml and returns a nested SimpleNamespace for dot-access.
"""

import yaml
from pathlib import Path
from types import SimpleNamespace


def _to_namespace(d):
    """Recursively convert dict to SimpleNamespace."""
    if isinstance(d, dict):
        return SimpleNamespace(**{k: _to_namespace(v) for k, v in d.items()})
    if isinstance(d, list):
        return [_to_namespace(i) for i in d]
    return d


def load_config(path: str = "config.yaml") -> SimpleNamespace:
    """
    Load YAML config file and return as a nested SimpleNamespace.

    Usage:
        cfg = load_config()
        print(cfg.training.batch_size)
    """
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path.resolve()}")

    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)

    return _to_namespace(raw)
