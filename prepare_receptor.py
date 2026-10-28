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
import sys
from pathlib import Path

from project_utils import load_project_from_cli

import requests

# ==========================================================
# FUNCTIONS
# ==========================================================

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


def get_preparation_command(original_pdb, receptor_pdbqt):
    """
    Detects available meeko preparation command or uses python module fallback.
    """
    for tool in ["mk_prepare_receptor", "mk_prepare_receptor.py"]:
        if shutil.which(tool):
            return [tool, "-i", str(original_pdb), "-o", str(receptor_pdbqt)]
    
    # Fallback to python module execution if executable is not in PATH
    return [sys.executable, "-m", "meeko.cli.mk_prepare_receptor", "-i", str(original_pdb), "-o", str(receptor_pdbqt)]


# ==========================================================
# START
# ==========================================================

print("\n====================================")
print(" Receptor Preparation")
print("====================================\n")

config = load_project_from_cli("prepare_receptor.py")

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
# PREPARE RECEPTOR (Flujo Profesional con Open Babel CLI + Clean)
# ==========================================================

print(
    "\nPreparing receptor with Open Babel CLI (Polar hydrogens, cleaning, Gasteiger charges)..."
)

receptor_pdbqt = (
    receptor_dir /
    "receptor.pdbqt"
)

cleaned_pdb = receptor_dir / "receptor_cleaned.pdb"

preparation_code = f"""
import sys
import os
import subprocess

input_pdb_path = r"{original_pdb.resolve().as_posix()}"
cleaned_pdb_path = r"{cleaned_pdb.resolve().as_posix()}"
output_pdbqt_path = r"{receptor_pdbqt.resolve().as_posix()}"

# 1. Limpiar el PDB original: conservar únicamente los átomos proteicos (ATOM) y descartar HETATM
lines_out = []
with open(input_pdb_path, 'r', encoding='utf-8', errors='ignore') as fin:
    for line in fin:
        if line.startswith("ATOM") or line.startswith("TER") or line.startswith("END"):
            lines_out.append(line)

with open(cleaned_pdb_path, 'w', encoding='utf-8') as fout:
    fout.writelines(lines_out)

# 2. Ejecutar Open Babel por línea de comandos
try:
    cmd = [
        "obabel",
        cleaned_pdb_path,
        "-O",
        output_pdbqt_path,
        "-h",
        "-xr",
        "--partialcharge",
        "gasteiger"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Error en obabel: {{result.stderr}}")
        
    # 3. Eliminar etiquetas no compatibles con receptores rígidos en AutoDock Vina (ROOT, ENDROOT, BRANCH, ENDBRANCH)
    with open(output_pdbqt_path, 'r', encoding='utf-8') as f_in:
        pdbqt_lines = f_in.readlines()
        
    forbidden_tags = ("ROOT", "ENDROOT", "BRANCH", "ENDBRANCH", "TORSDOF")
    clean_pdbqt = [line for line in pdbqt_lines if not line.startswith(forbidden_tags)]
    
    with open(output_pdbqt_path, 'w', encoding='utf-8') as f_out:
        f_out.writelines(clean_pdbqt)

    print("Receptor procesado y limpiado exitosamente para AutoDock Vina.")
except Exception as e:
    print(f"Error durante la preparación: {{e}}", file=sys.stderr)
    sys.exit(1)
"""

command = [
    sys.executable,
    "-c",
    preparation_code
]

result = subprocess.run(
    command,
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print(result.stderr)
    raise RuntimeError("Receptor preparation failed.")
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