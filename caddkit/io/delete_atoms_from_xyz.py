"""
Deletes specified atoms from a single XYZ or an XYZ trajectory.
Also allows the user to sample the trajectory with a stride option.
"""

import os
import glob
import sys

def parse_in_file(in_file_path):
    """
    Parses the .in file and returns a set of atom indices to remove.
    The .in file can contain ranges (e.g. "1-8") and single numbers,
    and any text after a '#' is ignored.
    """
    atoms_to_remove = set()
    with open(in_file_path, 'r') as f:
        for line in f:
            # Remove comment (anything after '#') and trim whitespace.
            line = line.split('#', 1)[0].strip()
            if not line:
                continue
            # Split tokens by comma.
            tokens = line.split(',')
            for token in tokens:
                token = token.strip()
                if not token:
                    continue
                if '-' in token:
                    try:
                        start, end = token.split('-')
                        start = int(start)
                        end = int(end)
                        # Add inclusive range.
                        atoms_to_remove.update(range(start, end + 1))
                    except ValueError:
                        print(f"Warning: Could not parse token '{token}' in {in_file_path}")
                else:
                    try:
                        atoms_to_remove.add(int(token))
                    except ValueError:
                        print(f"Warning: Could not parse token '{token}' in {in_file_path}")
    return atoms_to_remove

def remove_atoms_from_xyz(xyz_input, xyz_output, atoms_to_remove, stride=1):
    """
    Reads an xyz trajectory from xyz_input, removes atoms whose 1-indexed order
    (in each frame) is in atoms_to_remove, updates the atom count per frame,
    applies the stride sampling, and writes the cleaned frames to xyz_output.
    
    Each frame is assumed to consist of:
      - A first line with an integer (total number of atoms)
      - A title/comment line (left unchanged)
      - Followed by that many atom coordinate lines.
      
    The stride indicates that the output should include:
      - The first frame,
      - Every stride-th frame from the trajectory,
      - And the last frame (if not already included).
    """
    with open(xyz_input, 'r') as f:
        lines = f.readlines()

    frames = []
    index = 0
    while index < len(lines):
        try:
            num_atoms = int(lines[index].strip())
        except ValueError:
            print(f"Error reading number of atoms at line {index + 1}")
            sys.exit(1)
        title_line = lines[index + 1]
        atom_lines = lines[index + 2 : index + 2 + num_atoms]
        remaining_atom_lines = []
        # Assume atoms are ordered from 1 to num_atoms.
        for i, atom_line in enumerate(atom_lines, start=1):
            if i in atoms_to_remove:
                continue  # Skip this atom.
            remaining_atom_lines.append(atom_line)
        new_num_atoms = len(remaining_atom_lines)
        frame_lines = []
        frame_lines.append(f"{new_num_atoms}\n")
        frame_lines.append(title_line)
        frame_lines.extend(remaining_atom_lines)
        frames.append(frame_lines)
        index += 2 + num_atoms

    total_frames = len(frames)
    # Apply stride sampling.
    if stride <= 1:
        sampled_frames = frames
    else:
        sampled_frames = frames[::stride]
        if frames[-1] not in sampled_frames:
            sampled_frames.append(frames[-1])

    with open(xyz_output, 'w') as f:
        for frame in sampled_frames:
            f.writelines(frame)

    print(f"> Process complete: Processed {total_frames} frames, sampled {len(sampled_frames)} frames, and removed specified atoms.")
    print(f"> Output written to {xyz_output}")

def main():
    # Look for a single delete.in file in the current directory.
    in_files = glob.glob("delete.in")
    if len(in_files) == 0:
        print("Error: There should be a delete.in in the current directory.\n")
        print("As an example, its contents could look like this:")
        print("  1-8,104-106,166 # Asn")
        print("  9-16,107-109,168 # Asn")
        print("  59-69,134,135   # Phe\n")
        sys.exit(1)

    in_file = in_files[0]
    atoms_to_remove = parse_in_file(in_file)
    print(f"Atoms to remove: {sorted(atoms_to_remove)}")

    xyz_name = input("What is the name of your XYZ trajectory without the extension? ")
    xyz_input = f"{xyz_name}.xyz"
    xyz_output = f"{xyz_name}_stripped.xyz"

    if not os.path.exists(xyz_input):
        print(f"Error: The xyz input file '{xyz_input}' does not exist in the current directory.")
        sys.exit(1)

    stride_input = input("Enter stride (1 for every frame, 2 for every other frame, etc): ").strip()
    if not stride_input:
        stride = 1
    else:
        try:
            stride = int(stride_input)
            if stride < 1:
                stride = 1
        except ValueError:
            stride = 1

    remove_atoms_from_xyz(xyz_input, xyz_output, atoms_to_remove, stride)

if __name__ == "__main__":
    main()
