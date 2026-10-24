# AutoDock Vina Virtual Screening Pipeline

A Python-based pipeline for ligand preparation, receptor preparation, virtual screening, and result analysis using AutoDock Vina.

This workflow allows users to move from a ligand CSV file containing SMILES structures to ranked docking results with minimal manual intervention.

---

# Features

- Automatic project setup
- Ligand preparation from SMILES
- 3D conformer generation using RDKit
- Ligand conversion to PDBQT using Meeko
- Receptor preparation from:
  - Local PDB files
  - RCSB PDB IDs
- AutoDock Vina virtual screening
- Real-time docking progress monitoring
- Automatic log generation
- Ranked docking results
- Top 100 hit extraction
- Affinity distribution plots
- Statistical summary reports

---

# Requirements

## Python

Python 3.10+

## AutoDock Vina

Install AutoDock Vina and ensure that the executable is available in your system PATH.

Test your installation:

```bash
vina --version
```

## Python Packages

Required packages:

```text
pandas
numpy
rdkit
meeko
requests
biopython
matplotlib
tqdm
```

The setup script installs missing dependencies automatically.

---

# Installation

Clone the repository:

```bash
git clone https://github.com/your_username/AutoDock-Vina-Virtual-Screening-Pipeline.git

cd AutoDock-Vina-Virtual-Screening-Pipeline
```

Run setup:

```bash
python setup.py
```

---

# Workflow

The complete workflow consists of four steps:

```text
setup.py
      ↓
prepare_ligands.py
      ↓
prepare_receptor.py
      ↓
docking_screening.py
      ↓
docking_output.py
```

---

# 1. Project Setup

Run:

```bash
python setup.py
```

Example:

```text
Enter project name:

EGFR_screening
```

Output:

```text
EGFR_screening/

├── ligands_docking/
├── receptor_docking/
├── docking_poses/
├── docking_log/
└── results/
```

---

# 2. Ligand Preparation

Prepare ligands from a CSV file.

Run:

```bash
python prepare_ligands.py
```

Input CSV format:

```csv
id_ligand,smiles
LIG001,CCO
LIG002,CCN
LIG003,c1ccccc1
```

Output:

```text
ligands_docking/

├── LIG001.pdbqt
├── LIG002.pdbqt
└── LIG003.pdbqt
```

Metadata file:

```text
ligands_metadata.csv
```

---

# 3. Receptor Preparation

Run:

```bash
python prepare_receptor.py
```

Input options:

### Option 1

Use a local PDB file

```text
protein.pdb
```

### Option 2

Download structure directly from RCSB

Example:

```text
6LU7
```

Docking parameters:

```text
center_x
center_y
center_z

size_x
size_y
size_z

exhaustiveness
num_modes
energy_range
```

Output:

```text
receptor_docking/

├── receptor_original.pdb
├── receptor.pdbqt
├── conf.txt
└── receptor_info.json
```

---

# 4. Virtual Screening

Run:

```bash
python docking_screening.py
```

The script automatically detects:

```text
receptor_docking/receptor.pdbqt
receptor_docking/conf.txt
ligands_docking/*.pdbqt
```

Output:

```text
docki*g_poses/
docking_log/
```

For eac* ligand:

```text
ligand_out.pdbqt*ligand.log
```

The Vina output is*shown in the terminal and saved to*the corresponding log file.

---

* 5. Result Analysis

Run:

```bash*python docking_output.py
```

Gene*ated files:

```text
results/

├──*screening_results.csv
├── top100_h*ts.csv
├── docking_statistics.txt
*── affinity_histogram.png
└── top1*0_structures/
```

---

# Output F*les

## screening_results.csv

Con*ains all ligands ranked by binding*affinity.

Example:

```csv
Rank,i*_ligand,smiles,Affinity_energy
1,L*G017,CCN,-11.2
2,LIG165,CCC,-10.9
*,LIG054,COC,-10.7
```

## top100_h*ts.csv

Contains the 100 highest-r*nked compounds.

## top100_structu*es/

Contains the docking poses co*responding to the best 100 compoun*s.

## affinity_histogram.png

Dis*ribution of docking scores.

## do*king_statistics.txt

Summary stati*tics:

- Total ligands
- Successfu* dockings
- Failed dockings
- Best*affinity
- Worst affinity
- Mean a*finity
- Median affinity
- Standar* deviation

---

# Recommended Dir*ctory Structure

```text
project/
*├── ligands_docking/
├── receptor_*ocking/
├── docking_poses/
├── doc*ing_log/
├── results/

├── ligands*metadata.csv
├── project_config.js*n
└── dependencies_report.txt
```
*---

# Test Dataset

A small test *ataset is recommended before runni*g large-scale virtual screening ca*paigns.

Example:

```csv
id_ligan*,smiles
ASPIRIN,CC(=O)OC1=CC=CC=C1*(=O)O
CAFFEINE,CN1C=*C2=C1C*=O)N(C(=O)N*C)C
IBUPROFEN*CC(C)CC1=CC=C*C=C1)C(C)*(=O)O
```

---

# Future Improveme*ts

Planned features:

- Automatic*binding-site detection
- Multi-cor* parallel*docking
- Consensus scoring
- ADME* filtering
- Molecular descriptor *alculation
- Clustering of top*hits
- Docking report generation (*DF/HTML)
- Support for AutoDock-G*U

---

# Citation

If you use thi* workflow in your research, please*cite:

- AutoDock Vina
- RDKit
- M*eko
- Biopy*hon

---

# License

MIT License
`*``*