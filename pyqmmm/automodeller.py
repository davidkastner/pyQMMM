'''
Docs: https://github.com/davidkastner/pdb-utilities/automodeller.py
DESCRIPTION
   Automates the process of replacing missing residues with Modeller.
   Author: David Kastner
   Massachusetts Institute of Technology
   kastner (at) mit . edu

'''
################################ DEPENDENCIES ##################################
import numpy as np
import glob
import sys
import os.path
import shutil
from modeller import *
from modeller.automodel import *
################################## CONSTANTS ###################################
aa_lookup = {'CYS':'C', 'ASP':'D', 'SER':'S', 'GLN':'Q', 'LYS':'K',
             'ILE':'I', 'PRO':'P', 'THR':'T', 'PHE':'F', 'ASN':'N', 
             'GLY':'G', 'HIS':'H', 'LEU':'L', 'ARG':'R', 'TRP':'W', 
             'ALA':'A', 'VAL':'V', 'GLU':'E', 'TYR':'Y', 'MET':'M',
              None:'-'}
################################## FUNCTIONS ###################################
'''
Identify the user's primary PDB file.

Parameters
----------

Returns
-------
pdb_name : str
    The file name of the users PDB that will be used to create masks.
pdb_file : str
    The pdb name and the extenstion.
'''
def get_pdb_name():
    pdb_name_pattern = r'./1_in/*.pdb'
    # Collect all files ending in .pdb located in the current directory
    pdbs = glob.glob(pdb_name_pattern)
    if len(pdbs) == 0:
        print('No PDB file in 1_in')
        sys.exit()
    if len(pdbs) > 1:
        print('More than one PDB has been provided')
        sys.exit()
    # Extract the name of the PDB file
    pdb_file = pdbs[0]
    pdb = pdbs[0].split('/')[-1]
    pdb_name = pdb.split('.')[0]
    return pdb_name, pdb_file

'''
Get sequences from provided fasta file deposited in 1_in.

Parameters
----------
pdb_name : str
    The name of the user's PDB 
Returns
-------
fasta : dict
    The fasta seq with the index as the key and amino acid as the value
'''
def get_fasta(pdb_name):
    fasta_file_name = '{}.fasta'.format(pdb_name)
    # Check if the seq file exists
    if os.path.isfile('./1_in/{}'.format(fasta_file_name)):
        print('Found fasta file {}'.format(fasta_file_name))
    else:
        print('{} not found'.format(fasta_file_name))
        sys.exit()
    # Combine the lines from the fasta file into a single list
    fasta_list = []
    with open('./1_in/{}'.format(fasta_file_name), 'r') as fasta_file:
        for line in fasta_file:
            if line[0] == '>':
                continue
            else:
                fasta_list += list(line.strip())
    # Create a dictionary with the Res ID as the key and amino acid as the value
    fasta_seq = {}
    for index,item in enumerate(fasta_list):
        fasta_seq[index + 1] = item
    return fasta_seq

'''
Generate the modeller seq file.
Parameters
----------
pdb_name : str
    The name of the user's PDB 
pdb_file : str
    The pdb name and the extenstion.
Returns
-------
N/A
'''
def step_1(pdb_name, pdb_file):
    modeller_env = Environ()
    model = Model(modeller_env, file = pdb_file)
    aln = Alignment(modeller_env)
    aln.append_model(model, align_codes = pdb_name)
    aln.write(file = './2_temp/{}.seq'.format(pdb_name))
    print('A sequence file for {} was generated.'.format(pdb_name))
    return

'''
Using the Modeller seq file, create a list of the extracted residues.

Parameters
----------
pdb_name : str
    The name of the user's PDB
pdb_file : str
    The pdb name and the extenstion.
Returns
-------
mod_seq : list
    The modeller seq as a list with one-letter codes as elements.
    Missing residues are delineated with a - character.
'''
def get_mod_seq(pdb_name, pdb_file, aa_lookup):
    # Create a dictionary to convert between three and two letter codes
    
    # Get the sequence reported in the .seq file produced by Modeller
    with open('./2_temp/{}.seq'.format(pdb_name), 'r') as seq_file:
        mod_seq = []
        header = []
        for index,line in enumerate(seq_file):
            # Skip the first empty lines and get save the header
            if index < 3 and index > 0:
                header.append(line)
            if index > 2:
                mod_seq.append(list(line.strip()))
    return mod_seq, header

'''
Using the PDB, create a dict with keys as res IDs and values as amino acids.

Parameters
----------
pdb_name : str
    The name of the user's PDB
pdb_file : str
    The pdb name and the extenstion
Returns
-------
pdb_seq : dict
    Res IDs keys and amino acid values with missing residues with None type
'''
def get_pdb_seq(pdb_name, pdb_file, fasta_seq, aa_lookup):
    # Initialize the dictionary for storing the AA and res ID's
    pdb_seq = {}
    end_index = len(fasta_seq)
    # Loop through the user provided PDB file
    with open(pdb_file, 'r') as seq_file:
        index = 1
        # In each line of PDB, check the res ID and the residue name
        for line in seq_file:
            # Check to see if we have reached the end
            if line[0:3] == 'TER':
                while index <= end_index:
                    pdb_seq[index] = '-'
                    index += 1
                break
            # Get the residue name and its ID
            res = line[17:20].strip()
            res = aa_lookup[res]
            resid = int(line[22:26].strip())
            # Check if there are missing residues
            while index < resid:
                pdb_seq[index] = '-'
                index += 1
            # If there are no missing residues and we are at a new res, add it
            if resid not in pdb_seq:
                index += 1
            pdb_seq[resid] = res

    return pdb_seq

'''
Compare fasta and modeller seq files.
Create the .ali file that Modeller needs for part 2.

Parameters
----------
pdb_name : str
    The name of the user's PDB
fasta : list
    The fasta seq in list form with one-letter codes as elements
Returns
-------
'''
def get_ali(pdb_seq, fasta_seq, pdb_name, header):
    # Begin creating the .ali file
    with open('./2_temp/{}.ali'.format(pdb_name), 'w') as ali_file:
        # Check if the pdb and fasta extracted sequences are the same length
        if len(pdb_seq) == len(fasta_seq):
            print('The PDB and FASTA sequences match')
        else:
            print('The PDB and FASTA sequences do not match')
        # Convert dictionaries to lists so we can write out strings
        pdb_list = list(pdb_seq.values()) + ['*']
        fasta_list = list(fasta_seq.values()) + ['*']
        # Write the header information to the ali file
        for line in header:
            ali_file.write(str(line))
        # A Modeller line consists of 75 residues
        n = 75
        # Divide the ali list into N sublists of 75 characters
        pdb_str = ''.join(pdb_list)
        pdb_lines=[pdb_str[i:i + n] for i in range(0, len(pdb_str), n)]
        for line in pdb_lines:
            ali_file.write('{}\n'.format(line))
        print('The first section of the .ali file was written')
        
        # Write the second section of the ali file from the fasta dictionary    
        ali_file.write('{}_fill\n'.format(str(header[0].strip())))
        ali_file.write('sequence:::::::::\n')
        fasta_str = ''.join(fasta_list)
        fasta_lines=[fasta_str[i:i + n] for i in range(0, len(fasta_str), n)]
        for line in fasta_lines:
            ali_file.write('{}\n'.format(line))
        print('The second section of the .ali file was written')
    return

'''
The second step of Modeller software
Parameters
----------
Returns
-------
'''
def step_2(pdb_name, pdb_file):
    # log.verbose()
    env = Environ()
    # directories for input atom files
    env.io.atom_files_directory = ['./1_in', './2_temp']
    class MyModel(AutoModel):
        def select_atoms(self):
            return Selection(self.residue_range('1:A', '30:A'),
                             self.residue_range('324:A', '326:A'))
    a = MyModel(env, alnfile = './2_temp/{}.ali'.format(pdb_name),
                knowns = pdb_name, sequence = '{}_fill'.format(pdb_name))
    a.starting_model = 1
    a.ending_model  = 1
    a.make()
    return

'''
To address messy and strange file and naming conventions of Modeller,
we will clean up the output files for the user to save time.
Parameters
----------
N/A
Returns
-------
N/A
'''
def clean_up(pdb_name):
    # Get the names of all files and directories in the current directory
    out_files = os.listdir('./')
    for file in out_files:
        # Move non py, pdb files that were generated to 2_temp
        if '.pdb' in file:
            os.rename(file, './3_out/{}_filled.pdb'.format(pdb_name))
        elif '.py' in file:
            continue
        elif os.path.isfile(file):
            shutil.move(os.path.join('./', file), os.path.join('./2_temp', file))
    return

# Introduce user to Automodeller functionality
def automate_modeller(aa_lookup):
   print('\n.----------------------------.')
   print('|WELCOME TO AUTOMATE MODELLER|')
   print('.----------------------------.\n')
   print('Automates the process of replacing missing residues with Modeller.\n')
   
    # Step 1: Get the name of the PDB and also its location
    pdb_name, pdb_file = get_pdb_name()

    # Step 2: Get the full fasta sequence to find missing residues
    fasta_seq = get_fasta(pdb_name)
    
    # Step 3: Run Modeller to generate the .seq file
    step_1(pdb_name, pdb_file)
    
    # Step 4: Get the sequence from the PDB, which may be missing residues
    pdb_seq = get_pdb_seq(pdb_name, pdb_file, fasta_seq, aa_lookup)

    # Step 5: Extract the modeller seq and the header infor and store as lists
    seq, header = get_mod_seq(pdb_name, pdb_file, aa_lookup)
    
    # Step 6: Generate the .ali file that Modeller needs for the next step
    get_ali(pdb_seq, fasta_seq, pdb_name, header)
    
    # Step 7: Run Modeller's part two of the Missing Residue workflow
    step_2(pdb_name, pdb_file)
    
    # Step 8: Clean up the mess left behind by Modeller
    clean_up(pdb_name)  
    return


if __name__ == "__main__":
    automate_modeller()
