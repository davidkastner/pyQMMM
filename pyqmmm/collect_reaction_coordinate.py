'''
See more here: https://github.com/davidkastner/quick-csa/blob/main/README.md
DESCRIPTION
    Get the energy and reaction coordinate for each step of a TeraChem scan.
    Author: David Kastner
    Massachusetts Institute of Technology
    kastner (at) mit . edu
SEE ALSO
    energy_collector.py
'''
################################ DEPENDENCIES ##################################
from scipy.spatial import distance

################################## FUNCTIONS ###################################
'''
Get the user's reaction coordinate definition.
Returns
-------
atoms : list
    list of atoms indices
'''
def user_input():
    # What two atoms define your reaction coordinate distance
    my_atoms = input('What atoms define your reaction coordinate (e.g., 49,70)?')

    # Convert user input to a list even if it is hyphenated
    temp = [(lambda sub: range(sub[0], sub[-1] + 1))(list(map(int, ele.split('-')))) for ele in my_atoms.split(',')] 
    atoms = [b for a in temp for b in a] 

    return atoms

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
def get_reaction_coordinate(atoms):
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
    energy_list = []
    with open('./qmscript.out', 'r') as out_file:
        first_energy = None
        for line in out_file:
            if line[6:22] == 'Optimized Energy':
                energy = float(line[26:42])
                if first_energy == None:
                    first_energy = energy
                relative_energy = (energy - first_energy) * 627.5
                energy_list.append(relative_energy)

    return energy_list

'''
Combine reaction coordinate and energy list and write them to a .dat file
Parameters
----------
dist_list : list
    List of distances defining each step of the reaction coordinate
energy_list : list
    List of all energies mapping to each step of the reacitno coordinate
'''    
def get_reaction_dat(dist_list, energy_list):
    print(len(dist_list), len(energy_list))
    with open('./rc.dat', 'w') as dat_file:
        for dist,energy in zip(dist_list,energy_list):
            dat_file.write('{} {}\n'.format(dist, energy))

# General function handler
def reaction_coordinate_collector():
    print('\n.------------------------------------------.')
    print('| WELCOME TO REACTION COORDINATE COLLECTOR |')
    print('.------------------------------------------.\n')
    print('Run this script in the same directory where you ran your TeraChem job.')
    print('Extracts energies and a reaction coordiante.\n')

    atoms = user_input()
    dist_list = get_reaction_coordinate(atoms)
    energy_list = get_opt_energies()
    get_reaction_dat(dist_list, energy_list)

if __name__ == "__main__":
    reaction_coordinate_collector()
