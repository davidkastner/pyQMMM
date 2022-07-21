"""Swap any two atoms in an xyz."""

from typing import NoReturn


def swap_atoms() -> tuple[str, list[list[str]], int]:
    """
    Swap two atoms in the xyz file.

    Returns
    -------
    filename : str
        The name of the xyz file that the user would like switched
    """

    # Request user defined variables
    filename = input("What is your xyz file name? ")

    # Initialize variables used later
    lines_list: list[str] = []
    lines_lists: list[list[str]] = []
    count_lines_to_skip = True
    skipped = 0

    # with open("{}.xyz".format(filename), "r") as file:
    with open("{}.spin".format(filename), "r") as file:
        for line in file:
            lines_list.append(line)
            # If the line contains a coordinate, don't skip it
            number_of_columns = len(line.split())

            # if number_of_columns == 4:
            if number_of_columns == 10:
                count_lines_to_skip = False
            # Track the number of lines that have been skipped
            elif count_lines_to_skip:
                skipped += 1
            #
            # approaching_end = not count_lines_to_skip and len(
            #     lines_list) > skipped

            # is_xyz_header = number_of_columns != 4
            is_spin_end = "End scan" in line

            # if (is_xyz_header and approaching_end):
            if (is_spin_end):
                # last_line = lines_list.pop()
                # print(last_line)
                lines_lists.append(lines_list)
                lines_list = []
                # lines_list = [last_line]

        # lines_lists.append(lines_list)

    return filename, lines_lists, skipped


def write_scan(filename: str, lines_lists: tuple[str, list[list[str]]], skipped: int) -> NoReturn:
    """
    Write the lines from the scan with the switched atoms.

    Parameters
    ----------
    filename : str
        The name of the xyz file that the user would like switched
    lines_lists : list[list[str]]
        List of the coordinate lines
    skipped : int
        The number of lines that were skipped
    """

    # Get atoms from user and verify that the user has entered a number
    try:
        atom1 = int(input(f"What is the first atom to switch? "))
        atom2 = int(input(f"What is the second atom to switch? "))
    except SystemExit:
        print("Please enter a number.")

    # with open(f"{filename}_{atom1}_{atom2}.xyz", "w") as newfile:
    with open(f"{filename}_{atom1}_{atom2}.spin", "w") as newfile:
        for lines in lines_lists:
            atom1_line = lines[atom1 + skipped - 1]
            atom2_line = lines[atom2 + skipped - 1]
            lines[atom2 + skipped - 1] = atom1_line
            lines[atom1 + skipped - 1] = atom2_line
            for line in lines:
                newfile.write(line)


def pair_spin_swapper():
    print('\n.-------------------.')
    print('| PAIR SPIN SWAPPER |')
    print('.-------------------.\n')
    print('Sometimes atoms get switched between comparing scans.')
    print('This script gives you a way to switch then back.\n')

    filename, lines_lists, skipped = swap_atoms()
    write_scan(filename, lines_lists, skipped)


# Executes the function when run as a script
if __name__ == "__main__":
    pair_spin_swapper()
