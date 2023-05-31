"""Generate a new trajectory with only selected atoms."""

import os
import sys
import numpy
from typing import List


def get_selection():
    """
    Request the atoms to remove.

    Returns
    -------
    selection : list[int]
        A list of atoms.

    """
    selection = input(f"   > What atoms would you like to remove (e.g. 1-50,52-60)? ")

    # Convert user input to a list even if it is hyphenated
    temp = [
        (lambda sub: range(sub[0], sub[-1] + 1))(list(map(int, ele.split("-"))))
        for ele in selection.split(",")
    ]
    selection = [int(b) for a in temp for b in a]

    return selection


def remove_atoms(selection: List[int]) -> List[List[str]]:
    """
    Removes an atom and creates a new xyz.

    Takes an atom selection as input.
    Generates a new trajectory with those atoms removed.
    The final format is the .xyz format.

    Parameters
    ----------
    selection : list[int]
        A list of atoms.

    """
    # Search the current directory for the .xyz file
    xyz_files = [f for f in os.listdir(".") if f.endswith("xyz")]
    if len(xyz_files) != 1:
        raise ValueError("   > More than one .xyz file found.")
    xyz_file = xyz_files[0]

    # Lines in the molecule plus the header lines
    with open(xyz_file) as traj_orig:
        section_length = int(traj_orig.readline().strip()) + 2

    with open(xyz_file) as traj_orig:
        # Convert file to list of lists
        unsorted_lines: list[str] = []
        for line in traj_orig:
            stripped_line = line.strip()
            unsorted_lines.append(stripped_line)

        # Place each frame in its own list
        n = section_length
        frames = [
            unsorted_lines[i * n : (i + 1) * n]
            for i in range((len(unsorted_lines) + n - 1) // n)
        ]
        new_frames: list[list[str]] = []

        # Loop over the frames and delete all rows that match the selection
        for frame in frames:
            for index in sorted(selection, reverse=True):
                index += 1
                del frame[index]
            # Update the header line to match the new atom count
            frame[0] = str(int(frame[0]) - len(selection))
            new_frames.append(frame)

    # Write out the new xyz file
    new_traj_out = open("new_traj.xyz", "w")
    for frame in new_frames:
        for line in frame:
            new_traj_out.write(line + "\n")

    return new_frames


def get_pdb_ensemble():
    """
    Takes an xyz trajectory and a PDB template file.
    Creates a PDB ensemble file.

    """
    # Initialize files
    template = open("template.pdb", "r").readlines()
    xyz_file = open("new_traj.xyz", "r").readlines()
    pdb_file = open("new_traj.pdb", "w")

    # Initialize count variables
    max_atom = int(
        open("template.pdb", "r").readlines()[-1].split()[1]
    )  # Final atom number
    atom = -1  # Account for two header lines in the xyz
    model = 2  # MODEL 1 was already written

    pdb_file.write("MODEL        1\n")
    for index, line in enumerate(xyz_file):
        # If we have passed the xyz header lines
        if atom > 0:
            x, y, z = line.strip("\n").split()[1:5]
            pdb_file.write(
                f"{template[atom - 1][0:32]}{x[0:6]}  {y[0:6]}  {z[0:6]}{template[atom - 1][54:80]}\n"
            )
            atom += 1
        # If it is the first line continue
        else:
            atom += 1
        # If we have reached the end of the file
        if atom > max_atom:
            pdb_file.write(f"TER\nENDMDL\nMODEL        {model}\n")
            atom = -1
            model += 1


def traj_atom_filter():
    print("\n.------------------.")
    print("| TRAJ ATOM FILTER |")
    print(".------------------.\n")
    print("Requests the atoms to remove.")
    print("Removes the atoms from the trajectory.")
    print("Writes out a new trajectory.")
    print("Reads in a template file called template.pdb.\n")

    if not os.path.exists("new_traj.xyz"):
        selection = get_selection()
        remove_atoms(selection)
    get_pdb_ensemble()


# Executes the function when run as a script
if __name__ == "__main__":
    traj_atom_filter()
