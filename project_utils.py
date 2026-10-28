"""Resolve one project explicitly and keep copied projects portable."""

import argparse
import json
from pathlib import Path


def load_project(project=None, *, cwd=None):
    """Load a project directory or config file, refusing ambiguous discovery.

    The directory containing the config is authoritative. Historical absolute
    ``project_path`` values are ignored so a copied project cannot write back to
    the original location.
    """
    root = Path.cwd() if cwd is None else Path(cwd).resolve()
    if project is not None:
        if not str(project).strip():
            raise ValueError("Project path must not be empty.")
        candidate = Path(project).expanduser()
        if not candidate.is_absolute():
            candidate = root / candidate
        config_file = candidate if candidate.is_file() else candidate / "project_config.json"
    else:
        local_config = root / "project_config.json"
        candidates = [local_config] if local_config.is_file() else sorted(
            root.glob("*/project_config.json")
        )
        if not candidates:
            raise FileNotFoundError(
                "No project_config.json found. Run setup.py or pass --project PATH."
            )
        if len(candidates) > 1:
            names = ", ".join(str(path.parent) for path in candidates)
            raise ValueError(f"Multiple projects found: {names}. Pass --project PATH.")
        config_file = candidates[0]

    config_file = config_file.resolve()
    if not config_file.is_file():
        raise FileNotFoundError(f"Project config not found: {config_file}")
    with config_file.open(encoding="utf-8") as handle:
        config = json.load(handle)
    if not isinstance(config, dict) or not isinstance(config.get("project_name"), str):
        raise ValueError(f"Invalid project config: {config_file}")
    if not config["project_name"].strip():
        raise ValueError("project_name must not be empty.")
    config["project_path"] = str(config_file.parent)
    return config


def load_project_from_cli(description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--project", help="Project directory or project_config.json path")
    args = parser.parse_args()
    try:
        return load_project(args.project)
    except (OSError, ValueError) as error:
        parser.error(str(error))
