import os
import pandas as pd
import glob

def get_filenames():
    """
    Identify the only .csv and .pdb files in the current directory.

    Returns
    -------
    tuple
        The names of the identified .csv and .pdb files.
    """
    csv_files = glob.glob('*.csv')
    if len(csv_files) != 1:
        raise FileNotFoundError(f'Expected one .csv file in the current directory, found {len(csv_files)}')
    
    pdb_files = glob.glob('*.pdb')
    if len(pdb_files) != 1:
        raise FileNotFoundError(f'Expected one .pdb file in the current directory, found {len(pdb_files)}')

    return csv_files[0], pdb_files[0]

def process_and_write_pdb(csv_file, pdb_file):
    """
    Update the b-factors in a pdb file and write to a new file using data from a .csv file.

    Parameters
    ----------
    csv_file : str
        The name of the .csv file to read b-factor data from.
    pdb_file : str
        The name of the .pdb file to update.
    """
    # Get the b-factor data
    df = pd.read_csv(csv_file)
    b_factors = df.iloc[:, -1].tolist()  # Get the last column values

    # Process the pdb file and write to a new file
    with open(pdb_file, 'r') as pdb_file_obj, open('new_'+pdb_file, 'w') as new_pdb_file:
        for line in pdb_file_obj:
            if line.startswith(('ATOM', 'HETATM')):
                residue_number = int(line[22:26].strip())
                if residue_number <= len(b_factors):
                    b_factor = round(b_factors[residue_number - 1], 2)  # Round the b-factor to 2 decimal places
                    new_line = line[:60] + '{:6.2f}'.format(b_factor) + line[66:]
                    new_pdb_file.write(new_line)
                else:
                    new_pdb_file.write(line)
            else:
                new_pdb_file.write(line)

def add_bfactor():
    """
    Main function to execute the script.
    """
    csv_file, pdb_file = get_filenames()
    print('Using CSV file: {}'.format(csv_file))
    print('Using PDB file: {}'.format(pdb_file))

    process_and_write_pdb(csv_file, pdb_file)

    print('New PDB file with updated B-factors has been saved as new_'+pdb_file)

if __name__ == "__main__":
    add_bfactor()