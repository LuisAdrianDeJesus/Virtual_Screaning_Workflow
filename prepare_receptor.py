#!/usr/bin/env python3

"""
prepare_receptor.py

Prepare receptor for AutoDock Vina docking.

Input:
    - Local PDB file
    OR
    - PDB ID

Output:
    receptor_docking/
        receptor_original.pdb
        receptor.pdbqt
        conf.txt
        receptor_info.json
"""

import json
import shutil
import subprocess
from pathlib import Path

import requests

# ==========================================================
# FUNCTIONS
# ==========================================================

def load_project():

    project_dirs = list(
        Path(".").glob("*/project_config.json")
    )

    if len(project_dirs) == 0:

        raise FileNotFoundError(
            "project_config.json not found."
        )

    with open(project_dirs[0]) as f:

        return json.load(f)


def download_pdb(
    pdb_id,
    output_file
):

    url = (
        f"https://files.rcsb.org/download/"
        f"{pdb_id}.pdb"
    )

    response = requests.get(url)

    if response.status_code != 200:

        raise Exception(
            f"Unable to download {pdb_id}"
        )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            response.text
        )


def ask_parameter(
    text,
    default
):

    value = input(
        f"{text} [{default}]: "
    ).strip()

    if value == "":

        return default

    return value


def save_conf_file(
    conf_file,
    center_x,
    center_y,
    center_z,
    size_x,
    size_y,
    size_z,
    exhaustiveness,
    num_modes,
    energy_range
):

    with open(conf_file, "w") as f:

        f.write(
            f"center_x = {center_x}\n"
        )

        f.write(
            f"center_y = {center_y}\n"
        )

        f.write(
            f"center_z = {center_z}\n\n"
        )

        f.write(
            f"size_x = {size_x}\n"
        )

        f.write(
            f"size_y = {size_y}\n"
        )

        f.write(
            f"size_z = {size_z}\n\n"
        )

        f.write(
            f"exhaustiveness = {exhaustiveness}\n"
        )

        f.write(
            f"num_modes = {num_modes}\n"
        )

        f.write(
            f"energy_range = {energy_range}\n"
        )


def detect_receptor_tool():

    import shutil

    if shutil.which(
        "mk_prepare_receptor"
    ):

        return "mk_prepare_receptor"

    if shutil.which(
        "mk_prepare_receptor.py"
    ):

        return "mk_prepare_receptor.py"

    raise RuntimeError(
        "Meeko receptor preparation tool not found."
    )


# ==========================================================
# START
# ==========================================================

print("\n====================================")
print(" Receptor Preparation")
print("====================================\n")

config = load_project()

project_dir = Path(
    config["project_path"]
)

receptor_dir = (
    project_dir /
    "receptor_docking"
)

# ==========================================================
# INPUT SOURCE
# ==========================================================

print("Select input source:")

print(
    "\n1 - Local PDB file"
)

print(
    "2 - Download from PDB"
)

option = input(
    "\nOption: "
).strip()

original_pdb = (
    receptor_dir /
    "receptor_original.pdb"
)

# ==========================================================
# LOCAL FILE
# ==========================================================

if option == "1":

    pdb_file = input(
        "\nPDB file path: "
    ).strip()

    pdb_file = Path(
        pdb_file
    )

    if not pdb_file.exists():

        raise FileNotFoundError(
            "PDB file not found."
        )

    shutil.copy(
        pdb_file,
        original_pdb
    )

# ==========================================================
# RCSB DOWNLOAD
# ==========================================================

elif option == "2":

    pdb_id = input(
        "\nPDB ID: "
    ).strip().upper()

    print(
        f"\nDownloading {pdb_id}..."
    )

    download_pdb(
        pdb_id,
        original_pdb
    )

else:

    raise ValueError(
        "Invalid option."
    )

# ==========================================================
# BOX PARAMETERS
# ==========================================================

print(
    "\nDocking box parameters"
)

center_x = ask_parameter(
    "center_x",
    "0"
)

center_y = ask_parameter(
    "center_y",
    "0"
)

center_z = ask_parameter(
    "center_z",
    "0"
)

size_x = ask_parameter(
    "size_x",
    "20"
)

size_y = ask_parameter(
    "size_y",
    "20"
)

size_z = ask_parameter(
    "size_z",
    "20"
)

exhaustiveness = ask_parameter(
    "exhaustiveness",
    "8"
)

num_modes = ask_parameter(
    "num_modes",
    "9"
)

energy_range = ask_parameter(
    "energy_range",
    "3"
)

# ==========================================================
# SAVE CONF
# ==========================================================

conf_file = (
    receptor_dir /
    "conf.txt"
)

save_conf_file(

    conf_file,

    center_x,
    center_y,
    center_z,

    size_x,
    size_y,
    size_z,

    exhaustiveness,
    num_modes,
    energy_range

)

# ==========================================================
# PREPARE RECEPTOR
# ==========================================================

print(
    "\nPreparing receptor..."
)

preparation_tool = (
    detect_receptor_tool()
)

receptor_pdbqt = (
    receptor_dir /
    "receptor.pdbqt"
)

command = [

    preparation_tool,

    "-i",
    str(original_pdb),

    "-o",
    str(receptor_pdbqt)

]

result = subprocess.run(

    command,

    capture_output=True,

    text=True

)

if result.returncode != 0:

    print(
        result.stderr
    )

    raise RuntimeError(
        "Receptor preparation failed."
    )

# ==========================================================
# SAVE INFO
# ==========================================================

info = {

    "original_pdb":
        original_pdb.name,

    "receptor_pdbqt":
        receptor_pdbqt.name,

    "center_x":
        center_x,

    "center_y":
        center_y,

    "center_z":
        center_z,

    "size_x":
        size_x,

    "size_y":
        size_y,

    "size_z":
        size_z,

    "exhaustiveness":
        exhaustiveness,

    "num_modes":
        num_modes,

    "energy_range":
        energy_range

}

with open(

    receptor_dir /
    "receptor_info.json",

    "w"

) as f:

    json.dump(
        info,
        f,
        indent=4
    )

# ==========================================================
# SUMMARY
# ==========================================================

print("\n====================================")
print(" Receptor Preparation Completed")
print("====================================")

print(
    f"\nReceptor:\n{receptor_pdbqt}"
)

print(
    f"\nConfig:\n{conf_file}"
)

print(
    f"\nMetadata:\n"
    f"{receptor_dir / 'receptor_info.json'}"
)

print("\nDone.\n")