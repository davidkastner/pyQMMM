import os
import re

def get_xyz_files():
    # List all files in the current working directory
    files = os.listdir('.')
    # Filter files to get only those with a single number in their name ending with .xyz
    xyz_files = [f for f in files if re.match(r'^\d+\.xyz$', f)]
    # Sort files based on the numerical value in their name
    xyz_files.sort(key=lambda x: int(re.match(r'(\d+)', x).group()))
    return xyz_files

def read_xyz_frames(file):
    with open(file, 'r') as f:
        lines = f.readlines()
    frames = []
    i = 0
    while i < len(lines):
        num_atoms = int(lines[i].strip())
        header = lines[i + 1].strip()
        frame = lines[i:i + num_atoms + 2]
        frames.append(frame)
        i += num_atoms + 2
    return frames

def combine_xyz_files(xyz_files, output_file):
    combined_frames = []
    
    for i, file in enumerate(xyz_files):
        frames = read_xyz_frames(file)
        if i < len(xyz_files) - 1:
            combined_frames.extend(frames[:-1])  # Exclude the last frame of the file
        else:
            combined_frames.extend(frames)  # Include all frames of the last file
    
    with open(output_file, 'w') as f:
        for frame in combined_frames:
            f.writelines(frame)

def get_combined_trajectory():
    xyz_files = get_xyz_files()
    if xyz_files:
        combine_xyz_files(xyz_files, 'combined.xyz')
        print("Combined file 'combined.xyz' created successfully.")
    else:
        print("No suitable .xyz files found.")
