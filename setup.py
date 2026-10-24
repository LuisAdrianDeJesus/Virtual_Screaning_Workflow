#!/usr/bin/env python3

"""
Virtual Screening Pipeline Setup

Creates project structure and checks dependencies.
"""

import json
import sys
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
    "requests": "requests",
    "matplotlib": "matplotlib"
}

# ==========================================================
# FUNCTIONS
# ==========================================================

def install_package(package_name):

    try:

        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            package_name
        ])

        return True

    except Exception:

        return False


def check_python_package(module_name, package_name):

    try:

        importlib.import_module(module_name)

        return "INSTALLED"

    except ImportError:

        print(
            f"[WARNING] {module_name} not found."
        )

        print(
            f"[INFO] Installing {package_name}..."
        )

        success = install_package(
            package_name
        )

        if success:

            try:

                importlib.import_module(
                    module_name
                )

                return "INSTALLED"

            except ImportError:

                return "FAILED"

        return "FAILED"


def check_vina():

    if shutil.which("vina"):

        return "FOUND"

    return "NOT FOUND"


def get_vina_version():

    try:

        result = subprocess.run(

            ["vina", "--version"],

            capture_output=True,
            text=True

        )

        return result.stdout.strip()

    except Exception:

        return "VERSION NOT DETECTED"


def create_directories(project_dir):

    folders = [

        "ligands_docking",
        "receptor_docking",
        "docking_poses",
        "docking_log",
        "results"

    ]

    project_dir.mkdir(
        exist_ok=True
    )

    for folder in folders:

        (project_dir / folder).mkdir(
            exist_ok=True
        )

# ==========================================================
# MAIN
# ==========================================================

print("\n================================================")
print(" Virtual Screening Pipeline Setup")
print("================================================\n")

project_name = input(
    "Enter project name: "
).strip()

if not project_name:

    print(
        "\n[ERROR] Project name cannot be empty.\n"
    )

    sys.exit()

project_path = Path(
    project_name
)

create_directories(
    project_path
)

print(
    "\n[INFO] Project structure created.\n"
)

# ==========================================================
# DEPENDENCY CHECK
# ==========================================================

report = []

print(
    "\n[INFO] Checking Python dependencies...\n"
)

for module_name, package_name in REQUIRED_PACKAGES.items():

    status = check_python_package(

        module_name,

        package_name

    )

    print(
        f"{module_name:<20} {status}"
    )

    report.append(
        f"{module_name:<25} {status}"
    )

# ==========================================================
# VINA CHECK
# ==========================================================

print(
    "\n[INFO] Checking AutoDock Vina...\n"
)

vina_status = check_vina()

report.append(
    f"{'vina':<25} {vina_status}"
)

print(
    f"{'vina':<20} {vina_status}"
)

vina_version = get_vina_version()

# ==========================================================
# REPORT FILE
# ==========================================================

report_file = (

    project_path /

    "dependencies_report.txt"

)

with open(
    report_file,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "Virtual Screening Pipeline\n"
    )

    f.write(
        "=" * 60 + "\n\n"
    )

    for line in report:

        f.write(
            line + "\n"
        )

    f.write("\n")

    f.write(
        "AutoDock Vina Version:\n"
    )

    f.write(
        vina_version + "\n"
    )

# ==========================================================
# PROJECT CONFIG
# ==========================================================

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
            "results"

    },

    "vina_version":

        vina_version

}

config_file = ( 

    "project_config.json"

)

with open(
    config_file,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        config,
        f,
        indent=4
    )

# ==========================================================
# FINISH
# ==========================================================

print("\n================================================")
print(" Setup Completed")
print("================================================")

print(
    f"\nProject location:\n{project_path.resolve()}"
)

print("\nCreated directories:")

print("  ligands_docking/")
print("  receptor_docking/")
print("  docking_poses/")
print("  docking_log/")
print("  results/")

print("\nGenerated files:")

print("  dependencies_report.txt")
print("  project_config.json")

if vina_status == "NOT FOUND":

    print(
        "\n[WARNING] AutoDock Vina was not detected."
    )

    print(
        "Install Vina and add it to PATH before docking."
    )

else:

    print(
        "\n[OK] AutoDock Vina detected."
    )

print("\nNext steps:")

print(
    "  python prepare_ligands.py"
)

print(
    "  python prepare_receptor.py"
)

print(
    "\nSetup completed successfully.\n"
)