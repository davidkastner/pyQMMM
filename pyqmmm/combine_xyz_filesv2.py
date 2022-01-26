'''
Docs: https://github.com/davidkastner/pyQMMM/blob/main/pyqmmm/README.md
DESCRIPTION
    Reaction path calculations often need to be restarted from a later point.
    For example, rerunning a scan of the peak to get higher a resolution TS.
    Afterwards, the .xyz files of the two scans need to be stitched together.
    Here, users can specify the frames from each file that need to be combined.
    Returns the difference of distances against energy as a .dat file,
    and both reaction coordinates against the difference of distances coord.

    Author: David Kastner
    Massachusetts Institute of Technology
    kastner (at) mit . edu

'''
################################ DEPENDENCIES ##################################
import glob
import matplotlib.pyplot as plt
from scipy.spatial import distance
import numpy as np

################################## FUNCTIONS ###################################

'''
Search the current directory for all xyz files and remove any non-trajectories
Parameters
-------
atoms : list
    list of atoms indices
Get the user's reaction coordinate definition.
Returns
-------
trajectory_list : list
    list string names of all the trajectory xyz files in the directory
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
Get the request frames for each file from the user.
Parameters
----------
xyz_filename : str
    The filename of the current xyz trajectory of interest

Returns
-------
frames : list
    The frames the user requested to be extracted from the xyz trajectory
'''


def request_frame_info(xyz_filename):
    # What frames would you like from the first .xyz file?
    request = input('Which frames do you want from {}?: '.format(xyz_filename))
    reverse = input('Any key to reverse {} else Return: '.format(xyz_filename))
    # Continue if the user did not want that file processed and pressed enter
    if request == '':
        return request
    # Check the request and convert it to a list even if it is hyphenated
    temp = [(lambda sub: range(sub[0], sub[-1] + 1))
            (list(map(int, ele.split('-')))) for ele in request.split(',')]
    frames = [b for a in temp for b in a]

    print('For {} you requested frames {}.'.format(xyz_filename, frames))

    return frames, reverse


'''
Get the user's linear combination of restraints.
Parameters
-------
atoms : list
    list of atoms indices
Get the user's reaction coordinate definition.
Returns
-------
atoms : list
    list of atoms indices
'''


def user_input():
    # What atoms define the first reaction coordinate
    coord1_input = input('What atoms define your first reaction coordinate?')
    # Convert user input to a list even if it is hyphenated
    temp = [(lambda sub: range(sub[0], sub[-1] + 1))
            (list(map(int, ele.split('-')))) for ele in coord1_input.split(',')]
    coord1 = [b for a in temp for b in a]
    # What atoms define the second reaction coordinate
    coord2_input = input('What atoms define your second reaction coordinate?')
    # Convert user input to a list even if it is hyphenated
    temp = [(lambda sub: range(sub[0], sub[-1] + 1))
            (list(map(int, ele.split('-')))) for ele in coord2_input.split(',')]
    coord2 = [b for a in temp for b in a]

    return coord1, coord2


'''
Get each one of the frames and store them.
Parameters
----------
dict : dictionary
    List of two atoms defining a reaction coordiante distance
Returns
-------
reaction_coordinates : list
    List of values mapping to the distance that two atoms have moved.
'''


def get_frames(coord1, coord2, master_list, file):
    # Variables that measure our progress in parsing the optim.xyz file
    frame_contents = ''
    line_count = 0
    frame_count = 0
    section_length_flag = False
    xyz_coord1_list = []
    xyz_coord2_list = []
    energy_position = 4 if 'scan' in file else 0
    # Loop through optim.xyz and collect distances, energies and frame contents
    with open(file, 'r') as optim:
        for line in optim:
            # We need to know how long each section is but only count once
            if section_length_flag == False:
                section_length = int(line.strip()) + 2
                section_length_flag = True
            # The second line will have the energy
            if line_count == 1:
                energy = float(line.split()[energy_position])
                dict_new = {}
                master_list.append(dict_new)
                master_list[frame_count]['energy'] = energy
            # Calculate the distances and add them to the master list
            xyz_coord1_list, master_list = get_dist(
                frame_count, master_list, line, line_count, coord1, xyz_coord1_list, 'coord1_dist')
            xyz_coord2_list, master_list = get_dist(
                frame_count, master_list, line, line_count, coord2, xyz_coord2_list, 'coord2_dist')
            # At the end of the section reset the frame-specific variables
            if line_count == section_length:
                line_count = 0
                master_list[frame_count]['frame_contents'] = frame_contents
                frame_contents = ''
                frame_count += 1
                xyz_coord1_list = []
                xyz_coord2_list = []

            frame_contents += line
            line_count += 1

    return master_list


'''
Get the distance between two atoms of a reaction coordinate
Parameters
----------
frame_count : int
    Keeps track of what frame we are on
master_list : list
    List of dictionaries keyed by frame
line : object
    The line in the file that we are iterating over
coord : list
    The two numbers that define the current coordinate of interest
dict_key : string
    The name of the key we will assign the distance value to
Returns
-------
master_list : list
    Updated list of dictionaries keyed by frame
'''


def get_dist(frame_count, master_list, line, line_count, coord, xyz_coord_list, dict_key):
    # Get the distance between each atom for coordinate 2
    current_atom = line_count - 1
    if current_atom in coord:
        line_elements = line.split()
        xyz_coords = line_elements[1:]
        xyz_coord_list.append(list(map(float, xyz_coords)))
        # Calculate the Euclidean distance for the coordinates of two atoms
        if len(xyz_coord_list) and len(xyz_coord_list) % 2 == 0:
            atom_1 = tuple(xyz_coord_list[-1])
            atom_2 = tuple(xyz_coord_list[-2])
            coord_dist = distance.euclidean(atom_1, atom_2)
            master_list[frame_count][dict_key] = coord_dist

    return xyz_coord_list, master_list


'''
Calculate all difference of distances and add them to the master_list.
Parameters
----------
master_list : list
    List of dictionaries keyed by frame
Returns
-------
master_list : list
    Updated list of dictionaries keyed by frame
'''


def get_dist_diff(master_list):
    # Calculate the difference of distances
    for index, dict in enumerate(master_list):
        x1 = master_list[index]['coord1_dist']
        x2 = master_list[index]['coord2_dist']
        # We will cut sig figs at 8 so all data matches
        dist_diff = round(x2 - x1, 8)
        master_list[index]['dist_diff'] = dist_diff

    return master_list


def combine_xyz_files():
    # Welcome the user to the file and introduce basic functionality
    print('\n.-------------------.')
    print('| COMBINE XYZ FILES |')
    print('.-------------------.\n')
    print('Searches current directory for xyz trajectory files.')
    print('You can combine as many xyz files as you need.')
    print('Name your xyz file as 1.xyz, 2.xyz, etc.')
    print('Leave the prompt blank when you are done.\n')

    # Search through all xyz's in the current directory and get the trajectories
    xyz_filename_list = get_xyz_filenames()
    # For each xyz file convert to a list a select the requested frames
    combined_xyz_list = []
    for file in xyz_filename_list:
        requested_frames, reverse = request_frame_info(file)
        # The user can skip files by with enter which returns an empty string
        if requested_frames == '':
            continue
        # Convert the xyz files to a list
        xyz_list = multiframe_xyz_to_list(file)
        requested_xyz_list = [frame for index, frame in enumerate(
            xyz_list) if index + 1 in requested_frames]

        # Ask the user if they want the frames reversed for a given xyz file
        if reverse:
            requested_xyz_list.reverse()

        combined_xyz_list += requested_xyz_list

    with open('combined.xyz', 'w') as combined_file:
        for entry in combined_xyz_list:
            combined_file.write(entry)


if __name__ == "__main__":
    combine_xyz_files()
