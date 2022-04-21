"""
Docs: https://github.com/davidkastner/pyQMMM/blob/main/pyqmmm/README.md
DESCRIPTION
    When you generate a xyz scan you lose amino acid identifers.
    This script allows you to analyze distances between atoms in xyz files.

    Author: David Kastner
    Massachusetts Institute of Technology
    kastner (at) mit . edu

"""
################################ DEPENDENCIES ##################################
import sys
from pyqmmm.modules import analyze
from pyqmmm.modules import organize
from pyqmmm.modules import input

################################## FUNCTIONS ###################################


def distance_scanner():
    print("\n.------------------.")
    print("| DISTANCE SCANNER |")
    print(".------------------.\n")
    print("Calculates the distance between two centroids from an xyz traj.")
    print("Just provide two sets of atoms, and we handle the rest.")
    print("Returns the distance per frame and the average distance and std.\n")

    # Create an iterable list of frames from the xyz file
    organize.multiframe_xyz_to_list("xyz_filename")

    #


if __name__ == "__main__":
    distance_scanner()
