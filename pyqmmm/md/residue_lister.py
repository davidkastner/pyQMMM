"""Get a list of all residues in a PDB for the supplemental information."""

import os

# Mapping of three-letter amino acid codes to one-letter codes
three_to_one = {
    "ALA": "A", "CYS": "C", "ASP": "D", "GLU": "E", "PHE": "F",
    "GLY": "G", "HIS": "H", "ILE": "I", "LYS": "K", "LEU": "L",
    "MET": "M", "ASN": "N", "PRO": "P", "GLN": "Q", "ARG": "R",
    "SER": "S", "THR": "T", "VAL": "V", "TRP": "W", "TYR": "Y"
}

def extract_residue_names(filename, use_one_letter):
    """
    Extract residue names and their indices from a PDB file.

    Parameters
    ----------
    filename : str
        The name of the PDB file to read.
    use_one_letter : bool
        Whether to use one-letter amino acid codes instead of three-letter codes.

    Returns
    -------
    list
        A list of formatted residue names with their indices (e.g., MET1, THR2, GLU3 or M1, T2, E3).

    """
    residues = []

    with open(filename, "r") as file:
        for line in file:
            if line.startswith("ATOM") or line.startswith("HETATM"):
                residue_name = line[17:20].strip()
                residue_index = line[22:26].strip()

                if use_one_letter:
                    residue_name = three_to_one.get(residue_name, "X")  # Default to 'X' if not in mapping

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

    # Ask the user whether to use one-letter codes or three-letter codes
    use_one_letter = input("Do you want to use one-letter amino acid codes? (yes/no): ").strip().lower() == "yes"

    residues = extract_residue_names(pdb_filename, use_one_letter)
    write_residues_to_file(residues)

    code_type = "one-letter" if use_one_letter else "three-letter"
    print(f"Residue names ({code_type} codes) have been extracted and saved in 'residues.dat'.")

if __name__ == "__main__":
    list_residues()
