#!/usr/bin/env python3

import json
import shutil
import sys
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

            str(
                project_path.resolve()
            ),

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

print("\n===================================")
print(" Virtual Screening Pipeline Setup")
print("===================================\n")

project_name = input(
    "Enter project name: "
).strip()

if project_name == "":

    print(
        "\nERROR: Invalid project name."
    )

    sys.exit(1)

project_path = Path(
    project_name
)

create_project_folders(
    project_path
)

write_environment_file(
    project_path
)

write_project_config(
    project_path,
    project_name
)

write_report(
    project_path
)

print("\n===================================")
print(" Setup Completed")
print("===================================")

print(
    f"\nProject:\n"
    f"{project_path.resolve()}"
)

print(
    "\nNext step:"
)

print(
    "\nconda env create -f environment.yml"
)

print(
    "\nconda activate vina_pipeline"
)

print(
    "\npython prepare_ligands.py"
)

print(
    "\npython prepare_receptor.py"
)

print(
    "\nDone.\n"
)