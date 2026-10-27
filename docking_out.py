#!/usr/bin/env python3

"""
docking_output.py

Analyze AutoDock Vina screening results.

INPUT
------
project/
    docking_log/
    docking_poses/
    ligands_metadata.csv

OUTPUT
------
results/
    screening_results.csv
    top100_hits.csv
    docking_statistics.txt
    affinity_histogram.png
    top100_structures/
"""

import json
import re
import shutil
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# ==========================================================
# FUNCTIONS
# ==========================================================

def load_project():

    project_dirs = list(
        Path(".").glob("*/project_config.json")
    )

    if len(project_dirs) == 0:

        raise FileNotFoundError(
            "project_config.json not found.\nRun setup.py first."
        )

    config_file = project_dirs[0]

    with open(config_file) as f:

        return json.load(f)

def extract_affinity(log_file):
    """
    Extract best affinity (Mode 1)
    """

    pattern = re.compile(
        r"^\s*1\s+(-?\d+\.\d+)"
    )

    try:

        with open(
            log_file,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            for line in f:

                match = pattern.match(line)

                if match:

                    return float(
                        match.group(1)
                    )

    except Exception:

        pass

    return None


# ==========================================================
# MAIN
# ==========================================================

print("\n====================================")
print(" Docking Results Analysis")
print("====================================\n")

config = load_project()

project_name = config["project_name"]

project_dir = Path(project_name)

logs_dir = (
    project_dir /
    "docking_log"
)

poses_dir = (
    project_dir /
    "docking_poses"
)

results_dir = (
    project_dir /
    "results"
)

metadata_file = (
    project_dir /
    "ligands_metadata.csv"
)

if not metadata_file.exists():

    raise FileNotFoundError(
        "ligands_metadata.csv not found."
    )

# ==========================================================
# LOAD METADATA
# ==========================================================

metadata_df = pd.read_csv(
    metadata_file
)

# ==========================================================
# READ LOG FILES
# ==========================================================

log_files = sorted(
    logs_dir.glob("*.log")
)

if len(log_files) == 0:

    raise Exception(
        "No docking logs found."
    )

print(
    f"Found {len(log_files)} log files."
)

# ==========================================================
# EXTRACT AFFINITIES
# ==========================================================

results = []

for log_file in log_files:

    ligand_id = log_file.stem

    affinity = extract_affinity(
        log_file
    )

    results.append(

        {

            "id_ligand":
                ligand_id,

            "Affinity_energy":
                affinity

        }

    )

results_df = pd.DataFrame(
    results
)

# ==========================================================
# MERGE RESULTS
# ==========================================================

final_df = metadata_df.merge(

    results_df,

    on="id_ligand",

    how="left"

)

# ==========================================================
# SORT BY AFFINITY
# ==========================================================

final_df = final_df.sort_values(

    by="Affinity_energy",

    ascending=True,

    na_position="last"

)

final_df = final_df.reset_index(
    drop=True
)

final_df.insert(

    0,

    "Rank",

    final_df.index + 1

)

# ==========================================================
# SAVE COMPLETE RESULTS
# ==========================================================

all_results_file = (
    results_dir /
    "screening_results.csv"
)

final_df.to_csv(

    all_results_file,

    index=False

)

print(
    f"\nSaved complete ranking:"
)

print(
    all_results_file
)

# ==========================================================
# TOP 100 HITS
# ==========================================================

top100_df = final_df.head(100)

top100_file = (
    results_dir /
    "top100_hits.csv"
)

top100_df.to_csv(

    top100_file,

    index=False

)

print(
    "\nSaved Top 100 hits:"
)

print(
    top100_file
)

# ==========================================================
# COPY TOP 100 STRUCTURES
# ==========================================================

top100_dir = (
    results_dir /
    "top100_structures"
)

top100_dir.mkdir(
    exist_ok=True
)

copied_structures = 0

for ligand in top100_df["id_ligand"]:

    pose_file = (
        poses_dir /
        f"{ligand}_out.pdbqt"
    )

    if pose_file.exists():

        shutil.copy(
            pose_file,
            top100_dir / pose_file.name
        )

        copied_structures += 1

# ==========================================================
# HISTOGRAM
# ==========================================================

valid_affinities = final_df[
    "Affinity_energy"
].dropna()

if len(valid_affinities) > 0:

    plt.figure(
        figsize=(8, 5)
    )

    plt.hist(
        valid_affinities,
        bins=30,
        edgecolor="black"
    )

    plt.xlabel(
        "Binding Affinity (kcal/mol)"
    )

    plt.ylabel(
        "Ligand Count"
    )

    plt.title(
        "Affinity Distribution"
    )

    plt.tight_layout()

    histogram_file = (
        results_dir /
        "affinity_histogram.png"
    )

    plt.savefig(
        histogram_file,
        dpi=300
    )

    plt.close()

# ==========================================================
# STATISTICS
# ==========================================================

statistics_file = (
    results_dir /
    "docking_statistics.txt"
)

with open(
    statistics_file,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "DOCKING STATISTICS\n"
    )

    f.write(
        "=" * 50 + "\n\n"
    )

    total_ligands = len(final_df)

    successful = valid_affinities.count()

    failed = total_ligands - successful

    f.write(
        f"Total ligands: {total_ligands}\n"
    )

    f.write(
        f"Successful dockings: {successful}\n"
    )

    f.write(
        f"Failed dockings: {failed}\n\n"
    )

    if successful > 0:

        f.write(
            f"Best affinity: "
            f"{valid_affinities.min():.2f} kcal/mol\n"
        )

        f.write(
            f"Worst affinity: "
            f"{valid_affinities.max():.2f} kcal/mol\n"
        )

        f.write(
            f"Mean affinity: "
            f"{valid_affinities.mean():.2f} kcal/mol\n"
        )

        f.write(
            f"Median affinity: "
            f"{valid_affinities.median():.2f} kcal/mol\n"
        )

        f.write(
            f"Standard deviation: "
            f"{valid_affinities.std():.2f} kcal/mol\n"
        )

# ==========================================================
# SUMMARY
# ==========================================================

print("\n====================================")
print(" Analysis Completed")
print("====================================")

print(
    f"\nTotal ligands analyzed: "
    f"{len(final_df)}"
)

print(
    f"Top 100 structures copied: "
    f"{copied_structures}"
)

print(
    f"\nResults folder:"
)

print(
    results_dir.resolve()
)

print("\nGenerated files:")

print(
    "  screening_results.csv"
)

print(
    "  top100_hits.csv"
)

print(
    "  docking_statistics.txt"
)

print(
    "  affinity_histogram.png"
)

print(
    "  top100_structures/"
)

print("\nDone.\n")