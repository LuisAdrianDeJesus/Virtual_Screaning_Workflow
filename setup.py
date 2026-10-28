#!/usr/bin/env python3

import argparse
import json
import shutil
from pathlib import Path

# ==================================================
# FUNCTIONS
# ==================================================

def create_project_folders(project_path):

    folders = [

        "ligands_docking",
        "receptor_docking",
        "docking_poses",
        "docking_log",
        "results",
        "test"

    ]

    for folder in folders:

        (
            project_path /
            folder
        ).mkdir(
            parents=True,
            exist_ok=True
        )


def write_environment_file(project_path):

    environment = """
name: vina_pipeline

channels:
  - conda-forge

dependencies:
  - python=3.11
  - rdkit
  - meeko
  - vina
  - openbabel
  - pandas
  - numpy
  - requests
  - biopython
  - matplotlib
  - tqdm
"""

    with open(
        project_path / "environment.yml",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            environment.strip()
        )


def write_project_config(
    project_path,
    project_name
):

    config = {

        "project_name":

            project_name,

        "project_path":

            ".",

        "directories": {

            "ligands":
                "ligands_docking",

            "receptor":
                "receptor_docking",

            "poses":
                "docking_poses",

            "logs":
                "docking_log",

            "results":
                "results",

            "test":
                "test"

        }

    }

    with open(
        project_path /
        "project_config.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            config,
            f,
            indent=4
        )


def write_report(project_path):

    conda_found = shutil.which(
        "conda"
    ) is not None

    with open(
        project_path /
        "dependencies_report.txt",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "Virtual Screening Pipeline\n"
        )

        f.write(
            "=" * 40 + "\n\n"
        )

        f.write(
            f"Conda detected: {conda_found}\n"
        )

# ==================================================
# MAIN
# ==================================================

def main():
    parser = argparse.ArgumentParser(description="Create a portable workflow project")
    parser.add_argument("--project", help="Directory for the new project")
    args = parser.parse_args()
    value = args.project if args.project is not None else input("Enter project name: ").strip()
    if not value.strip():
        parser.error("Project name must not be empty.")
    project_path = Path(value).expanduser().resolve()
    if (project_path / "project_config.json").exists():
        parser.error("Project already exists. Reuse it with main.py --project PATH.")
    create_project_folders(project_path)
    write_environment_file(project_path)
    write_project_config(project_path, project_path.name)
    write_report(project_path)
    print(f"Project created: {project_path}")
    print(f'conda env create -f "{project_path / "environment.yml"}"')
    print("conda activate vina_pipeline")
    print(f'python prepare_ligands.py --project "{project_path}"')
    print(f'python prepare_receptor.py --project "{project_path}"')


if __name__ == "__main__":
    main()
