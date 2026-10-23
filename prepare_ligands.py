#!/usr/bin/env python3

"""
prepare_ligands.py

Input:
    CSV file containing:
        id_ligand
        smiles

Output:
    ligands_docking/*.pdbqt
    ligands_metadata.csv
"""

import json
import os
import re
import subprocess
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from rdkit import Chem
from rdkit.Chem import AllChem


# ==========================================================
# FUNCTIONS
# ==========================================================

def sanitize_filename(name):

    return re.sub(
        r'[<>:"/\\|?*]',
        "_",
        str(name)
    )


def load_project():

    config_file = Path("project_config.json")

    if not config_file.exists():

        raise FileNotFoundError(
            "project_config.json not found.\n"
            "Run setup.py first."
        )

    with open(config_file) as f:

        return json.load(f)


def create_3d_structure(smiles):

    mol = Chem.MolFromSmiles(smiles)

    if mol is None:
        return None

    mol = Chem.AddHs(mol)

    status = AllChem.EmbedMolecule(
        mol,
        randomSeed=42
    )

    if status != 0:
        return None

    AllChem.UFFOptimizeMolecule(mol)

    return mol


def sdf_to_pdbqt(sdf_file, pdbqt_file):

    command = [

        "mk_prepare_ligand.py",

        "-i",
        str(sdf_file),

        "-o",
        str(pdbqt_file)

    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    return result.returncode == 0


# ==========================================================
# MAIN
# ==========================================================

print("\n========================================")
print(" Ligand Preparation Module")
print("========================================\n")

config = load_project()

project_name = config["project_name"]

project_dir = Path(project_name)

ligands_dir = project_dir / "ligands_docking"

csv_file = input(
    "Enter ligand CSV file path: "
).strip()

csv_file = Path(csv_file)

if not csv_file.exists():

    raise FileNotFoundError(
        f"File not found:\n{csv_file}"
    )

df = pd.read_csv(csv_file)

required_columns = [
    "id_ligand",
    "smiles"
]

for col in required_columns:

    if col not in df.columns:

        raise ValueError(
            f"Missing column: {col}"
        )

metadata = []

success_count = 0
failure_count = 0

print(
    f"\nProcessing {len(df)} ligands...\n"
)

for _, row in tqdm(
    df.iterrows(),
    total=len(df)
):

    ligand_id = sanitize_filename(
        row["id_ligand"]
    )

    smiles = str(
        row["smiles"]
    )

    try:

        mol = create_3d_structure(
            smiles
        )

        if mol is None:

            failure_count += 1

            metadata.append({

                "id_ligand": ligand_id,
                "smiles": smiles,
                "pdbqt_file": None,
                "status": "FAILED"

            })

            continue

        sdf_file = ligands_dir / f"{ligand_id}.sdf"

        writer = Chem.SDWriter(
            str(sdf_file)
        )

        writer.write(mol)
        writer.close()

        pdbqt_file = ligands_dir / f"{ligand_id}.pdbqt"

        success = sdf_to_pdbqt(
            sdf_file,
            pdbqt_file
        )

        sdf_file.unlink(
            missing_ok=True
        )

        if success:

            metadata.append({

                "id_ligand": ligand_id,
                "smiles": smiles,
                "pdbqt_file": pdbqt_file.name,
                "status": "SUCCESS"

            })

            success_count += 1

        else:

            metadata.append({

                "id_ligand": ligand_id,
                "smiles": smiles,
                "pdbqt_file": None,
                "status": "FAILED"

            })

            failure_count += 1

    except Exception:

        metadata.append({

            "id_ligand": ligand_id,
            "smiles": smiles,
            "pdbqt_file": None,
            "status": "FAILED"

        })

        failure_count += 1


metadata_df = pd.DataFrame(metadata)

metadata_file = (
    project_dir /
    "ligands_metadata.csv"
)

metadata_df.to_csv(
    metadata_file,
    index=False
)

print("\n========================================")
print(" Ligand Preparation Finished")
print("========================================")

print(f"\nSuccessful ligands : {success_count}")
print(f"Failed ligands     : {failure_count}")

print(
    f"\nPDBQT files saved in:\n{ligands_dir}"
)

print(
    f"\nMetadata saved in:\n{metadata_file}"
)