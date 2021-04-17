import os
import shutil

def pdb_ensemblize():
    '''
    Combines separate PDBs into a single ensemble.

    Parameters
    ----------
    Does not require any parameters

    Returns
    -------
    Creates a new PDB called ensemble.pdb
        Creates a directory called ensemble for the new PDB
    '''
    model_count = 1
    dir = 'ensemble'
    if os.path.exists(dir):
        shutil.rmtree(dir)
        os.makedirs(dir)
    else:
        os.makedirs(dir)
    with open('./ensemble/ensemble.pdb', 'a') as ensemble:
        for file in os.listdir("."):
            if file.endswith(".pdb"):
                ensemble.write('MODEL        {}\n'.format(model_count))
                with open(file, 'r') as current_pdb:
                    for line in current_pdb:
                        if line[:4] == 'ATOM':
                            ensemble.write(line)
                        elif line[:3] == 'TER':
                            ensemble.write(line + 'ENDMDL\n')
                    model_count += 1

pdb_ensemblize()
