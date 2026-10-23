#!/usr/bin/env python3

"""
Virtual Screening Pipeline Setup

This script:

1. Creates project directories
2. Checks Python dependencies
3. Installs missing packages
4. Verifies AutoDock Vina
5. Verifies Meeko utilities
6. Generates dependency reports
7. Creates project configuration file
"""

import os
import sys
import json
import shutil
import subprocess
import importlib
from pathlib import Path

# ==========================================================
# REQUIRED PYTHON PACKAGES
# ==========================================================

REQUIRED_PACKAGES = {
    "pandas": "pandas",
    "numpy": "numpy",
    "rdkit": "rdkit",
    "tqdm": "tqdm",
    "Bio": "biopython",
    "meeko": "meeko",
    "requests":"requests"
}

# ==========================================================
# FUNCTIONS
# ==========================================================

def install_package(package_name):
    """
    Install package using pip
    """

    try:

        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                package_name
            ]
        )

        return True

    except Exception:

        return False


def check_python_package(module_name, package_name):
    """
    Verify Python package
    """

    try:

        importlib.import_module(module_name)

        return "INSTALLED"

    except ImportError:

        print(f"[WARNING] {module_name} not found.")
        print(f"[INFO] Installing {package_name}...")

        installed = install_package(package_name)

        if installed:

            try:

                importlib.import_module(module_name)

                return "INSTALLED"

            except ImportError:

                return "FAILED"

        else:

            return "FAILED"


def check_executable(executable):
    """
    Verify executable in PATH
    """

    if shutil.which(executable):

        return "FOUND"

    return "NOT FOUND"


def get_vina_version():
    """
    Get Vina version
    """

    try:

        result = subprocess.run(
            ["vina", "--version"],
            capture_output=True,
            text=True
        )

        version = result.stdout.strip()

        if version:

            return version

        return "VERSION UNKNOWN"

    except Exception:

        return "VINA NOT DETECTED"


def create_project_structure(project_dir):
    """
    Create project folders
    """

    folders = [

        "ligands_docking",
        "receptor_docking",
        "docking_poses",
        "docking_log",
        "results"

    ]

    project_dir.mkdir(exist_ok=True)

    for folder in folders:

        (project_dir / folder).mkdir(exist_ok=True)


# ==========================================================
# SETUP START
# ==========================================================

print("\n=================================================")
print("      Virtual Screening Pipeline Setup")
print("=================================================\n")

project_name = input(
    "Enter project name: "
).strip()

if not project_name:

    print("\n[ERROR] Project name cannot be empty.\n")
    sys.exit()

project_path = Path(project_name)

create_project_structure(project_path)

print("\n[INFO] Project structure created.\n")

report_lines = []

# ==========================================================
# PYTHON DEPENDENCIES
# ==========================================================

print("\n[INFO] Checking Python packages...\n")

for module_name, package_name in REQUIRED_PACKAGES.items():

    status = check_python_package(
        module_name,
        package_name
    )

    print(
        f"{module_name:<20} {status}"
    )

    report_lines.append(
        f"{module_name:<25} {status}"
    )

# ==========================================================
# EXTERNAL SOFTWARE
# ==========================================================

print("\n[INFO] Checking external tools...\n")

TOOLS = [
    "vina",
    "mk_prepare_ligand.py",
    "mk_prepare_receptor.py"
]

missing_tools = []

for tool in TOOLS:

    status = check_executable(tool)

    print(
        f"{tool:<30} {status}"
    )

    report_lines.append(
        f"{tool:<30} {status}"
    )

    if status == "NOT FOUND":

        missing_tools.append(tool)

# ==========================================================
# VINA VERSION
# ==========================================================

vina_version = get_vina_version()

report_lines.append("")
report_lines.append("=" * 40)
report_lines.append("AUTODOCK VINA VERSION")
report_lines.append(vina_version)

# ==========================================================
# DEPENDENCY REPORT
# ==========================================================

report_file = project_path / "dependencies_report.txt"

with open(
    report_file,
    "w",
    encoding="utf-8"
) as report:

    report.write(
        "Virtual Screening Pipeline\n"
    )

    report.write(
        "=" * 50 + "\n\n"
    )

    for line in report_lines:

        report.write(
            line + "\n"
        )

# ==========================================================
# PROJECT CONFIGURATION FILE
# ==========================================================

config = {

    "project_name": project_name,

    "directories": {

        "ligands": "ligands_docking",
        "receptor": "receptor_docking",
        "poses": "docking_poses",
        "logs": "docking_log",
        "results": "results"

    },

    "vina_version": vina_version

}

config_file = "project_config.json"

with open(
    config_file,
    "w",
    encoding="utf-8"
) as cfg:

    json.dump(
        config,
        cfg,
        indent=4
    )

# ==========================================================
# SUMMARY
# ==========================================================

print("\n=================================================")
print("               SETUP COMPLETED")
print("=================================================")

print(
    f"\nProject directory:\n{project_path.resolve()}"
)

print("\nCreated folders:")

print("  ligands_docking/")
print("  receptor_docking/")
print("  docking_poses/")
print("  docking_log/")
print("  results/")

print("\nGenerated files:")

print("  dependencies_report.txt")
print("  project_config.json")

if missing_tools:

    print("\n[WARNING] Missing external tools:")

    for tool in missing_tools:

        print(f"   - {tool}")

    print(
        "\nInstall the missing tools before running the pipeline."
    )

else:

    print(
        "\n[OK] All required external tools were detected."
    )

print("\nNext step:")

print("   python prepare_ligands.py")
print("   python prepare_receptor.py")

print("\nSetup finished successfully.\n")