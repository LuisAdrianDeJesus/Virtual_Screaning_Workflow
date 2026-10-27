#!/usr/bin/env python3

"""
prepare_ligands.py

Prepare ligands for AutoDock Vina virtual screening.

Input:
    CSV file with columns:

        id_ligand
        smiles

Output:
    ligands_docking/
        *.pdbqt

    ligands_metadata.csv
"""

import json
import re
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from rdkit import Chem
from rdkit.Chem import AllChem

from meeko import MoleculePreparation
from meeko import PDBQTWriterLegacy


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


def sanitize_filename(name):

    return re.sub(
        r'[<>:"/\\|?*]',
        "_",
        str(name)
    )


def smiles_to_mol(smiles):

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

    AllChem.UFFOptimizeMolecule(
        mol
    )

    return mol

def mol_to_pdbqt(mol, output_file):

    preparator = MoleculePreparation()

    mol_setups = preparator.prepare(mol)

    result = PDBQTWriterLegacy.write_string(
        mol_setups[0]
    )

    # Meeko 0.8 devuelve una tupla
    if isinstance(result, tuple):

        pdbqt_string = result[0]

    else:

        pdbqt_string = result

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(pdbqt_string)



# ==========================================================
# START
# ==========================================================

print("\n====================================")
print(" Ligand Preparation")
print("====================================\n")

config = load_project()

project_dir = Path(
    config["project_path"]
)

ligands_dir = (
    project_dir /
    "ligands_docking"
)

csv_file = input(
    "Enter ligand CSV file path: "
).strip()

csv_file = Path(
    csv_file
)

if not csv_file.exists():

    raise FileNotFoundError(
        f"{csv_file} not found."
    )

# ==========================================================
# LOAD CSV
# ==========================================================

df = pd.read_csv(
    csv_file
)

required_columns = [

    "id_ligand",
    "smiles"

]

for col in required_columns:

    if col not in df.columns:

        raise ValueError(
            f"Missing required column: {col}"
        )

# ==========================================================
# PROCESS LIGANDS
# ==========================================================

metadata = []

success = 0
failed = 0

print(
    f"\nPreparing {len(df)} ligands...\n"
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

        mol = smiles_to_mol(
            smiles
        )

        if mol is None:

            failed += 1

            metadata.append({

                "id_ligand":
                    ligand_id,

                "smiles":
                    smiles,

                "pdbqt_file":
                    None,

                "status":
                    "FAILED"

            })

            continue

        pdbqt_file = (
            ligands_dir /
            f"{ligand_id}.pdbqt"
        )

        mol_to_pdbqt(
            mol,
            pdbqt_file
        )

        metadata.append({

            "id_ligand":
                ligand_id,

            "smiles":
                smiles,

            "pdbqt_file":
                pdbqt_file.name,

            "status":
                "SUCCESS"

        })

        success += 1

    except Exception as e:

        failed += 1

        print(
            f"\nERROR: {ligand_id}"
        )

        print(
            str(e)
        )

        metadata.append({

            "id_ligand":
                ligand_id,

            "smiles":
                smiles,

            "pdbqt_file":
                None,

            "status":
                "FAILED"

        })

# ==========================================================
# SAVE METADATA
# ==========================================================

metadata_df = pd.DataFrame(
    metadata
)

metadata_file = (
    project_dir /
    "ligands_metadata.csv"
)

metadata_df.to_csv(

    metadata_file,

    index=False

)

# ==========================================================
# SUMMARY
# ==========================================================

print("\n====================================")
print(" Ligand Preparation Completed")
print("====================================")

print(
    f"\nSuccessful ligands: {success}"
)

print(
    f"Failed ligands: {failed}"
)

print(
    f"\nPDBQT files saved in:\n{ligands_dir}"
)

print(
    f"\nMetadata file:\n{metadata_file}"
)

print("\nDone.\n")