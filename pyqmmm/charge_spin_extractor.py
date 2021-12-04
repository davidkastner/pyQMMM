'''
See more here: https://github.com/davidkastner/quick-csa/blob/main/README.md
DESCRIPTION
    Extract charge and spin data for a given subset of atoms for graphing.
    Written to interpet TeraChem mullpop and charge_mull.xls files.
    Author: David Kastner
    Massachusetts Institute of Technology
    kastner (at) mit . edu
SEE ALSO
    scan_data_organizer.py
'''

################################## FUNCTIONS ###################################
'''
Get the user's atom set.
Returns
-------
atoms : list
    list of atoms indices
'''
def user_input():
    # What atoms would the user like to sum the spin for
    my_atoms = input('What atom indexes would you like to sum (e.g., 58-76)?')

    # Convert user input to a list even if it is hyphenated
    temp = [(lambda sub: range(sub[0], sub[-1] + 1))(list(map(int, ele.split('-')))) for ele in my_atoms.split(', ')] 
    atoms = [str(b) for a in temp for b in a] 

    return atoms

'''
Gets the charges for the atoms specified by the user and sums them
Parameters
----------
atoms : list
    list of atoms indices
'''
def get_spins(atoms):
    # Sum the spins for the user selected atoms
    net_spins = []
    net_spin = 0
    scan_step_count = 0
    with open('./scan_spin', 'r') as scan_spin_file:
        for line in scan_spin_file:
            line_list = line.split()
            if line_list[0] in atoms:
                net_spin += float(line_list[9])

            if line_list[0] == 'End':
                scan_step_count += 1
                net_spins.append('{} {}\n'.format(scan_step_count, net_spin))
                net_spin = 0
    
    with open('./select_spin', 'w') as select_spin_file:
        for pair in net_spins:
            select_spin_file.write(pair)

'''
Gets the charge for the atoms specified by the user and sums them
Parameters
----------
atoms : list
    list of atoms indices
'''
def get_charges(atoms):
    # Sum the charges for the user selected atoms
    net_charges = []
    net_charge = 0
    scan_step_count = 0
    with open('./scan_charge', 'r') as scan_charge_file:
        for line in scan_charge_file:
            line_list = line.split()
            if line_list[0] in atoms:
                net_charge += float(line_list[2])

            if line_list[0] == 'End':
                scan_step_count += 1
                net_charges.append('{} {}\n'.format(scan_step_count, net_charge))
                net_charge = 0
    
    with open('./select_charge', 'w') as select_charge_file:
        for pair in net_charges:
            select_charge_file.write(pair)


# General function handler
def charge_spin_extractor():
    print('\n.----------------------------------.')
    print('| WELCOME TO CHARGE-SPIN EXTRACTOR |')
    print('.----------------------------------.\n')
    print('First run scan_data_organizer')
    print('Extracts summed charge and spin for user specified atoms\n')

    atoms = user_input()
    get_charges(atoms)
    get_charges(atoms)

if __name__ == "__main__":
    charge_spin_extractor()
