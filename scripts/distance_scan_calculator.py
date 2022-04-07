'''
Docs: https://github.com/davidkastner/pyQMMM/blob/main/pyqmmm/README.md
DESCRIPTION
    When you generate a xyz scan you lose amino acid identifers.
    This script allows you to analyze distances between atoms in xyz files.

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


def function(function):
    return
