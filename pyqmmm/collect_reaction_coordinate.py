'''
Docs: https://github.com/davidkastner/pyQMMM/blob/main/pyqmmm/README.md
DESCRIPTION
    After performing a TeraChem PES, the coordinates are found in scan_optim.xyz.
    Using this file we can extract reaction coordinates against energies.
    This is can then be graphed in your plotter of choice such as XMGrace.
    The output is a .dat file with energies in column 1 and the RC in column 2.

    Author: David Kastner
    Massachusetts Institute of Technology
    kastner (at) mit . edu

'''
################################ DEPENDENCIES ##################################
from scipy.spatial import distance
import numpy as np

################################## FUNCTIONS ###################################
'''
Get the user's reaction coordinate definition.
Returns
-------
atoms : list
    list of atoms indices
'''


def user_input(rc_request):
    # What atoms define your reaction coordinate
    request = input('Atoms in your {} RC? (e.g., 1_2): '.format(rc_request))

    # Check if RC is requested and onvert to a list even if it is hyphenated
    if request != '':
        temp = [(lambda sub: range(sub[0], sub[-1] + 1))
                (list(map(int, ele.split('-')))) for ele in request.split('_')]
        atoms = [b for a in temp for b in a]

    return atoms, request


'''
Calculates the reaction coordinate at each step of the scan from scan_optim.xyz.
Parameters
----------
atoms : list
    List of two atoms defining a reaction coordiante distance
Returns
-------
reaction_coordinates : list
    List of values mapping to the distance that two atoms have moved.
'''


def get_distance(atoms):
    atom_count = 0
    coords_list = []
    dist_list = []
    with open('./scr/scan_optim.xyz', 'r') as scan_optim:
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
# def get_angle(atoms):
#     atom_index = 0
#     coords_list = []
#     angle_list = []
#     with open('./scr/scan_optim.xyz', 'r') as scan_optim:
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
Loop through the file, collect optimized energies.
Returns
-------
energy_df : dataframe
    The optimized energy from the current convergence line of the file.
energy_list : list
    Returns a list of the energies extracted from the .out file.
'''


def get_opt_energies():
    DE_list = []
    E_list = []
    with open('./qmscript.out', 'r') as out_file:
        first_energy = None
        for line in out_file:
            if line[6:22] == 'Optimized Energy':
                energy = float(line[26:42])
                if first_energy == None:
                    first_energy = energy
                relative_energy = (energy - first_energy) * 627.5
                absolute_energy = energy * 627.5
                DE_list.append(relative_energy)
                E_list.append(absolute_energy)

    # Return lists of relative and absolute energies
    return DE_list, E_list


'''
Combine reaction coordinate and energy list and write them to a .dat file
Parameters
----------
dist_list : list
    List of distances defining each step of the reaction coordinate
energy_list : list
    List of all energies mapping to each step of the reacitno coordinate
'''


def get_reaction_dat(xaxis_list, yaxis_list, extension):
    with open('./rc_{}.dat'.format(extension), 'w') as dat_file:
        for x, y in zip(xaxis_list, yaxis_list):
            dat_file.write('{} {}\n'.format(x, y))

# General function handler


def reaction_coordinate_collector():
    print('\n.------------------------------.')
    print('| COLLECT REACTION COORDINATES |')
    print('.------------------------------.\n')
    print('Run this script in the same directory as the TeraChem job.')
    print('Computes energy (kcal/mol) against two distance coordinates.\n')
    print('If you only have one RC, leave a prompt empty.\n')
    print('Optionally computes an angle coordinate against distance.\n')

    # Energy against a distance coordinate
    dist_atoms, request = user_input('first')
    if request != '':
        dist_list = get_distance(dist_atoms)
        DE_list, E_list = get_opt_energies()
        get_reaction_dat(dist_list, E_list, request)

    # Energy against a distance coordinate
    dist_atoms, request = user_input('second')
    if request != '':
        dist_list = get_distance(dist_atoms)
        DE_list, E_list = get_opt_energies()
        get_reaction_dat(dist_list, E_list, request)

    # # Angle against a distance coordinate
    # angle_atoms = user_input()
    # angle_list = get_angle(angle_atoms)
    # get_reaction_dat(dist_list, angle_list, 'angle')


if __name__ == "__main__":
    reaction_coordinate_collector()
