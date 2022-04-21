"""
Docs: https://github.com/davidkastner/pyQMMM/blob/main/pyqmmm/README.md
DESCRIPTION
    Allows you to change the starting residue of a PDB file.

    Author: David Kastner
    Massachusetts Institute of Technology
    kastner (at) mit . edu

"""

################################## FUNCTIONS ###################################


def renumber(pdb_name, offset):
    # Create a new pdb and read in the user's PDB
    with open("{}_shifted.pdb".format(pdb_name), "w") as shifted_pdb:
        with open("{}.pdb".format(pdb_name), "r") as original:
            # Loop through each line in the PDB
            for line in original:
                line_list = line.split(" ")
                count = 0
                # Find the residue count, always the second numerical value
                for index, entry in enumerate(line_list):
                    if entry.isnumeric():
                        count += 1
                    if count == 2:
                        # Add the offset onto the second integar in the line
                        entry_len = len(entry)
                        new_entry = str(int(entry) + int(offset) - 1)
                        line_list[index] = new_entry
                        del_spaces = len(new_entry) - entry_len
                        if del_spaces:
                            del line_list[index - del_spaces : index]
                        break
                # Write out the new line
                shifted_pdb.write(" ".join(line_list))


def residue_numerator():
    # Introduce user to Renumber Residues functionality
    print("\n.-------------------.")
    print("| RESIDUE NUMERATOR |")
    print(".-------------------.\n")
    print("Renumbers all residues in a PDB from an integar of your choice.")
    print("------------------------\n")

    pdb_name = input("Which PDB would you like to renumber (e.g., 1OS7)? ")
    offset = input("What number should your first residue be? ")
    renumber(pdb_name, offset)


if __name__ == "__main__":
    residue_numerator()
