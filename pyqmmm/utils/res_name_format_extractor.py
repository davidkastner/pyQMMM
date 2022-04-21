def res_name_format_extractor():

    """
    Combine the residue name and index of a protien (e.g., Ala100).

    This script solves the specific problem of obtaining residues for SI tables.
    In a PDB residues are of the form 'PRO   103' on each line,
    and contains duplicates for each at in the residue.
    This script parses a PDB to get a unique list of the residues in a protein.

    """

    # Parse the input text and clean the data
    with open("Book1.txt", "r") as atom_list:
        res_list = []  # A variable for storing processed residues
        # Loop through a list with residue names and numbers
        for line in atom_list:
            id_and_name = line.split()
            # Remove atoms where the atom ID is an empty string
            id_and_name[1] = id_and_name[1].strip()
            if len(id_and_name[1]) == 1:
                continue
            else:
                id_and_name[1] = int(id_and_name[1])
            # Remove atoms where the residue name is an empty string
            id_and_name[0] = id_and_name[0].strip()
            if len(id_and_name[0]) == 0:
                continue
            res_list.append(id_and_name)

    # Remove duplicates as each residue as many atoms each as a new line
    clean_res_list = []
    for res in res_list:
        if res not in clean_res_list:
            clean_res_list.append(res)

    # Write the formatted final residues to a new file
    with open("residues.dat", "w") as file_res_file:
        for res in clean_res_list:
            # Combine the residue name and index e.g., Ala100
            res_combined = res[0] + str(res[1])
            file_res_file.write(res_combined + "\n")


if __name__ == "__main__":
    res_name_format_extractor()
