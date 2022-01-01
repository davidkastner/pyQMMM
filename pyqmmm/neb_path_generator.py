'''
See more here: https://github.com/davidkastner/quick-csa/blob/main/README.md
DESCRIPTION
    Identify the ideal starting path for NEB from a TeraChem PES.
    Author: David Kastner
    Massachusetts Institute of Technology
    kastner (at) mit . edu
SEE ALSO
    collect_reaction_coordinate.py
'''
################################ DEPENDENCIES ##################################
from scipy.spatial import distance
import numpy as np

################################## FUNCTIONS ###################################

'''
Get the user's linear combination of restraints and preferred NEB path length.
Returns
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
    # How many images should be in the NEB path
    image_count = int(
        input('What atoms define your second reaction coordinate?'))

    return coord1, coord2, image_count


'''
Get each one of the frames on store them.
Parameters
----------
dict : dictionary
    List of two atoms defining a reaction coordiante distance
Returns
-------
reaction_coordinates : list
    List of values mapping to the distance that two atoms have moved.
'''


def get_frames(coord1, coord2, master_list):
    # Variables that measure our progress in parsing the optim.xyz file
    frame_contents = []
    line_count = 0
    frame_count = 0
    section_length_flag = False
    xyz_coord1_list = []
    xyz_coord2_list = []
    # Loop through optim.xyz and collect distances, energies and frame contents
    with open('./optim.xyz', 'r') as optim:
        for line in optim:
            # We need to know how long each section is but only count once
            if section_length_flag == False:
                section_length = int(line.strip()) + 2
                section_length_flag = True
            # The second line will have the energy
            if line_count == 1:
                energy = float(line.split(' ')[0])
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
                frame_contents = []
                frame_count += 1
                xyz_coord1_list = []
                xyz_coord2_list = []

            frame_contents.append(line)
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
        if len(xyz_coord_list) and len(xyz_coord_list) % 2 == 0:
            atom_1 = tuple(xyz_coord_list[-1])
            atom_2 = tuple(xyz_coord_list[-2])
            coord_dist = distance.euclidean(atom_1, atom_2)
            master_list[frame_count][dict_key] = coord_dist

    return xyz_coord_list, master_list

# General function handler


def neb_image_generator():
    print('\n.--------------------------------.')
    print('| WELCOME TO NEB IMAGE GENERATOR |')
    print('.--------------------------------.\n')
    print('Run this script in the same directory as the TeraChem job.')
    print('Identifies the best set of images for an initial NEB path.\n')

    # This list will be populated with dictionaries for each frame
    master_list = []
    # Get the two reaction coordinates and the preferred number of images
    #coord1,coord2,image_count = user_input()
    coord1 = [123, 128]
    coord2 = [128, 138]
    image_count = 20

    # Get the distances for the first reaction coordinate
    master_list = get_frames(coord1, coord2, master_list)
    print(master_list[1000]['energy'])
    print(master_list[1000]['coord1_dist'])
    print(master_list[1000]['coord2_dist'])
    print(master_list[1000])


if __name__ == "__main__":
    neb_image_generator()
