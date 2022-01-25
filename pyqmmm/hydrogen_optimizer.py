'''
Docs: https://github.com/davidkastner/md-utilities/hyscore-plotter/blob/main/README.md
DESCRIPTION
   Creates a list with the indices of all heavy atoms in an xyz.
   This is useful if you want to only optimize the hydrogen positions.
   Author: David Kastner
   Massachusetts Institute of Technology
   kastner (at) mit . edu

'''
################################ DEPENDENCIES ##################################
import os
import sys
################################## FUNCTIONS ###################################
'''
Check the current dir for an .xyz file and let user know if one exists.
Parameters
----------
N/A
Returns
-------
file : str
    The name of the .xyz that we will loop through
'''


def get_xyz_file():
    files = os.listdir('.')
    count = 0
    current_file = ''
    for file in files:
        if '.xyz' in file:
            count += 1
            current_file = file
    if count > 1:
        print('More than one .xyz found')
        sys.exit()
    print('Using {}'.format(current_file))
    return current_file


'''
Search the user's xyz file for the index of all hydrogen atoms.
Parameters
----------
file : str
    The name of the .xyz that we will loop through
Returns
-------
N/A
'''


def find_heavy_atoms(file):
    heavy_atoms_list = []
    with open(file, 'r') as xyz_file:
        for index, line in enumerate(list(xyz_file)[2:]):
            if line[0] != 'H':
                heavy_atoms_list.append(str(index + 1))
    heavy_atoms = ','.join(heavy_atoms_list)
    print(heavy_atoms)


############################### HYDRO OPTIMIZER ###################################
# Introduce user to Hydro Optimizer functionality
print('WELCOME TO HYDRO OPTIMIZER')
print('--------------------------\n')
print('Takes an .xyz file and returns the index of all hydrogens as a list.')
print('This script will search the current directory for the following input:')
print('+ An xyz file')
print('------------------------\n')

# Gets the name of the xyz file in the current directory
file = get_xyz_file()
# Gets a list of the heavy atoms to freeze
find_heavy_atoms(file)
