'''
Docs: https://github.com/davidkastner/pyQMMM/blob/main/pyqmmm/README.md
DESCRIPTION
    A compilation of essential standalone functions to analyze an xyz traj.

    Author: David Kastner
    Massachusetts Institute of Technology
    kastner (at) mit . edu

'''
################################ DEPENDENCIES ##################################
from scipy.spatial import distance

################################## FUNCTIONS ###################################

'''
Calculates the reaction coordinate at each step of the xyz trajectory.
Parameters
----------
atoms : list
    List of two atoms for which a distance will be calculated
xyz_traj : list
    List of lists containing the trajectory with each frame saved as an element

Returns
-------
dist_list : list
    List of values mapping to the distance that two atoms have moved.
'''


def get_distance(atoms, xyz_traj):
    # Initializing important varibales
    atom_count = 0
    coords_list = []
    dist_list = []

# Loop through the xyz trajectory
    for frame in xyz_traj:

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
