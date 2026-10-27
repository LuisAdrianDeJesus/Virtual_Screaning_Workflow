# AutoDock Vina Virtual Screening Pipeline

A Python-based, fully automated pipeline for ligand preparation, receptor preparation, virtual screening, and result analysis using AutoDock Vina.

This workflow seamlessly takes you from a raw SMILES CSV file to fully processed, ranked docking results, automated environment provisioning via Conda, and structured outputs with minimal manual intervention.

---

## Features

- **Automated Master Orchestration**: Run the entire pipeline sequentially using `main.py` or run individual modular scripts step-by-step.
- **Dynamic Environment Management**: Automatically creates or updates the Conda environment (`vina_pipeline`) without throwing prefix conflicts.
- **Dynamic Project Path Lookup**: Flexible project configuration resolution (`glob("*/project_config.json")`) allowing execution across any working directory without path errors.
- **Ligand Preparation**: 3D conformer generation using RDKit and legacy PDBQT conversion using Meeko.
- **Receptor Preparation & Open Babel CLI Integration**:
  - Automatically fetches structures from RCSB PDB or processes local PDB files.
  - Cleans structures to retain protein atoms (`ATOM`, `TER`, `END`).
  - Adds polar hydrogens (`-h`) and calculates Gasteiger charges via Open Babel CLI.
  - **Tag Sanitization**: Automatically strips non-rigid tags (`ROOT`, `ENDROOT`, `BRANCH`, `ENDBRANCH`, `TORSDOF`) to enforce rigidity requirements for AutoDock Vina receptors.
- **Virtual Screening with AutoDock Vina**:
  - Live progress monitoring using `tqdm`.
  - Real-time log file capture per ligand.
  - Temporary progress tracking (`screening_progress.csv`).
- **Result Analysis & Reporting**:
  - Complete ranking by binding affinity energy (`screening_results.csv`).
  - Automated extraction of Top 100 hit structures to `top100_structures/`.
  - High-resolution affinity distribution histogram (`affinity_histogram.png`).
  - Comprehensive statistical summary report (`docking_statistics.txt`).

---

## Requirements

### System Requirements
- Python 3.10+
- Conda / Miniconda / Anaconda
- Open Babel (CLI binary `obabel` available in PATH or Conda)
- AutoDock Vina executable (`vina` or `vina.exe` available in PATH or local execution directory)

### Core Dependencies
```text
openbabel
rdkit
meeko
vina
pandas
numpy
requests
biopython
matplotlib
tqdm
```

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your_username/AutoDock-Vina-Virtual-Screening-Pipeline.git
   cd AutoDock-Vina-Virtual-Screening-Pipeline
   ```

2. **Perform Initial Setup**:
   ```bash
   python setup.py
   ```
   *Or simply run `python main.py` to handle setup, Conda environment creation/update, and pipeline execution automatically.*

---

## Workflow & Execution

The complete pipeline can be executed in two ways:

### Option A: Master Automated Execution (Recommended)

Run the master orchestrator to handle environment checks, project initialization, ligand/receptor preparation, virtual screening, and post-processing sequentially:

```bash
python main.py
```

### Option B: Step-by-Step Manual Execution

```text
setup.py
   ↓
prepare_ligands.py
   ↓
prepare_receptor.py
   ↓
docking_screaning.py
   ↓
docking_out.py
```

1. **Project Setup**:
   ```bash
   python setup.py
   ```
   Creates project directory structure, `environment.yml`, `project_config.json`, and `dependencies_report.txt`.

2. **Environment Creation / Activation**:
   ```bash
   conda env create -f environment.yml
   conda activate vina_pipeline
   ```
   *(If the environment already exists: `conda env update -n vina_pipeline -f environment.yml --prune`).*

3. **Prepare Ligands**:
   ```bash
   python prepare_ligands.py
   ```
   Provide a CSV file containing `id_ligand` and `smiles` columns.

4. **Prepare Receptor**:
   ```bash
   python prepare_receptor.py
   ```
   Select local PDB or download via RCSB PDB ID (e.g., `7TLY`), and specify grid box parameters.

5. **Run Virtual Screening**:
   ```bash
   python docking_screaning.py
   ```

6. **Analyze Results**:
   ```bash
   python docking_out.py
   ```

---

## 1. Project Setup (`setup.py`)

Generates project folder hierarchy, configuration metadata, and environment specification.

**Example Input**:
```text
Enter project name: EGFR_screening
```

**Output Hierarchy**:
```text
EGFR_screening/
├── ligands_docking/
├── receptor_docking/
├── docking_poses/
├── docking_log/
├── results/
├── test/
├── environment.yml
└── project_config.json
```

---

## 2. Ligand Preparation (`prepare_ligands.py`)

Converts SMILES strings into 3D low-energy conformers and generates PDBQT ligand files.

**Input CSV format**:
```csv
id_ligand,smiles
LIG001,CCO
LIG002,CCN
LIG003,c1ccccc1
```

**Output**:
```text
EGFR_screening/ligands_docking/
├── LIG001.pdbqt
├── LIG002.pdbqt
└── LIG003.pdbqt

EGFR_screening/ligands_metadata.csv
```

---

## 3. Receptor Preparation (`prepare_receptor.py`)

Processes receptors using Open Babel CLI (`obabel`):
1. Filters protein records (`ATOM`, `TER`, `END`).
2. Adds polar hydrogens (`-h`) and calculates Gasteiger partial charges.
3. Sanitizes forbidden tags (`ROOT`, `ENDROOT`, `BRANCH`, `ENDBRANCH`, `TORSDOF`) to ensure compatibility with AutoDock Vina.

**Output**:
```text
EGFR_screening/receptor_docking/
├── receptor_original.pdb
├── receptor_cleaned.pdb
├── receptor.pdbqt
├── conf.txt
└── receptor_info.json
```

---

## 4. Virtual Screening (`docking_screaning.py`)

Automatically detects prepared ligands, receptor PDBQT, and `conf.txt` settings to execute Vina docking with real-time log tracking.

**Output**:
```text
EGFR_screening/docking_poses/*.pdbqt
EGFR_screening/docking_log/*.log
EGFR_screening/results/screening_summary.csv
```

---

## 5. Result Analysis (`docking_out.py`)

Extracts binding affinities, ranks compounds, copies top pose structures, plots distribution charts, and exports summary statistics.

**Generated Files**:
```text
EGFR_screening/results/
├── screening_results.csv
├── top100_hits.csv
├── docking_statistics.txt
├── affinity_histogram.png
└── top100_structures/
```

### Output Descriptions

- **`screening_results.csv`**: Full dataset ranked by binding affinity (`kcal/mol`).
- **`top100_hits.csv`**: Best 100 binding compounds.
- **`top100_structures/`**: Copied PDBQT pose files for the top 100 compounds.
- **`affinity_histogram.png`**: High-res distribution histogram of binding affinities.
- **`docking_statistics.txt`**: Summary report covering total, successful, failed dockings, best/worst affinity, mean, median, and standard deviation.

---

## Validation Case Study: `test_covid`

A complete test dataset and validation benchmark were conducted in the `test_covid` directory:

- **Target Receptor**: SARS-CoV-2 Main Protease / Mpro (**PDB ID: 7TLY**).
- **Ligand Dataset**: 5 FDA-approved antiviral drugs in SMILES format.
- **Benchmark Results**:
  - `prepare_receptor.py` successfully downloaded `7TLY.pdb`, cleaned HETATM/water molecules, applied Gasteiger charges, and sanitized rigid receptor tags via `obabel`.
  - `prepare_ligands.py` processed 5/5 SMILES into 3D low-energy conformers and generated PDBQT structures via Meeko.
  - `docking_screaning.py` performed docking across all 5 ligands without parsing errors.
  - `docking_out.py` generated affinity rankings, histogram distribution, and statistical metrics inside `test_covid/results/`.

---

## Troubleshooting & Common Solutions

### 1. `PDBQT parsing error: Unknown or inappropriate tag found in rigid receptor. > ROOT`
- **Cause**: Open Babel adds `ROOT` and `ENDROOT` tags during PDB to PDBQT conversion, which AutoDock Vina rejects in rigid receptors.
- **Solution**: `prepare_receptor.py` automatically strips non-rigid tags (`ROOT`, `ENDROOT`, `BRANCH`, `ENDBRANCH`, `TORSDOF`) from `receptor.pdbqt`.

### 2. `FileNotFoundError: project_config.json not found`
- **Cause**: Static path resolution looking only in the working root directory.
- **Solution**: Dynamic lookup `list(Path(".").glob("*/project_config.json"))` was implemented across all scripts (`prepare_ligands.py`, `prepare_receptor.py`, `docking_screaning.py`, `docking_out.py`).

### 3. `CondaValueError: prefix already exists`
- **Cause**: Attempting to recreate an existing Conda environment.
- **Solution**: `main.py` checks environment status (`check_env_exists()`) and runs `conda env update` if `vina_pipeline` already exists.

### 4. `TypeError` in `setup.py`
- **Cause**: Passing concatenated path instead of distinct arguments to `write_project_config`.
- **Solution**: Updated call signature to `write_project_config(project_path, project_name)`.

---

## Directory Structure

```text
project_root/
├── main.py
├── setup.py
├── prepare_ligands.py
├── prepare_receptor.py
├── docking_screaning.py
├── docking_out.py
├── test_covid/
│   ├── ligands_docking/
│   ├── receptor_docking/
│   │   ├── receptor_original.pdb
│   │   ├── receptor_cleaned.pdb
│   │   ├── receptor.pdbqt
│   │   ├── conf.txt
│   │   └── receptor_info.json
│   ├── docking_poses/
│   ├── docking_log/
│   ├── results/
│   │   ├── screening_results.csv
│   │   ├── top100_hits.csv
│   │   ├── docking_statistics.txt
│   │   ├── affinity_histogram.png
│   │   └── top100_structures/
│   ├── ligands_metadata.csv
│   ├── project_config.json
│   └── dependencies_report.txt
└── README.md
```

---

## Future Improvements

- Automatic binding-site detection.
- Multi-core parallel docking.
- Consensus scoring and ADME filtering.
- Molecular descriptor calculation and hit clustering.
- Automated docking report generation (PDF/HTML).

---

## Citation

If you use this pipeline in your research, please cite:
- **AutoDock Vina**: Trott, O., & Olson, A. J. (2010). AutoDock Vina: improving the speed and accuracy of docking.
- **Open Babel**: O'Boyle, N. M., et al. (2011). Open Babel: An open chemical toolbox.
- **RDKit**: Open-source cheminformatics toolkit.
- **Meeko**: Preparation of small molecules for AutoDock.
- **Biopython**: Cock, P. J., et al. (2009). Biopython: freely available Python tools for computational molecular biology.

---

## License

Apache-2.0 License