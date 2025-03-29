"""
Deletes specified atoms from a multi-model PDB trajectory.
Also allows the user to sample the trajectory with a stride option.
"""

import os
import sys
import glob

def parse_in_file(in_file_path):
    """
    Parses the .in file and returns a set of atom indices to remove (1-based).
    """
    atoms_to_remove = set()
    with open(in_file_path, 'r') as f:
        for line in f:
            line = line.split('#', 1)[0].strip()
            if not line:
                continue
            tokens = line.split(',')
            for token in tokens:
                token = token.strip()
                if not token:
                    continue
                if '-' in token:
                    try:
                        start, end = map(int, token.split('-'))
                        atoms_to_remove.update(range(start, end + 1))
                    except ValueError:
                        print(f"Warning: Could not parse token '{token}' in {in_file_path}")
                else:
                    try:
                        atoms_to_remove.add(int(token))
                    except ValueError:
                        print(f"Warning: Could not parse token '{token}' in {in_file_path}")
    return atoms_to_remove

def remove_atoms_from_pdb(pdb_input, pdb_output, atoms_to_remove, stride=1):
    """
    Removes specified atoms (1-indexed per frame) from a MODEL-based PDB trajectory.
    Applies stride sampling and writes result to output.
    """
    with open(pdb_input, 'r') as f:
        lines = f.readlines()

    frames = []
    current_frame = []
    in_model = False
    atom_counter = 0
    total_frames = 0
    preamble_lines = []

    for line in lines:
        if line.startswith("MODEL"):
            if total_frames == 0:
                preamble_lines = []  # clear previous top-level lines
            total_frames += 1
            in_model = True
            atom_counter = 0
            current_frame = [line]
        elif line.startswith("ENDMDL"):
            current_frame.extend(["TER\n", "ENDMDL\n"])
            frames.append(current_frame)
            in_model = False
        elif in_model and line.startswith(("ATOM", "HETATM")):
            atom_counter += 1
            if atom_counter not in atoms_to_remove:
                current_frame.append(line)
        elif in_model:
            current_frame.append(line)
        elif not in_model:
            preamble_lines.append(line)

    # Stride selection
    if stride <= 1:
        sampled_frames = frames
    else:
        sampled_frames = frames[::stride]
        if frames[-1] not in sampled_frames:
            sampled_frames.append(frames[-1])

    with open(pdb_output, 'w') as f:
        if preamble_lines:
            f.writelines(preamble_lines)
        for frame in sampled_frames:
            f.writelines(frame)

    print(f"> Process complete: Processed {total_frames} frames, sampled {len(sampled_frames)} frames, and removed specified atoms.")
    print(f"> Output written to {pdb_output}")

def main(in_files, pdb_input, pdb_output):
    in_file = in_files[0]
    atoms_to_remove = parse_in_file(in_file)
    print(f"Atoms to remove: {sorted(atoms_to_remove)}")

    if not os.path.exists(pdb_input):
        print(f"Error: The PDB input file '{pdb_input}' does not exist in the current directory.")
        sys.exit(1)

    stride_input = input("Enter stride (1 for every frame, 2 for every other frame, blank for default 1): ").strip()
    if not stride_input:
        stride = 1
    else:
        try:
            stride = int(stride_input)
            if stride < 1:
                stride = 1
        except ValueError:
            stride = 1

    remove_atoms_from_pdb(pdb_input, pdb_output, atoms_to_remove, stride)

if __name__ == "__main__":
    in_files = glob.glob("delete.in")
    if len(in_files) == 0:
        print("Error: There should be a delete.in in the current directory indicating which atoms to delete.\n")
        print("As an example, its contents could look like this:")
        print("  1-8,104-106,166 # Asn")
        print("  9-16,107-109,168 # Asn")
        print("  59-69,134,135   # Phe\n")
        sys.exit(1)
    pdb_name = input("What is the name of the PDB file you want to delete atoms from without the extension? ")
    pdb_input = f"{pdb_name}.pdb"
    pdb_output = f"{pdb_name}_stripped.pdb"
    main(in_files, pdb_input, pdb_output)