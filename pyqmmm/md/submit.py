import os

# Load queueing system
os.system("module load sge")

# Set path elements
root = os.getcwd()
dirs = sorted(os.listdir(root))
script = "amber_gpu.q"

# Loop over all directories
for dir in dirs:
    # Don't try entering files only directories
    if os.path.isfile(dir):
        continue
    # Make sure the target script is in the directory before entering
    elif os.path.exists(f"{root}/{dir}/{script}"):
        os.chdir(f"{root}/{dir}")
        print(os.getcwd())
        os.system(f"qsub {script}")
        os.chdir(f"{root}")
