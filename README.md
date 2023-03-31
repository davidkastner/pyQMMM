![Graphical Summary of README](docs/_static/header.jpg)
pyQMMM
==============================
[//]: # (Badges)
[![GitHub Actions Build Status](https://github.com/davidkastner/pyqmmm/workflows/CI/badge.svg)](https://github.com/davidkastner/pyqmmm/actions?query=workflow%3ACI)
[![Documentation Status](https://readthedocs.org/projects/pyqmmm/badge/?version=latest)](https://pyqmmm.readthedocs.io/en/latest/?badge=latest)

# PyQMMM Package
## Table of Contents
1. **Overview**
    * Introduction
    * Purpose
2. **Installation**
    * Installing pyQMMM
    * Prerequisites
    * File structure
3. **What is included?**
    * Library
    * Utility functions
4. **Documentation**
    * Read the Docs
    * Examples


## 1. Overview
PyQMMM is a package for accelerating structure to simulation workflows for QM, MD, and QM/MM simulations. 
The package contains useful tools for all stages of the QM/MM workflow, from MD, to QM, to multiscale QM/MM.
As the package is designed spcifically for accelerating research in the Kulik group at MIT, 
much of the functionality is built around the Amber-TeraChem interface.
It's current purpose is to act as a utility sandbox for my projects.

---

## 2. Installation
Install the package by running the follow command inside the repository. 
This will perform a developmental version install. 
It is good practice to do this inside of a virtual environment.

### Download the package from GitHub
```
git clone git@github.com:davidkastner/pyQMMM.git
```

### Creating python environment
All the dependencies can be loaded together using the prebuilt environment.yml file.
Compatibility is automatically tested for python versions 3.8 and higher.
Installing all dependencies together has shown to produce more robust installations.

Installing all packages together via the yaml will produce a more robust and efficient environment:
```
cd pyQMMM
conda env create -f environment.yml
source activate pyqmmm
```

```
conda activate pyqmmm
cd pyqmmm
pip install -e
```

### Supporting installations
To have complete access to all pyQMMM functionality, you should also install following dependencies. 
This should be done inside you pyqmmm virtual environment. 
pyQMMM contains automated workflows for modelling in missing loops using Modeller.

```
conda install -c salilab modeller
```

### Developer install of pyQMMM
```
cd pyQMMM
python -m pip install -e .
```

---

## 3. What's included?
pyQMMM is built as both a library and a collection of pre-built scripts.
The scripts aim to accelerate data processesing and automation of calculations.
If a script is not already included for procedure, many of the functions may be useful in building a procedure.

### File structure

```
.
|── cli.py      # Command-line interface entry point
├── docs        # Readthedocs documentation site
├── pyqmmm      # Directory containing pyQMMM modules
│   ├── mm      # Processes for setting MD optimizations prior to QM/MM
│   └── qm      # Processes for running and anlayzing QM cluster model jobs 
└── ...
```

### Command Line Interface
The contents of the library are designed to be navigated through the commandline interface.
Add the following line to your bash.rc
```
alias pyqmmm='python /the/path/to/pyQMMM/cli.py'
```

---

## 4. Documentation
Accurate documentation will always be a high priority for the project.
You can find documentation at the project's Read the Docs.

### Run the following commands to update the ReadTheDocs site
```bash
make clean
make html
```

### Developer guide
### GitHub refresher for those who would like to contribute
#### Push new changes
```bash
git status
git pull
git add .
git commit -m "Change a specific functionality"
git push -u origin main
```

#### Handle merge conflict
```bash
git stash push --include-untracked
git stash drop
git pull
```

#### Copyright
&copy; 2022,  Kulik group at MIT

---

#### Acknowledgements
Author: David W. Kastner
[MolSSi template](https://github.com/molssi/cookiecutter-cms) version 1.6.
