"""Calculates the distance between two centroids from an xyz traj."""

from pyqmmm.modules import organize


def distance_scanner():
    """
    When you generate a xyz scan you lose amino acid identifers.
    This script allows you to analyze distances between atoms in xyz files.
    """

    print("\n.------------------.")
    print("| DISTANCE SCANNER |")
    print(".------------------.\n")
    print("Calculates the distance between two centroids from an xyz traj.")
    print("Just provide two sets of atoms, and we handle the rest.")
    print("Returns the distance per frame and the average distance and std.\n")

    # Create an iterable list of frames from the xyz file
    organize.multiframe_xyz_to_list("xyz_filename")


if __name__ == "__main__":
    distance_scanner()
