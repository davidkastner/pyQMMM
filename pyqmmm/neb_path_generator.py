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
import matplotlib.pyplot as plt
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
        input('Into how many bins would you like to divide the data?')) + 1

    return coord1, coord2, image_count


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


'''
Assign bins to all frames.
Parameters
----------

Returns
-------

'''


def get_bins(master_list, scan_master_list, image_count):
    # Get all the differences of distances and add them to a new list
    dist_diff_list = []
    for dict in master_list:
        dist_diff_list.append(dict['dist_diff'])
    # Find the min and max from scan_geom.xyz
    min_dist_diff = min(dist_diff_list)
    max_dist_diff = max(dist_diff_list)

    # Divided the total difference of distances into equal parts
    bin_categories = list(np.linspace(min_dist_diff, max_dist_diff, image_count))
    print(bin_categories)
    # Find the bin for each frame, less than the previous and more than the next
    for index, dist_diff in enumerate(dist_diff_list):
        for i, bin_category in enumerate(bin_categories):
            if dist_diff >= bin_category and dist_diff <= bin_categories[i + 1]:
                master_list[index]['bin'] = i + 1

                break

    return master_list, min_dist_diff, max_dist_diff


def find_lowest_energy(master_list):
    bin_mins = {}
    # Create a dictionary of dictionary to store all the energy values
    for index, dict in enumerate(master_list):
        if dict['bin'] not in bin_mins:
            bin_mins[dict['bin']] = {}
            bin_mins[dict['bin']]['energy'] = dict['energy']
            bin_mins[dict['bin']]['index'] = index
            continue
        
        # We only want the frame from each bin with the smallest energy
        curr_bin_min = bin_mins[dict['bin']]['energy']
        if curr_bin_min > dict['energy']:
            bin_mins[dict['bin']]['energy'] = dict['energy']
            bin_mins[dict['bin']]['index'] = index

    frame_indices = [value['index'] for key, value in bin_mins.items()]

    return frame_indices


def get_ts(scan_master_list):
    max_energy = None
    max_energy_index = 0
    # We need to get the transition state from scan_optim.xyz
    for index, dict in enumerate(scan_master_list):
        # Since our starting list is empty, we will handle first case separately
        if max_energy == None:
            max_energy = scan_master_list[index]['energy']
            max_energy_index = index
        # Look for the largest energy
        elif max_energy <= scan_master_list[index]['energy']:
            max_energy = scan_master_list[index]['energy']
            max_energy_index = index
    # Extract the dictionary corresponding ot the TS frame
    ts_dict = scan_master_list[max_energy_index]

    return ts_dict, max_energy_index


def get_final_master(frame_indices, master_list, ts_dict):
    final_master_list = []
    # Loop through master list and remove the binned frames
    for i, index in enumerate(frame_indices):
        final_master_list.append(master_list[index])
        if i + 1 > len(frame_indices) - 1:
            continue
        if master_list[index]['dist_diff'] < ts_dict['dist_diff'] and master_list[frame_indices[i + 1]]['dist_diff'] > ts_dict['dist_diff']:
            final_master_list.append(ts_dict)
    final_master_list = sorted(final_master_list, key = lambda i: i['dist_diff'])

    return final_master_list


def get_neb_path(final_master_list):
    with open('./neb_path.xyz', 'w') as neb_path:
        for dict in final_master_list:
            neb_path.write(dict['frame_contents'])


def get_dist_energy_lists(final_master_list):
    dist_diff_list = []
    energy_list = []
    for index, dict in enumerate(final_master_list):
        dist_diff_list.append(final_master_list[index]['dist_diff'])
        energy_list.append(final_master_list[index]['energy'])
    return dist_diff_list, energy_list


def get_plot(dist_diff_list, energy_list):
    plt.rc('axes', linewidth=2.5)
    plt.ylabel('relative energy (kcal/mol)', fontsize=16)
    plt.xlabel('difference of distance (Å)', fontsize=16)
    plt.plot(dist_diff_list, energy_list, marker='o')
    plt.tick_params(labelsize=14)
    plt.savefig('./plot.pdf', bbox_inches='tight')
    plt.show()


def neb_image_generator():
    print('\n.--------------------------------.')
    print('| WELCOME TO NEB IMAGE GENERATOR |')
    print('.--------------------------------.\n')
    print('Run this script in the same directory as the TeraChem job.')
    print('Identifies the best set of images for an initial NEB path.\n')

    # This list will be populated with dictionaries for each frame
    master_list = []
    scan_master_list = []

    # 1) Get the two reaction coordinates and the preferred number of images
    # coord1,coord2,image_count = user_input()
    coord1 = [123, 128]
    coord2 = [128, 138]
    image_count = 20
    print('Step 1: Your atom indices are {} and {} and you want {} frames.'.format(
        coord1, coord2, image_count))

    # 2) Get the distances and differences of distances
    master_list = get_frames(coord1, coord2, master_list, './scr/scan_optim.xyz')
    master_list = get_dist_diff(master_list)
    print('Step 2: {} frames have been parsed and stored.'.format(len(master_list)))

    # 3) Find the TS frame in scan_optim.xyz
    scan_master_list = get_frames(coord1, coord2, scan_master_list, './scr/scan_optim.xyz')
    scan_master_list = get_dist_diff(scan_master_list)
    ts_dict, index = get_ts(scan_master_list)
    print('Step 3: The TS was found in frame {}.'.format(index))

    # 4) Assign bins to each of the frames
    master_list, min_dist_diff, max_dist_diff = get_bins(
        master_list, scan_master_list, image_count)
    print('Step 4: Your max value is {} and your min value is {}.'.format(
        min_dist_diff, max_dist_diff))

    # 5) Find the frame in each bin with the lowest energy
    frame_indices = find_lowest_energy(master_list)
    print('Step 5: Your binned frames: {}'.format(frame_indices))


    # 6) Create a dictionary with only the final selected frames and the TS
    final_master_list = get_final_master(frame_indices, master_list, ts_dict)
    get_neb_path(final_master_list)
    print('Step 6: The file neb_path.xyz was generated.')

    # 7) Generate plot of the distance difference vs relative energy
    dist_diff_list, energy_list = get_dist_energy_lists(final_master_list)
    get_plot(dist_diff_list, energy_list)
    print(dist_diff_list)
    print('Step 7: The line plot plot.pdf was generated.')


if __name__ == "__main__":
    neb_image_generator()
