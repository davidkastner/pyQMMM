![Graphical Summary of README](docs/_static/header.jpg)
pyQMMM
==============================
[//]: # (Badges)
[![GitHub Actions Build Status](https://github.com/davidkastner/pyqmmm/workflows/CI/badge.svg)](https://github.com/davidkastner/pyqmmm/actions?query=workflow%3ACI)
[![Documentation Status](https://readthedocs.org/projects/pyqmmm/badge/?version=latest)](https://pyqmmm.readthedocs.io/en/latest/?badge=latest)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/davidkastner/pyQMMM.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/davidkastner/pyQMMM/context:python)
[![codecov](https://codecov.io/gh/davidkastner/pyQMMM/branch/master/graph/badge.svg)](https://codecov.io/gh/davidkastner/pyQMMM/branch/master)

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


## Overview
PyQMMM is a package of useful utility functions for accelerating structure to simulation workflows for QM/MM simulations. 
The package contains useful tools for all stages of the QM/MM workflow, form MD, to QM, to multiscale QM/MM.
As the package is designed spcifically for accelerating research in the Kulik group at MIT, 
much of the functionality is built around the Amber-TeraChem interface. 
However, we aim for software agnostic functionality. 

The initial limited goal of the package is serve as a repository sandbox for useful scripts used in my molecular modelling workflows.
However, eventually, I would hope to grow PyQMMM into a robust tool for automating the job preparation and analysis of QM/MM simulations.

---

## Installation
Install the package by running the follow command inside the repository. 
This will perform a developmental version install. 
It is good practice to do this inside of a virtual environment.

```
conda create -n pyqmmm
conda activate pyqmmm
cd pyqmmm
pip install -e
```

To have complete access to all pyQMMM functionality, you should install the following dependencies. 
This should be done inside you pyqmmm virtual environment. 

```
conda install -c conda-forge matplotlib
conda install -c anaconda pandas
conda install -c anaconda configparser
conda install -c salilab modeller
```

### File structure

```
.
├── devtools
├── docs
├── pyqmmm
│   ├── md      # Processes for setting MD optimizations prior to QM/MM
│   ├── ml      # Machine learning analysis scripts
│   ├── qm      # Processes for running and anlayzing QM cluster model jobs 
│   └── qmmm    # Process for automating QM/MM jobs with TeraChem and Amber
└── ...
```

---

## What's included?
pyQMMM is built as both a library and a collection of pre-built scripts.
The scripts are prepared to accelerate data processesing and automation of calculations.
If a script is not already included for procedure, many of the functions may be useful in building a procedure.


---

## Documentation
While pyQMMM is still underconstrunction and its functionality is limited,
detailed and accurate documentation will always be a high priority for the project.
You can find documentation at the project's Read the Docs.
You can also find examples of some of the more used functions, 
such as quickCSA.py, in the the docs/examples folder.

#### Copyright

&copy; 2022,  Kulik group at MIT

---

#### Acknowledgements
Author: David W. Kastner
[MolSSi template](https://github.com/molssi/cookiecutter-cms) version 1.6.
