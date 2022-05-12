"""
Docs: https://github.com/davidkastner/pyQMMM/blob/main/pyqmmm/README.md
DESCRIPTION
    Extract charge and spin data for a given subset of atoms for graphing.
    Written to interpet TeraChem mullpop and charge_mull.xls files.

    Author: David Kastner
    Massachusetts Institute of Technology
    kastner (at) mit . edu
"""

import glob


def get_files(file_pattern):
    """
    Find all examples of a file type in the current directory.

    Parameters
    ----------
    file_pattern : str
        The type of file the for which the user would like to search the current directory

    Returns
    -------
    xyz_filename_list : list
        list of files found matching the user's pattern
    """

    file_list = glob.glob(file_pattern)
    file_list = sorted(file_list)
    print("We found {} using the pattern {}".format(file_list, file_pattern))

    return file_list


def get_selection(file):
    """
    Get the user's atom set.
    Returns
    -------
    atoms : selection
        the index of the atom the user would like the spin and charge for
    """

    # For which frames would the user like
    selection = input("What frames would you like for {}: ".format(file))

    # Convert user input to a list even if it is hyphenated
    temp = [
        (lambda sub: range(sub[0], sub[-1] + 1))(list(map(int, ele.split("-"))))
        for ele in selection.split(",")
    ]
    selection = [int(b) for a in temp for b in a]

    return selection


def get_atoms():
    # For which atoms would the user like to sum the spin and charge
    my_atoms = input("What atom indexes would you like to sum (e.g., 58-76): ")

    # Convert user input to a list even if it is hyphenated
    temp = [
        (lambda sub: range(sub[0], sub[-1] + 1))(list(map(int, ele.split("-"))))
        for ele in my_atoms.split(",")
    ]
    atoms = [str(b) for a in temp for b in a]

    return atoms


def get_spins(atoms, file, selection):
    """
    Gets the charges for the atoms specified by the user and sums them
    Parameters
    ----------
    atoms : list
        list of atoms indices
    file : str
        the name of the file that you would like to analyze
    selection : list
        the indices of the atoms that the user would like the charge and spin for

    Returns
    -------
    net_spins : list
        list fo spins corresponding to each image in the scan
    """

    # Sum the spins for the user selected atoms
    net_spins = []
    net_spin = 0
    step_count = 0
    with open(file, "r") as scan_spin_file:
        for line in scan_spin_file:
            line_list = line.split()
            if line_list[0] in atoms:
                net_spin += float(line_list[9])

            if line_list[0] == "End":
                step_count += 1
                net_spins.append("{},{}\n".format(step_count, net_spin))
                net_spin = 0

    net_spins_reference = net_spins.copy()
    for index, spin in enumerate(net_spins_reference):
        if index + 1 not in selection:
            net_spins.remove(net_spins_reference[index])

    reverse = input("Press any key to reverse data for {}: ".format(file))
    if reverse:
        net_spins.reverse()

    return net_spins


def get_charges(atoms, file, selection):
    """
    Gets the charge for the atoms specified by the user and sums them
    Parameters
    ----------
    atoms : list
        list of atoms indices
    file : str
        the name of the file that you would like to analyze
    selection : list
        the indices of the atoms that the user would like the charge and spin for

    Returns
    -------
    net_spins : list
        list fo spins corresponding to each image in the scan
    """

    # Sum the charges for the user selected atoms
    net_charges = []
    net_charge = 0
    step_count = 0
    with open(file, "r") as scan_charge_file:
        for line in scan_charge_file:
            line_list = line.split()
            if line_list[0] in atoms:
                net_charge += float(line_list[2])

            if line_list[0] == "End":
                step_count += 1
                net_charges.append("{},{}\n".format(step_count, net_charge))
                net_charge = 0

    net_charges_reference = net_charges.copy()
    for index, charge in enumerate(net_charges_reference):
        if index + 1 not in selection:
            net_charges.remove(net_charges_reference[index])

    reverse = input("Press any key to reverse data for {}: ".format(file))
    if reverse:
        net_charges.reverse()

    return net_charges


def write_data(file, net_data):
    """
    Writes out the data for either the charge or spin
    Parameters
    ----------
    file : str
        the name of the file where we are going to write out the data
    net_data : list
        list of data extracted from either the spin or charge files
    """

    with open(file, "w") as select_file:
        for pair in net_data:
            select_file.write(pair)


def charge_spin_extractor():
    print("\n.-----------------------.")
    print("| CHARGE SPIN EXTRACTOR |")
    print(".-----------------------.\n")
    print("First run organize_energy_scan_data.py for each job.")
    print("Move the scan_charge and scan_spin to the same directory.")
    print("Give them unique names.")
    print("Extract summed charge and spin for user specified atoms\n")

    # Check how many charge and spin files
    charge_files = get_files("*.charge")
    spin_files = get_files("*.spin")

    # What atoms does the user want to perform charge-spin analysis for?
    atoms = get_atoms()

    # Loop through each charge files and concatonate them
    charge_lists = []
    for file in charge_files:
        selection = get_selection(file)
        net_charge_data = get_charges(atoms, file, selection)
        charge_lists += net_charge_data
    write_data("combined_charge.csv", charge_lists)

    # Loop through each spin files and concatonate them
    spin_lists = []
    for file in spin_files:
        selection = get_selection(file)
        net_spin_data = get_spins(atoms, file, selection)
        spin_lists += net_spin_data
    write_data("combined_spin.csv", spin_lists)


if __name__ == "__main__":
    charge_spin_extractor()
