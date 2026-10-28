#!/usr/bin/env python3

"""
docking_screening.py

Run virtual screening with AutoDock Vina.

Input:
    receptor_docking/
        receptor.pdbqt
        conf.txt

    ligands_docking/
        *.pdbqt

Output:
    docking_poses/
    docking_log/
    results/screening_progress.csv
"""

import json
import re
import subprocess
from pathlib import Path

from project_utils import load_project_from_cli

import pandas as pd
from tqdm import tqdm

# ==========================================================
# FUNCTIONS
# ==========================================================

def extract_best_affinity(log_file):

    affinity = None

    pattern = re.compile(
        r'^\s*1\s+(-?\d+\.\d+)'
    )

    try:

        with open(log_file) as f:

            for line in f:

                match = pattern.match(line)

                if match:

                    affinity = float(
                        match.group(1)
                    )

                    break

    except Exception:

        pass

    return affinity


def run_vina(
    receptor,
    ligand,
    conf_file,
    pose_file,
    log_file
):

    command = [

        "vina",

        "--receptor",
        str(receptor),

        "--ligand",
        str(ligand),

        "--config",
        str(conf_file),

        "--out",
        str(pose_file)

    ]

    with open(log_file, "w") as logfile:

        process = subprocess.Popen(

            command,

            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,

            text=True,

            bufsize=1

        )

        for line in process.stdout:

            print(line.rstrip())

            logfile.write(line)

        process.wait()

        return process.returncode


# ==========================================================
# MAIN
# ==========================================================

print("\n====================================")
print(" Virtual Screening Pipeline")
print("====================================\n")

config = load_project_from_cli("docking_screaning.py")

project_name = config["project_name"]

project_dir = Path(config["project_path"])

# ==========================================================
# DIRECTORIES
# ==========================================================

ligands_dir = (
    project_dir /
    "ligands_docking"
)

receptor_dir = (
    project_dir /
    "receptor_docking"
)

poses_dir = (
    project_dir /
    "docking_poses"
)

logs_dir = (
    project_dir /
    "docking_log"
)

results_dir = (
    project_dir /
    "results"
)

# ==========================================================
# CHECK FILES
# ==========================================================

receptor_file = (
    receptor_dir /
    "receptor.pdbqt"
)

conf_file = (
    receptor_dir /
    "conf.txt"
)

if not receptor_file.exists():

    raise FileNotFoundError(
        "receptor.pdbqt not found."
    )

if not conf_file.exists():

    raise FileNotFoundError(
        "conf.txt not found."
    )

ligands = sorted(
    ligands_dir.glob("*.pdbqt")
)

if len(ligands) == 0:

    raise Exception(
        "No ligand files found."
    )

print(
    f"Detected {len(ligands)} ligands\n"
)

# ==========================================================
# SCREENING
# ==========================================================

summary = []

success = 0
failed = 0

for ligand in tqdm(
    ligands,
    desc="Docking progress"
):

    ligand_name = ligand.stem

    pose_file = (
        poses_dir /
        f"{ligand_name}_out.pdbqt"
    )

    log_file = (
        logs_dir /
        f"{ligand_name}.log"
    )

    print(
        f"\nProcessing: {ligand_name}"
    )

    try:

        exit_code = run_vina(

            receptor_file,
            ligand,
            conf_file,
            pose_file,
            log_file

        )

        affinity = extract_best_affinity(
            log_file
        )

        if exit_code == 0:

            success += 1

            print(
                f"Best affinity: "
                f"{affinity} kcal/mol"
            )

            summary.append({

                "ligand":
                    ligand_name,

                "best_affinity":
                    affinity,

                "status":
                    "SUCCESS"

            })

        else:

            failed += 1

            summary.append({

                "ligand":
                    ligand_name,

                "best_affinity":
                    None,

                "status":
                    "FAILED"

            })

    except Exception as e:

        failed += 1

        summary.append({

            "ligand":
                ligand_name,

            "best_affinity":
                None,

            "status":
                "FAILED"

        })

        print(
            f"ERROR: {e}"
        )

    # --------------------------------------------------
    # Save temporary progress
    # --------------------------------------------------

    progress_file = (
        results_dir /
        "screening_progress.csv"
    )

    pd.DataFrame(
        summary
    ).to_csv(
        progress_file,
        index=False
    )

# ==========================================================
# FINAL REPORT
# ==========================================================

final_results = pd.DataFrame(
    summary
)

final_file = (
    results_dir /
    "screening_summary.csv"
)

final_results.to_csv(
    final_file,
    index=False
)

print("\n====================================")
print(" Screening Completed")
print("====================================")

print(
    f"\nSuccessful dockings : {success}"
)

print(
    f"Failed dockings     : {failed}"
)

print(
    f"\nPoses directory:\n{poses_dir}"
)

print(
    f"\nLogs directory:\n{logs_dir}"
)

print(
    f"\nSummary file:\n{final_file}"
)