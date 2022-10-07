"""Generate a new trajectory with only selected atoms."""

import os
import sys
import numpy

def get_selection():
    """
    Request the atoms to remove.

    Returns
    -------
    selection : list[int]
        A list of atoms.
    """


    selection = input(f"What atoms would you like to remove (e.g. 1-50,52-60)? ")

    # Convert user input to a list even if it is hyphenated
    temp = [
        (lambda sub: range(sub[0], sub[-1] + 1))(list(map(int, ele.split("-"))))
        for ele in selection.split(",")
    ]
    selection = [int(b) for a in temp for b in a]

    return selection

def remove_atoms(selection: list[int]) -> list[list[str]]:
    """
    Takes an atom selection as input.
    Generates a new trajectory with those atoms removed.
    The final format is the .xyz format.

    Parameters
    ----------
    selection : list[int]
        A list of atoms.
    
    Return
    ------
    new_frames: list[list[str]]
        List of list containing the updated xyz file.

    """
    # Search the current directory for the .xyz file
    xyz_files = [f for f in os.listdir('.') if f.endswith('xyz')]
    if len(xyz_files) != 1:
        raise ValueError('More than one .xyz file found.')
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
        frames = [unsorted_lines[i * n:(i + 1) * n] for i in range((len(unsorted_lines) + n - 1) // n)]
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


def get_pdb_ensemble(new_frames: list[list[str]]):
    """
    Takes an xyz trajectory and a PDB template file.
    Creates a PDB ensemble file.

    Parameters
    ----------
    new_frames: list[list[str]]
        List of list containing the updated xyz file.

    """
    # Read in the template file and get the final atom number
    with open('template.pdb', 'r') as template:
        max_atom = int(template[len(template) - 3].split()[1])

    # Initialize files for reading and writing
    xyz_file = open("new_traj.xyz", 'r').readlines()
    pdb_file = open('new_traj.pdb', 'w')
    my_atom = -1
    pdb_file.write('MODEL        1\n')

    model = 2  # Starts with MODEL 2 as MODEL 1 was written
    for index in range(0, len(xyz_file)):
        if my_atom > 0:
            my_atom += 1
            x, y, z = xyz_file[index].strip('\n').split()[1:5]
            pdb_file.write(template[my_atom][0:30] + x[0:6] + '  '+y[0:6] + '  ' + z[0:6] + '  ' + template[my_atom][54:80] + '\n')
        else:
            # If it is the first line continue
            my_atom += 1
            x, y, z = '', '', ''
        if my_atom > max_atom:
            # Check if we have reached the end of the file
            my_atom = -1
            x, y, z = '', '', ''   
            pdb_file.write('TER\n')
            pdb_file.write('ENDMDL\n')
            pdb_file.write('MODEL        ' + str(i) + '\n')
        model += 1

    return


def traj_atom_filter():
    print("\n.------------------.")
    print("| TRAJ ATOM FILTER |")
    print(".------------------.\n")
    print("Requests the atoms to remove.")
    print("Removes the atoms from the trajectory.")
    print("Writes out a new trajectory.")
    print("Reads in a template file called template.pdb.")

    selection = get_selection()
    new_frames = remove_atoms(selection)
    get_pdb_ensemble(new_frames)


# Executes the function when run as a script
if __name__ == "__main__":
    traj_atom_filter()