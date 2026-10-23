#!/usr/bin/env python3

"""
prepare_receptor.py

Prepare receptor for AutoDock Vina docking.

Input:
    - Local PDB file
    OR
    - PDB code

Output:
    receptor_docking/
        receptor.pdbqt
        receptor_original.pdb
        conf.txt
        receptor_info.json
"""

import json
import shutil
import subprocess
from pathlib import Path

import requests
from Bio.PDB import PDBParser
from Bio.PDB import PDBIO
from Bio.PDB import Select

# =====================================================
# FUNCTIONS
# =====================================================

def load_project():

    config_file = Path("project_config.json")

    if not config_file.exists():

        raise FileNotFoundError(
            "project_config.json not found.\nRun setup.py first."
        )

    with open(config_file) as f:
        return json.load(f)


def download_pdb(pdb_id, output_file):

    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"

    response = requests.get(url)

    if response.status_code != 200:

        raise Exception(
            f"Could not download PDB {pdb_id}"
        )

    with open(output_file, "w") as f:
        f.write(response.text)


def ask_parameter(message, default):

    value = input(
        f"{message} [{default}]: "
    ).strip()

    if value == "":
        return default

    return value


def save_conf_file(
    conf_path,
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

    with open(conf_path, "w") as f:

        f.write(f"center_x = {center_x}\n")
        f.write(f"center_y = {center_y}\n")
        f.write(f"center_z = {center_z}\n\n")

        f.write(f"size_x = {size_x}\n")
        f.write(f"size_y = {size_y}\n")
        f.write(f"size_z = {size_z}\n\n")

        f.write(
            f"exhaustiveness = {exhaustiveness}\n"
        )

        f.write(
            f"num_modes = {num_modes}\n"
        )

        f.write(
            f"energy_range = {energy_range}\n"
        )


# =====================================================
# MAIN
# =====================================================

print("\n====================================")
print(" Receptor Preparation Module")
print("====================================\n")

config = load_project()

project_name = config["project_name"]

project_dir = Path(project_name)

receptor_dir = (
    project_dir /
    "receptor_docking"
)

print("\nInput options:")
print("1. Local PDB file")
print("2. Download PDB from RCSB")

choice = input(
    "\nSelect option (1/2): "
).strip()

pdb_file = receptor_dir / "receptor_original.pdb"

# =====================================================
# LOCAL PDB
# =====================================================

if choice == "1":

    pdb_path = input(
        "\nEnter PDB file path: "
    ).strip()

    pdb_path = Path(pdb_path)

    if not pdb_path.exists():

        raise FileNotFoundError(
            "PDB file not found."
        )

    shutil.copy(
        pdb_path,
        pdb_file
    )

# =====================================================
# DOWNLOAD PDB
# =====================================================

elif choice == "2":

    pdb_id = input(
        "\nEnter PDB code: "
    ).strip().upper()

    download_pdb(
        pdb_id,
        pdb_file
    )

    print(
        f"\nDownloaded {pdb_id}"
    )

else:

    raise ValueError(
        "Invalid option."
    )

# =====================================================
# BOX PARAMETERS
# =====================================================

print("\nDocking Box Parameters")

center_x = ask_parameter(
    "Center X",
    "0"
)

center_y = ask_parameter(
    "Center Y",
    "0"
)

center_z = ask_parameter(
    "Center Z",
    "0"
)

size_x = ask_parameter(
    "Size X",
    "20"
)

size_y = ask_parameter(
    "Size Y",
    "20"
)

size_z = ask_parameter(
    "Size Z",
    "20"
)

exhaustiveness = ask_parameter(
    "Exhaustiveness",
    "8"
)

num_modes = ask_parameter(
    "Number of modes",
    "9"
)

energy_range = ask_parameter(
    "Energy range",
    "3"
)

# =====================================================
# CREATE CONF FILE
# =====================================================

conf_file = receptor_dir / "conf.txt"

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

# =====================================================
# PREPARE RECEPTOR
# =====================================================

receptor_pdbqt = (
    receptor_dir /
    "receptor.pdbqt"
)

command = [

    "mk_prepare_receptor.py",

    "-i",
    str(pdb_file),

    "-o",
    str(receptor_pdbqt)

]

print("\nPreparing receptor...\n")

result = subprocess.run(
    command,
    capture_output=True,
    text=True
)

if result.returncode != 0:

    print(result.stderr)

    raise Exception(
        "Receptor preparation failed."
    )

# =====================================================
# RECEPTOR INFO
# =====================================================

info = {

    "receptor_file":
        "receptor.pdbqt",

    "original_pdb":
        "receptor_original.pdb",

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

# =====================================================
# DONE
# =====================================================

print("\n====================================")
print(" Receptor preparation completed")
print("====================================")

print(
    f"\nPDBQT saved in:\n{receptor_pdbqt}"
)

print(
    f"\nConfiguration saved in:\n{conf_file}"
)