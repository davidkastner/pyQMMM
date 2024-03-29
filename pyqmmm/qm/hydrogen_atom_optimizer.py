"""Creates a list with the indices of all heavy atoms in an xyz."""

import os
import sys


def get_xyz_file():
    """
    Check the current dir for an .xyz file and let user know if one exists.

    Returns
    -------
    file : str
        The name of the .xyz that we will loop through.
    """
    files = os.listdir(".")
    count = 0
    current_file = ""
    for file in files:
        if ".xyz" in file:
            count += 1
            current_file = file
    if count > 1:
        print("   > More than one .xyz found")
        sys.exit()
    print(f"   > Using {current_file}")
    return current_file


def find_heavy_atoms(file):
    """
    Search the user's xyz file for the index of all hydrogen atoms.

    Parameters
    ----------
    file : str
        The name of the .xyz that we will loop through.
    """
    heavy_atoms_list = []
    with open(file, "r") as xyz_file:
        for index, line in enumerate(list(xyz_file)[2:]):
            if line[0] != "H":
                heavy_atoms_list.append(str(index + 1))
    heavy_atoms = ",".join(heavy_atoms_list)
    print(heavy_atoms)


def hydrogen_atom_optimizer():
    # Introduce user to Hydro Optimizer functionality
    print("\n.-------------------------.")
    print("| HYDROGEN ATOM OPTIMIZER |")
    print(".-------------------------.\n")
    print("Takes an .xyz file and returns the index of all hydrogens as a list.")
    print("This script will search the current directory for the following input:")
    print("+ An xyz file")
    print("------------------------\n")

    # Gets the name of the xyz file in the current directory
    file = get_xyz_file()
    # Gets a list of the heavy atoms to freeze
    find_heavy_atoms(file)


if __name__ == "__main__":
    hydrogen_atom_optimizer()
