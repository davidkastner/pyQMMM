'''
Docs: https://github.com/davidkastner/pyQMMM/blob/main/pyqmmm/README.md
DESCRIPTION
    After performing a TeraChem PES, the coordinates are found in the xyz file.
    Using this file we can extract reaction coordinates against energies.
    This is can then be graphed in your plotter of choice such as XMGrace.
    The output is a .csv file with energies in column 1 and the RC in column 2.

    Author: David Kastner
    Massachusetts Institute of Technology
    kastner (at) mit . edu

'''
################################ DEPENDENCIES ##################################
from math import comb
from scipy.spatial import distance
import numpy as np
import os

################################## FUNCTIONS ###################################
'''
Get the user's reaction coordinate definition.
Returns
-------
atoms : list
    list of atoms indices
'''


def request_rc(rc_request):
    # What atoms define your reaction coordinate
    request = input('Atoms in your {} RC? (e.g., 1_2): '.format(rc_request))

    # Check if RC is requested and onvert to a list even if it is hyphenated
    if request != '':
        temp = [(lambda sub: range(sub[0], sub[-1] + 1))
                (list(map(int, ele.split('-')))) for ele in request.split('_')]
        atoms = [b for a in temp for b in a]

    return atoms, request


'''
Calculates the reaction coordinate at each step of the scan in the xyz file.
Parameters
----------
atoms : list
    List of two atoms defining a reaction coordiante distance
Returns
-------
reaction_coordinates : list
    List of values mapping to the distance that two atoms have moved.
'''


def get_distance(atoms, xyz_file):
    atom_count = 0
    coords_list = []
    dist_list = []
    with open(xyz_file, 'r') as scan_optim:
        for line in scan_optim:
            if line[:9] == 'Converged':
                atom_count = 0
            if atom_count in atoms:
                line_elements = line.split()
                coords = line_elements[1:4]
                coords_list.append(list(map(float, coords)))
                if len(coords_list) and len(coords_list) % 2 == 0:
                    atom_1 = tuple(coords_list[-1])
                    atom_2 = tuple(coords_list[-2])
                    dist = distance.euclidean(atom_1, atom_2)
                    dist_list.append(dist)
            atom_count += 1

    return dist_list

# '''
# Calculates an optional y-axis reaction coordinate at each step of the scan.
# Parameters
# ----------
# yaxis_atoms : list
#     List of two atoms defining the y-axis reaction coordinate angle
# Returns
# -------
# reaction_coordinates : list
#     List of values mapping to the distance that two atoms have moved.
# '''
# def get_angle(atoms, xyz_file):
#     atom_index = 0
#     coords_list = []
#     angle_list = []
#     with open(xyz_file, 'r') as scan_optim:
#         for line in scan_optim:
#             if line[:9] == 'Converged':
#                 atom_index = 0
#             if atom_index in atoms:
#                 line_elements = line.split()
#                 coords = line_elements[1:4]
#                 coords_list.append(list(map(float, coords)))

#                 if len(coords_list) and len(coords_list) % 3 == 0:
#                     a = np.array(coords_list[-1])
#                     b = np.array(coords_list[-2])
#                     c = np.array(coords_list[-3])
#                     ba = a - b
#                     bc = c - b
#                     cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
#                     angle = np.arccos(cosine_angle)
#                     angle_degrees = np.degrees(angle)
#                     angle_list.append(angle_degrees)
#             atom_index += 1

#     return angle_list


'''
Loop through the xyz file and collect optimized energies.
Returns
-------
energy_df : dataframe
    The optimized energy from the current convergence line of the file.
energy_list : list
    Returns a list of the energies extracted from the .out file.
'''


def get_opt_energies(xyz_file):
    DE_list = []
    E_list = []
    with open(xyz_file, 'r') as file:
        first_energy = None
        for line in file:
            if line[:9] == 'Converged':
                line = line.split()
                energy = float(line[4])
                if first_energy == None:
                    first_energy = energy
                relative_energy = (energy - first_energy) * 627.5
                absolute_energy = energy
                DE_list.append(relative_energy)
                E_list.append(absolute_energy)

    # Return lists of relative and absolute energies
    return DE_list, E_list


'''
Combine reaction coordinate and energy list and write them to a .csv file
Parameters
----------
dist_list : list
    List of distances defining each step of the reaction coordinate
energy_list : list
    List of all energies mapping to each step of the reacitno coordinate
'''


def get_reaction_csv(xaxis_list, yaxis_list, extension):
    with open('./{}.csv'.format(extension), 'w') as csv_file:
        for x, y in zip(xaxis_list, yaxis_list):
            csv_file.write('{},{}\n'.format(x, y))


def reaction_coordinate_collector():
    print('\n.-------------------------------.')
    print('| REACTION COORDINATE COLLECTOR |')
    print('.-------------------------------.\n')
    print('Run this script in the same directory as the TeraChem job.')
    print('Computes energy (kcal/mol) against two distance coordinates.')
    print('If you only have one RC, leave a prompt empty.')
    print('Optionally computes an angle coordinate against distance.\n')

    # Preprocessed combined.xyz files take priority so check if one exists
    combined_xyz = './combined.xyz'
    combined_xyz_exists = os.path.exists(combined_xyz)
    if combined_xyz_exists:
        xyz_file = combined_xyz
        print('Will use found combined.xyz file')
    else:
        xyz_file = input('What xyz file would you like to use?')

    DE_list, E_list = get_opt_energies(xyz_file)
    # Energy against first distance coordinate
    rc1_dist_atoms, rc1_request = request_rc('first')
    if rc1_request != '':
        rc1_dist_list = get_distance(rc1_dist_atoms, xyz_file)
        get_reaction_csv(rc1_dist_list, E_list, 'rc1_v_energy')

    # Energy against second distance coordinate
    rc2_dist_atoms, rc2_request = request_rc('second')
    if rc2_request != '':
        rc2_dist_list = get_distance(rc2_dist_atoms, xyz_file)
        get_reaction_csv(rc2_dist_list, E_list, 'rc2_v_energy')

    # Calculate differences of differences
    rc1_dist_list = np.array(rc1_dist_list)
    rc2_dist_list = np.array(rc2_dist_list)
    # Check to see which coordinate is larger
    if rc1_dist_list[0] > rc2_dist_list[0]:
        diff_dist_list = rc2_dist_list - rc1_dist_list
    else:
        diff_dist_list = rc1_dist_list - rc2_dist_list
    get_reaction_csv(diff_dist_list, E_list, 'dd_v_energy')
    get_reaction_csv(diff_dist_list, rc1_dist_list, 'dd_v_rc1')
    get_reaction_csv(diff_dist_list, rc2_dist_list, 'dd_v_rc2')


if __name__ == "__main__":
    reaction_coordinate_collector()
