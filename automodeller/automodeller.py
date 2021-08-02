'''
Docs: https://github.com/davidkastner/pdb-utilities/automodeller.py
DESCRIPTION
   Automates the process of replacing missing residues with Modeller.
   Author: David Kastner
   Massachusetts Institute of Technology
   kastner (at) mit . edu
SEE ALSO
    N/A
'''
################################ DEPENDENCIES ##################################
import numpy as np
import glob
import sys
import os.path
from modeller import *
from modeller.automodel import *
################################## FUNCTIONS ###################################
'''
Searches the current directory for the user's PDB file.
Parameters
----------
Returns
-------
'''
def check_pdb():
    return

'''
Searches the current directory for a PDB file.
Parameters
----------
Returns
-------
'''
def check_pdb():
    return

'''
Description
Parameters
----------
Returns
-------
'''
def step_1():
    code = input("Enter a PDB accession: ") 
    e = Environ()
    m = Model(e, file=code)
    aln = Alignment(e)
    aln.append_model(m, align_codes=code)
    aln.write(file=code+'.seq')
    print('A sequence file for {} was generated.'.format(code))
    return

'''
Description
Parameters
----------
Returns
-------
'''
def step_2():
    log.verbose()
    env = Environ()
    # directories for input atom files
    env.io.atom_files_directory = ['.', '../atom_files']
    code = input("Enter a PDB accession: ")
    class MyModel(AutoModel):
        def select_atoms(self):
            return Selection(self.residue_range('29:A', '30:A'),self.residue_range('324:A', '326:A'))
    a = MyModel(env, alnfile = '{}.ali'.format(code),
                knowns = code, sequence = '{}_fill'.format(code))
    a.starting_model= 1
    a.ending_model  = 1
    a.make()
    return


################################ AUTOMODELLER ##################################
# Introduce user to HyScore Eval functionality
print('WELCOME TO AUTOMODELLER')
print('--------------------------\n')
print('Automates the process of replacing missing residues with Modeller.')
print('+ Checks the current directory for a PDB file')
print('+ Analyzes the PDB file based on the header information')
print('------------------------\n')

# Get filenames from output directory