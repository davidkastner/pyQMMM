'''
See more here: https://github.com/davidkastner/pdb-utilities/blob/main/README.md
DESCRIPTION
   Allows you to change the starting residue of a PDB file
   Author: David Kastner
   Massachusetts Institute of Technology
   kastner (at) mit . edu
SEE ALSO
   renumerate.py
'''

def renumerate():
    print('So your PDB numbers are shifted?')
    pdb_loc = input('Which PDB file is off? ')
    offset = input('What number is your first residue? ')

    with open('shifted_pdb.pdb', 'w') as shifted_pdb:
        with open(pdb_loc, 'r') as original:
            for line in original:
                line_list = line.split(" ")
                count = 0
                for index,entry in enumerate(line_list):
                    if entry.isnumeric():
                        count += 1
                    if count == 2:
                        entry_len = len(entry)
                        new_entry = str(int(entry) + int(offset) - 1)
                        line_list[index] = new_entry
                        del_spaces = len(new_entry) - entry_len
                        if del_spaces:
                            del line_list[index - del_spaces:index]
                        break
                shifted_pdb.write(' '.join(line_list))

renumerate()
