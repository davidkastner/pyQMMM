import os
import time

# Load queueing system
os.system("module load sge")

# Set path elements
root = os.getcwd()
dirs = sorted(os.listdir(root))
angle_file_name = "ang.out"
angles_all = []
distance_file_name = "dist.out"
distances_all = []

# Loop over all directories
for dir in dirs:
    # Don't try entering files only directories
    if os.path.isfile(dir):
        continue
    # Check if the angle file exists
    if os.path.isfile(f"{root}/{dir}/{angle_file_name}"):
        print(f"{angle_file_name} exists in {dir}.")
        os.chdir(f"{root}/{dir}")
        print(os.getcwd())
        
        # Get the value of the angle from the second line
        with open(angle_file_name, "r") as angle_file:
            for index,line in enumerate(angle_file):
                if index == 1:
                    angles_all.append(line.split()[1])

    # Check if the distance file exists
    if os.path.isfile(f"{root}/{dir}/{distance_file_name}"):
        print(f"{distance_file_name} exists in {dir}.")
        os.chdir(f"{root}/{dir}")
        print(os.getcwd())
        
        # Get the value of the angle from the second line
        with open(distance_file_name, "r") as distance_file:
            for index,line in enumerate(distance_file):
                if index == 1:
                    distances_all.append(line.split()[1])

os.chdir(f"{root}")
with open("angles_distances.csv", "w") as save_results:
    save_results.write(f"Job,Angle,Distance\n")
    for index,dir in enumerate(dirs):
        save_results.write(f'{dir},{angles_all[index]},{distances_all[index]}\n')





