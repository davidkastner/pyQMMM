"""Reverses an xyz trajectory, for example if it was run backwards for better convergence."""

import os

def read_xyz(file):
    """
    Read an xyz trajectory file and return a list of frames.

    Parameters
    ----------
    file : str
        The name of the xyz file to read.

    Returns
    -------
    frames : list
        A list of tuples containing the number of atoms, title, and atom lines for each frame.
    """
    frames = []
    with open(file, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            line = line.strip()
            if not line:  # Skip empty lines
                continue
            natoms = int(line)
            title = f.readline().strip()
            atoms = []
            for _ in range(natoms):
                atom_line = f.readline().strip()
                atoms.append(atom_line)
            frames.append((natoms, title, atoms))
    return frames

def write_xyz(file, frames):
    """
    Write frames to an xyz trajectory file.

    Parameters
    ----------
    file : str
        The name of the output xyz file.
    frames : list
        A list of tuples containing the number of atoms, title, and atom lines for each frame.
    """
    with open(file, 'w') as f:
        for natoms, title, atoms in frames:
            f.write(f'{natoms}\n')
            f.write(f'{title}\n')
            for atom_line in atoms:
                f.write(f'{atom_line}\n')

def xyz_flipper(input_file):
    """
    Takes an xyz file and reverses the order of the frames.

    Parameters
    ----------
    input_file : str
        The name of the input xyz file to reverse.

    Notes
    -----
    The input file should be an xyz trajectory file, usually named scan_optim in TeraChem.
    The output file will be named as "{input_file}_reversed.xyz".

    """
    print("\n.-------------.")
    print("| XYZ FLIPPER |")
    print(".-------------.\n")
    print("Reverse an xyz trajectory.")
    print("Useful if a geometry scan was run in reverse.\n")

    # Generate the output file name based on the input file name
    xyz_file = f"{input_file}.xyz"
    output_file = f"{input_file}_reversed.xyz"

    # Read frames from the input file
    frames = read_xyz(xyz_file)

    # Reverse the order of the frames
    frames_reversed = list(reversed(frames))

    # Write the reversed frames to the output file
    write_xyz(output_file, frames_reversed)

    print(f"Reversed trajectory written to {output_file}")

if __name__ == '__main__':
    xyz_flipper()