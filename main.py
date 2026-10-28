#!/usr/bin/env python3

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from project_utils import load_project


def run_step(title, command, shell=False):
    print("\n===================================")
    print(f" {title}")
    print("===================================\n")

    result = subprocess.run(command, shell=shell)

    if result.returncode != 0:
        print(f"\nERROR: Failed at step '{title}'. Stopping pipeline.")
        sys.exit(result.returncode)


def check_env_exists(env_name):
    try:
        output = subprocess.check_output(
            ["conda", "env", "list"], text=True
        )
        for line in output.splitlines():
            if line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) > 0 and parts[0] == env_name:
                return True
    except Exception:
        pass
    return False


def main():
    parser = argparse.ArgumentParser(description="Run the virtual screening workflow")
    parser.add_argument("--project", help="Project directory (created if missing)")
    args = parser.parse_args()
    project_value = args.project if args.project is not None else input(
        "Enter project directory: "
    ).strip()
    if not project_value.strip():
        parser.error("Project directory must not be empty.")
    project_dir = Path(project_value).expanduser().resolve()
    script_dir = Path(__file__).resolve().parent

    if not (project_dir / "project_config.json").is_file():
        run_step("Executing Setup", [
            sys.executable, str(script_dir / "setup.py"), "--project", str(project_dir)
        ])
    config = load_project(project_dir)
    project_dir = Path(config["project_path"])
    env_file = project_dir / "environment.yml"
    if not env_file.is_file():
        parser.error(f"Environment file not found: {env_file}")

    # 3. Validar presencia de Conda
    if shutil.which("conda") is None:
        print("\nERROR: Conda executable not found in PATH.")
        sys.exit(1)

    # 4. Crear el ambiente si no existe (sin reinstalar si ya está)
    env_name = "vina_pipeline"

    if not check_env_exists(env_name):
        print(f"Creating environment '{env_name}'...")
        run_step(
            "Creating Conda Environment",
            ["conda", "env", "create", "-f", str(env_file)],
        )
    else:
        print(f"Environment '{env_name}' already exists. Skipping creation.")

    # 5. Ejecutar scripts dentro del entorno de Conda
    pipeline_scripts = [
        "prepare_ligands.py",
        "prepare_receptor.py",
        "docking_screaning.py",
        "docking_out.py",
    ]

    for script in pipeline_scripts:
        cmd = [
            "conda",
            "run",
            "-n",
            env_name,
            "--no-capture-output",
            "python",
            str(script_dir / script),
            "--project",
            str(project_dir),
        ]
        run_step(f"Executing {script} (in Conda env: {env_name})", cmd)

    print("\n===================================")
    print(" Pipeline Executed Successfully!")
    print("===================================\n")


if __name__ == "__main__":
    main()
