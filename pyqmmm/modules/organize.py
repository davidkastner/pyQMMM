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
import glob

################################## FUNCTIONS ###################################

'''
Search the current directory for all xyz files and ignore non-trajectory files
Returns
-------
xyz_filename_list : list
    A list of all trajectory file names in the current directory
'''


def get_xyz_filenames():
    # Get all xyz files and sort them
    file_list = glob.glob('*.xyz')
    sorted(file_list)
    xyz_filename_list = []

    # Loop through files and check to see if they are trajectories
    for file in file_list:
        with open(file, 'r') as current_file:
            trajectory = False
            first_line = True
            header_count = 0
            # If the atom count appears more than once than it is a trajectory
            for line in current_file:
                if first_line == True:
                    atom_count = line.strip()
                    header_count += 1
                    first_line = False
                if line.strip() == atom_count:
                    header_count += 1
                if header_count > 1:
                    trajectory = True
                    break
        # Combine all the trajectory files into a single list
        if trajectory == True:
            xyz_filename_list.append(file)

    xyz_filename_list.sort()
    print('We found these .xyz files: {}'.format(xyz_filename_list))

    return xyz_filename_list


'''
Turns an xyz trajectory file into a list of lists where each element is a frame.
Parameters
----------
xyz_filename : string
    The file name of an xyz trajectory

Returns
-------
xyz_traj : list
    List of lists containing the trajectory with each frame saved as an element
'''


def multiframe_xyz_to_list(xyz_filename):
    # Variables that measure our progress in parsing the optim.xyz file
    xyz_traj = []  # List of lists containing all frames
    frame_contents = ''
    line_count = 0
    frame_count = 0
    first_line = True  # Marks if we've looked at the atom count yet

    # Loop through optim.xyz and collect distances, energies and frame contents
    with open(xyz_filename, 'r') as traj:
        for line in traj:
            # We determine the section length using the atom count in first line
            if first_line == True:
                section_length = int(line.strip()) + 2
                first_line = False
            # At the end of the section reset the frame-specific variables
            if line_count == section_length:
                line_count = 0
                xyz_traj.append(frame_contents)
                frame_contents = ''
                frame_count += 1
            frame_contents += line
            line_count += 1

        xyz_traj.append(frame_contents)

    # Print statistics of the xyz parsing to the user
    print(f'We found {xyz_traj} frames in {xyz_filename}.')

    return xyz_traj


'''
Combines two xyz files into one.
Parameters
----------
combined_filename : string
    What the user would like to call the newly created combined xyz file
'''


def combine_xyz_files(combined_filename='combined.xyz'):
    # Find xyz trajectories in the current directory
    xyz_filename_list = get_xyz_filenames()
    # For each xyz file convert to a list with only the requested frames
    combined_xyz_list = []
    for file in xyz_filename_list:
        requested_frames = request_frames(file)
        # The user can skip files by with enter which returns an empty string
        if requested_frames == '':
            continue
        # Convert the xyz files to a list
        xyz_list = multiframe_xyz_to_list(file)
        requested_xyz_list = [frame for index, frame in enumerate(
            xyz_list) if index + 1 in requested_frames]
        # Ask the user if they want the frames reversed for a given xyz file
        reverse = input('Any key to reverse {} else Return: '.format(file))
        if reverse:
            requested_xyz_list.reverse()
            reverse = False
        combined_xyz_list += requested_xyz_list
    # Write the combined trajectories out to a new file called combined.xyz
    with open(combined_filename, 'w') as combined_file:
        for entry in combined_xyz_list:
            combined_file.write(entry)
    print(f'Your combined xyz was written to {combined_filename}.')
