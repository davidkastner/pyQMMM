'''
Docs: https://github.com/davidkastner/pyQMMM/blob/main/pyqmmm/README.md
DESCRIPTION
    A compilation of essential standalone functions to organize an xyz traj.

    Author: David Kastner
    Massachusetts Institute of Technology
    kastner (at) mit . edu

'''
################################ DEPENDENCIES ##################################
import numpy as np

################################## FUNCTIONS ###################################

'''
Turns an xyz trajectory file into a list of lists where each element is a frame.
Parameters
----------
xyz_filename : string
    The file name of an xyz trajectory

Returns
-------
xyz_as_list : list
    List of lists containing the trajectory with each frame saved as an element
'''


def multiframe_xyz_to_list(xyz_filename):
    # Variables that measure our progress in parsing the optim.xyz file
    xyz_as_list = []  # List of lists containing all frames
    frame_contents = ''
    line_count = 0
    frame_count = 0
    first_line = True  # Marks if we've looked at the atom count yet

    # Loop through optim.xyz and collect distances, energies and frame contents
    with open(xyz_filename, 'r') as trajectory:
        for line in trajectory:
            # We determine the section length using the atom count in first line
            if first_line == True:
                section_length = int(line.strip()) + 2
                first_line = False
            # At the end of the section reset the frame-specific variables
            if line_count == section_length:
                line_count = 0
                xyz_as_list.append(frame_contents)
                frame_contents = ''
                frame_count += 1
            frame_contents += line
            line_count += 1

        xyz_as_list.append(frame_contents)

    # Print statistics of the xyz parsing to the user
    print(f'We found {xyz_as_list} frames in {xyz_filename}.')

    return xyz_as_list