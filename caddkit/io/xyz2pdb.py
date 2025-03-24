import time

def xyz2pdb_traj(xyz_name, pdb_name, pdb_template) -> None:
    """
    Converts an XYZ trajectory file into a valid PDB trajectory file using a PDB template.

    Notes:
    - Assumes XYZ format: first line = number of atoms, second line = title, followed by atomic coordinates.
    - Uses a template PDB for residue information.
    - Assumes all frames in the XYZ file have the same number of atoms as the PDB template.
    - Adds MODEL and ENDMDL records for PDB trajectory compatibility.
    """

    start_time = time.time()  # Start time for execution speed reporting

    # Read input files
    with open(xyz_name, "r") as f:
        xyz_lines = f.readlines()
    with open(pdb_template, "r") as f:
        pdb_lines = f.readlines()

    # Get the number of atoms from the PDB template
    try:
        max_atom = int(pdb_lines[-3].split()[1])  # Get max_atom from PDB numbering
    except (IndexError, ValueError):
        print("> Error: Template PDB file does not have expected atom numbering.")
        return

    # Open output PDB file
    with open(pdb_name, "w") as new_file:
        line_count = 0  # Track current line in XYZ file
        frame_count = 0  # Track the number of frames processed

        while line_count < len(xyz_lines):
            try:
                num_atoms = int(xyz_lines[line_count].strip())  # Read number of atoms
            except ValueError:
                print(f"> Error at line {line_count+1}: Expected number of atoms but got '{xyz_lines[line_count].strip()}'")
                return

            line_count += 2  # Skip the title/comment line
            frame_count += 1

            # Write MODEL record
            new_file.write(f"MODEL     {frame_count}\n")

            # Process atom lines
            for atom in range(num_atoms):
                try:
                    parts = xyz_lines[line_count].strip().split()
                    if len(parts) < 4:
                        raise ValueError(f"Incomplete XYZ line: {xyz_lines[line_count].strip()}")
                    x, y, z = parts[1:4]  # Extract XYZ coordinates
                except Exception as e:
                    print(f"> Script died at line {line_count+1} -> '{xyz_lines[line_count].strip()}'")
                    print(f"> Error: {e}")
                    return

                # Get corresponding PDB line
                try:
                    pdb_line = pdb_lines[atom]
                except IndexError:
                    print(f"> Error: Atom index {atom+1} out of range in PDB template.")
                    return

                # Write new PDB line with updated coordinates
                new_file.write(
                    f"{pdb_line[:30]}{float(x):8.3f}{float(y):8.3f}{float(z):8.3f}{pdb_line[54:]}"
                )

                line_count += 1

            # Write ENDMDL record at the end of the frame
            new_file.write("TER\n")
            new_file.write("ENDMDL\n")

    total_time = round(time.time() - start_time, 3)  # Measure execution time
    print(
        f"""
        \t----------------------------ALL RUNS END----------------------------
        \tRESULT: Converted {xyz_name} to {pdb_name}.
        \tOUTPUT: Generated {pdb_name} in the current directory.
        \tFRAMES PROCESSED: {frame_count}
        \tTIME: Total execution time: {total_time} seconds.
        \t--------------------------------------------------------------------\n
        """
    )

if __name__ == "__main__":
    # Run the conversion
    xyz_traj = input("What is the name or your xyz trajectory without the extension? ") + ".xyz"
    template = input("What is the name or your PDB template without the extension? ") + ".pdb"
    output_pdb = "pdb_trajectory.pdb"
    xyz2pdb_traj(xyz_traj, output_pdb, template)
