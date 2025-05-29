import sys

def translate_pdb(pdb_input, pdb_output, atom_index):
    """
    Translates all PDB frames in a trajectory so that atom `atom_index` in frame 1 is at (0,0,0).
    
    Parameters:
    - pdb_input: str, Path to the input PDB trajectory.
    - pdb_output: str, Path to the output translated PDB trajectory.
    - atom_index: int, The 1-based index of the atom to place at (0,0,0) in frame 1.
    """

    with open(pdb_input, "r") as f:
        pdb_lines = f.readlines()

    translation_vector = None  # Store the translation vector
    translated_lines = []
    frame_count = 0
    model_found = False

    # First pass: Find center atom in frame 1
    for line in pdb_lines:
        if line.startswith("MODEL"):
            frame_count += 1
        if frame_count == 1 and line.startswith(("ATOM", "HETATM")):
            try:
                atom_id = int(line[6:11].strip())  # Extract atom index
                if atom_id == atom_index:
                    # Extract the reference coordinates of atom index in frame 1
                    x_ref = float(line[30:38].strip())
                    y_ref = float(line[38:46].strip())
                    z_ref = float(line[46:54].strip())

                    # Compute translation vector to shift this atom to (0,0,0)
                    translation_vector = (-x_ref, -y_ref, -z_ref)
                    print(f"> Translation vector found: {translation_vector}")
                    break  # Stop searching once the vector is found
            except ValueError as e:
                print(f"> Error processing line: {line.strip()}")
                print(f"> Exception: {e}")
                continue  # Skip malformed lines

    if translation_vector is None:
        print(f"> Error: Atom index {atom_index} not found in frame 1. Exiting.")
        return

    # Second pass: Apply translation to all atoms
    frame_count = 0
    for line in pdb_lines:
        if line.startswith("MODEL"):
            frame_count += 1
            model_found = True
        
        if line.startswith(("ATOM", "HETATM")):
            try:
                # Ensure coordinate fields are not empty
                x_str, y_str, z_str = line[30:38].strip(), line[38:46].strip(), line[46:54].strip()
                if not x_str or not y_str or not z_str:
                    print(f"> Skipping invalid coordinate line: {line.strip()}")
                    translated_lines.append(line)
                    continue

                # Convert to float and apply translation
                x = float(x_str) + translation_vector[0]
                y = float(y_str) + translation_vector[1]
                z = float(z_str) + translation_vector[2]

                # Format the new PDB line
                line = f"{line[:30]}{x:8.3f}{y:8.3f}{z:8.3f}{line[54:]}"
            
            except ValueError as e:
                print(f"> Error processing line: {line.strip()}")
                print(f"> Exception: {e}")
                continue  # Skip malformed lines

        translated_lines.append(line)

    if not model_found:
        print("> Error: No MODEL records found. Ensure the input is a valid PDB trajectory.")
        return

    with open(pdb_output, "w") as f:
        f.writelines(translated_lines)

    print(f"> Translation complete. Output written to {pdb_output}")

if __name__ == "__main__":
    input_pdb = input("What is the name of the PDB you would like to center? ") + ".pdb"
    center_point = int(input("What atom would you like to make the new center of your trajectory (atom number)? ")) # Indexed at 1
    output_pdb = "centered_pdb.pdb"
    translate_pdb(input_pdb, output_pdb, center_point)
