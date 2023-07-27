from Bio.PDB import PDBParser, PDBIO
import pandas as pd


def read_info(info_file_path):
    return pd.read_csv(info_file_path)


def read_xyz_last_frame(xyz_file_path):
    with open(xyz_file_path, 'r') as file:
        lines = file.readlines()

    # Determine the number of lines in one frame. The first two lines contain
    # the atom count and a comment, respectively. The rest are atom lines.
    num_atoms = int(lines[0].strip())
    lines_per_frame = num_atoms + 2

    # Get the lines of the final frame. Exclude the atom count and comment lines.
    last_frame_lines = lines[-lines_per_frame + 2:]

    # Check if the last line is blank
    if last_frame_lines[-1].strip() == '':
        # If it is, remove it
        last_frame_lines = last_frame_lines[:-1]

    # Split each line into its components and convert to float
    data = {
        "X": [],
        "Y": [],
        "Z": []
    }
    for line in last_frame_lines:
        _, x, y, z = line.split()
        data["X"].append(float(x))
        data["Y"].append(float(y))
        data["Z"].append(float(z))
        
    return pd.DataFrame(data)


def replace_coordinates_in_pdb(pdb_file_path, xyz_file_path, info_file_path, output_file_path):
    info_df = read_info(info_file_path)
    xyz_df = read_xyz_last_frame(xyz_file_path)

    # Create a PDB parser
    parser = PDBParser()
    structure = parser.get_structure("temp", pdb_file_path)

    model = structure[0]
    atom_index = 0 # to track the current atom number from the xyz file

    for index, row in info_df.iterrows():
        atoms_range = row["ATOMS"].split('-')
        start_atom = int(atoms_range[0])
        end_atom = int(atoms_range[1]) if len(atoms_range) > 1 else start_atom
        residue_id = row['RESID']
        for chain in model:
            for residue in chain:
                if residue.id[1] == residue_id:
                    for atom in residue:
                        # Check if current atom in PDB corresponds to atom in xyz
                        if start_atom <= atom_index + 1 <= end_atom:
                            new_coords = xyz_df.iloc[atom_index][["X", "Y", "Z"]].values
                            atom.set_coord(new_coords)
                            atom_index += 1 # move to next atom in the xyz file

    io = PDBIO()
    io.set_structure(structure)
    io.save(output_file_path)
    print(f"   > Saved new PDB file to {output_file_path}")


if __name__ == "__main__":
    pdb_file_path = "input.pdb"
    xyz_file_path = "input.xyz"
    info_file_path = "info.csv"
    output_file_path = "output.pdb"

    replace_coordinates_in_pdb(pdb_file_path, xyz_file_path, info_file_path, output_file_path)