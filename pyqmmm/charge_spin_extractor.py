'''
Docs: https://github.com/davidkastner/pyQMMM/blob/main/pyqmmm/README.md
DESCRIPTION
    Extract charge and spin data for a given subset of atoms for graphing.
    Written to interpet TeraChem mullpop and charge_mull.xls files.

    Author: David Kastner
    Massachusetts Institute of Technology
    kastner (at) mit . edu

'''

################################ DEPENDENCIES ##################################
import glob
import matplotlib.pyplot as plt
from scipy.spatial import distance
import numpy as np
import collect_reaction_coordinate

################################## FUNCTIONS ###################################
'''
Find all examples of a file type in the current directory
Parameters
----------
file_pattern : str
    The type of file the user would like to search the current directory for
Returns
-------
xyz_filename_list : list
    list of files found matching the user's pattern
'''


def get_files(file_pattern):
    file_list = glob.glob(file_pattern)
    sorted(file_list)
    print('We found {} for the pattern {}'.format(file_list, file_pattern))
    return file_list


'''
Get the user's atom set.
Returns
-------
atoms : list
    list of atoms indices
'''


def get_selection(file):
    # For which frames would the user like
    selection = input('What frames would you like for {}: '.format(file))

    # Convert user input to a list even if it is hyphenated
    temp = [(lambda sub: range(sub[0], sub[-1] + 1))
            (list(map(int, ele.split('-')))) for ele in selection.split(',')]
    selection = [int(b) for a in temp for b in a]

    return selection


def get_atoms():
    # For which atoms would the user like to sum the spin and charge
    my_atoms = input('What atom indexes to sum (e.g., 58-76): ')

    # Convert user input to a list even if it is hyphenated
    temp = [(lambda sub: range(sub[0], sub[-1] + 1))
            (list(map(int, ele.split('-')))) for ele in my_atoms.split(',')]
    atoms = [str(b) for a in temp for b in a]

    return atoms


'''
Gets the charges for the atoms specified by the user and sums them
Parameters
----------
atoms : list
    list of atoms indices
'''


def get_spins(atoms, file, selection):
    # Sum the spins for the user selected atoms
    net_spins = []
    net_spin = 0
    step_count = 0
    with open(file, 'r') as scan_spin_file:
        for line in scan_spin_file:
            line_list = line.split()
            if line_list[0] in atoms:
                net_spin += float(line_list[9])

            if line_list[0] == 'End':
                step_count += 1
                net_spins.append('{} {}\n'.format(step_count, net_spin))
                net_spin = 0

    net_spins_reference = net_spins.copy()
    for index, spin in enumerate(net_spins_reference):
        if index + 1 not in selection:
            net_spins.remove(net_spins_reference[index])

    reverse = input('Press any key to reverse data for {}: '.format(file))
    if reverse:
        net_spins.reverse()

    return net_spins


'''
Gets the charge for the atoms specified by the user and sums them
Parameters
----------
atoms : list
    list of atoms indices
'''


def get_charges(atoms, file, selection):
    # Sum the charges for the user selected atoms
    net_charges = []
    net_charge = 0
    step_count = 0
    with open(file, 'r') as scan_charge_file:
        for line in scan_charge_file:
            line_list = line.split()
            if line_list[0] in atoms:
                net_charge += float(line_list[2])

            if line_list[0] == 'End':
                step_count += 1
                net_charges.append('{},{}\n'.format(step_count, net_charge))
                net_charge = 0

    net_charges_reference = net_charges.copy()
    for index, charge in enumerate(net_charges_reference):
        if index + 1 not in selection:
            net_charges.remove(net_charges_reference[index])

    reverse = input('Press any key to reverse data for {}: '.format(file))
    if reverse:
        net_charges.reverse()

    return net_charges


'''
Writes out the data for either the charge or spin
Parameters
----------
file : str
    the name of the file where we are going to write out the data
net_data : list
    list of data extracted from either the spin or charge files
'''


def write_data(file, net_data):
    with open(file, 'w') as select_file:
        for pair in net_data:
            select_file.write(pair)


def extract_charges_spins():
    print('\n.-----------------------.')
    print('| EXTRACT CHARGES SPINS |')
    print('.-----------------------.\n')
    print('First run organize_energy_scan_data.py for each job.')
    print('Move the scan_charge and scan_spin to the same directory.')
    print('Give them unique names.')
    print('Extract summed charge and spin for user specified atoms\n')

    # Check how many charge and spin files
    charge_files = get_files('*.charge')
    spin_files = get_files('*.spin')

    # What atoms does the user want to perform charge-spin analysis for?
    atoms = get_atoms()

    # Loop through each charge files and concatonate them
    charge_lists = []
    for file in charge_files:
        selection = get_selection(file)
        net_charge_data = get_charges(atoms, file, selection)
        charge_lists += net_charge_data
    write_data('combined_charge.dat', charge_lists)

    # Loop through each spin files and concatonate them
    spin_lists = []
    for file in spin_files:
        selection = get_selection(file)
        net_spin_data = get_spins(atoms, file, selection)
        spin_lists += net_spin_data
    write_data('combined_spin.dat', spin_lists)


if __name__ == "__main__":
    extract_charges_spins()
