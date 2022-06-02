"""Module for analyzing MD and QM trajectories"""

from scipy.spatial import distance


def get_distance(atoms, xyz_traj):
    """
    Calculates the reaction coordinate at each step of the xyz trajectory.

    Parameters
    ----------
    atoms : list
        List of two atoms for which a distance will be calculated.
    xyz_traj : list
        List of lists containing the trajectory with each frame saved as an element.

    Returns
    -------
    dist_list : list
        List of values mapping to the distance that two atoms have moved.
    """
    # Initializing important varibales
    atom_count = 0
    coords_list = []
    dist_list = []

    # This function is broken
    # Loop through the xyz trajectory
    for frame in xyz_traj:
        line = []  # Added fr flake8
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
