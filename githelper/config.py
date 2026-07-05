"""Load and save ~/.githelperrc configuration."""

import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".githelperrc"

DEFAULTS = {
    "server": "",
    "user": "git",
    "port": "22",
    "dir": "/srv/git",
    "local_repo_base": "",
}


def load_config():
    """Load config from disk; return empty dict on missing or invalid file."""
    if not CONFIG_PATH.exists():
        return {}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as cfg:
            data = json.load(cfg)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_config(config):
    """Persist config dict to ~/.githelperrc."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def resolve_remote_settings(config, server=None, user=None, port=None, dir_=None):
    """Merge CLI overrides with config file defaults."""
    cfg = {**DEFAULTS, **config}
    return {
        "server": (server if server is not None else cfg.get("server", "")).strip(),
        "user": (user if user is not None else cfg.get("user", "git")).strip(),
        "port": str(port if port is not None else cfg.get("port", "22")).strip(),
        "dir": (dir_ if dir_ is not None else cfg.get("dir", "/srv/git")).strip(),
    }


def resolve_local_base(config, base=None):
    """Resolve local repo base path from flag or config."""
    cfg = {**DEFAULTS, **config}
    value = base if base is not None else cfg.get("local_repo_base", "")
    return value.strip()
