"""Run CPPTraj analysis across all MD replicates."""

import os
import shutil

# Load queueing system
os.system("module load sge")

# Set path elements
root = os.getcwd()
dirs = sorted(os.listdir(root))
add_script = "cpptraj.in"

# Loop over all directories
for dir in dirs:
    # Don't try entering files only directories
    if os.path.isfile(dir):
        continue
    else:
        shutil.copyfile(f"{root}/{add_script}", f"{root}/{dir}/{add_script}")
        os.chdir(f"{root}/{dir}")
        os.system("module load amber/18")
        os.system("cpptraj -i cpptraj.in")
    
