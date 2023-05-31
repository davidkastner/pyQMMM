"""Allows you to change the starting residue of a PDB file."""

def renumber(pdb_name, offset):
    """"
    Creates a new PDB with shifted residue numbers.

    Useful when the first residue in the PDB does not match the gene.
    For example, if the PDB starts at residue 7 and you created an AMBER PDB,
    AMBER will renumber such that it now starts at 1.

    Parameters
    ----------
    pdb_name: str
        The name of the PDB that you would like to renumber.
    offset: str
        By how many residues the first residue should be changed.

    """"
    # Create a new pdb and read in the user's PDB
    with open(f"{pdb_name}_shifted.pdb", "w") as shifted_pdb:
        with open(f"{pdb_name}.pdb", "r") as original:
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

    pdb_name = input("   > Which PDB would you like to renumber (e.g., 1OS7)? ")
    offset = input("   > What number should your first residue be? ")
    renumber(pdb_name, offset)


if __name__ == "__main__":
    residue_numerator()
