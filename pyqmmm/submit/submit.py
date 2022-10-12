"""Script for submitting many jobs in the same directory."""

import os
import time

# Load queueing system
os.system("module load sge")

# Set path elements
root = os.getcwd()
dirs = sorted(os.listdir(root))
script = "amber_gpu.q"
output = "constP_run.mdcrd"

# Loop over all directories
for dir in dirs:
    # Don't try entering files only directories
    if os.path.isfile(dir):
        continue
    # Make sure the target script is in the directory before entering
    elif os.path.isfile(f"{root}/{dir}/{output}"):
        print(f"{output} already exists in {dir}.")
        continue
    else:
        os.chdir(f"{root}/{dir}")
        print(os.getcwd())
        os.system(f"qsub {script}")
