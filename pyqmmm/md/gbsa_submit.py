"""Prepares a mmGBSA job and submits it to the SLURM queue"""

import pyqmmm.md.amber_toolkit


# Check if stripped .mdcrd and prmtop exist

# If not end with an error

# Else submit the GBSA calculation
pyqmmm.md.amber_toolkit.gbsa_script(protein_id, ligand_name, ligand_index_minus_one, stride, cpus=16)


