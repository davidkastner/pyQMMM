
'''
See more here: https://github.com/davidkastner/pdb-utilities/blob/main/README.md
DESCRIPTION
   Extracts all residues from the PDB with the format RES# for SI
   Author: David Kastner
   Massachusetts Institute of Technology
   kastner (at) mit . edu
'''

# Get the name of the PDB file from the user
pdb = input('What PDB file would you like to extract the residues from? (e.g., 6L6X.pdb) ')
prev_residue = ''
with open(pdb, 'r') as pdb_file:
    for line in pdb_file:
        curr_residue = line[17:20] + line[23:32].strip()
        if curr_residue == prev_residue:
            pass
        else:
            print(curr_residue)
        prev_residue = curr_residue
