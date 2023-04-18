"""Get a list of all residues in a PDB for the supplemental information."""

import os

def extract_residue_names(filename):
    """
    Extract residue names and their indices from a PDB file.

    Parameters
    ----------
    filename : str
        The name of the PDB file to read.

    Returns
    -------
    list
        A list of formatted residue names with their indices (e.g., MET1, THR2, GLU3).
    """
    residues = []

    with open(filename, "r") as file:
        for line in file:
            if line.startswith("ATOM") or line.startswith("HETATM"):
                residue_name = line[17:20].strip()
                residue_index = line[22:26].strip()
                residue = f"{residue_name}{residue_index}"

                if residue not in residues:
                    residues.append(residue)

    return residues

def write_residues_to_file(residues, output_filename="residues.dat"):
    """
    Write the extracted residues to a file, one residue per line.

    Parameters
    ----------
    residues : list
        A list of formatted residue names with their indices (e.g., MET1, THR2, GLU3).

    output_filename : str, optional
        The name of the output file, by default "residues.dat".
    """
    with open(output_filename, "w") as file:
        for residue in residues:
            file.write(f"{residue}\n")

def list_residues():
    """
    Parses all the residues in the PDB and returns them as a single list.

    """
    pdb_filename = input("Please enter the name of your PDB file: ")
    residues = extract_residue_names(pdb_filename)
    write_residues_to_file(residues)
    print(f"Residue names have been extracted and saved in 'residues.dat'.")

if __name__ == "__main__":
    list_residues()