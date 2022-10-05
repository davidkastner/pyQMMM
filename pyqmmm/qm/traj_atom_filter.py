"""Generate a new trajectory with only selected atoms."""

def get_selection():
    """
    Request the user's atom set.

    Returns
    -------
    selection : list[int]
        A list of atoms.
    """


    selection = input(f"What atoms would you like in the new traj (e.g. 1-50,52-60)? ")

    # Convert user input to a list even if it is hyphenated
    temp = [
        (lambda sub: range(sub[0], sub[-1] + 1))(list(map(int, ele.split("-"))))
        for ele in selection.split(",")
    ]
    selection = [int(b) for a in temp for b in a]

    return selection

def remove_atoms(selection: list[int]):
    """
    Takes an atom selection as input.
    Generates a new trajectory with only those atoms.
    The final format is the .xyz format.

    Parameters
    ----------
    selection : list[int]
        A list of atoms.

    """


def traj_atom_filter():
    print("\n.------------------.")
    print("| TRAJ ATOM FILTER |")
    print(".------------------.\n")
    print("Requests the atoms to keep.")
    print("Removes the atoms from the trajectory.")
    print("Writes out a new trajectory.")

    selection = get_selection()
    remove_atoms()


# Executes the function when run as a script
if __name__ == "__main__":
    traj_atom_filter()