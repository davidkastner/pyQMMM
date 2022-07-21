"""Swap any two atoms in an xyz."""

from typing import NoReturn


def swap_xyz(filename: str) -> tuple[list[list[str]], int]:
    """
    Swap two atoms in a spin file.

    Parameters
    ----------
    filename : str
        The name of the xyz file that the user would like switched

    Return
    ------
    lines_lists : list[list[str]]
        List of lists containing each section of the file
    skipped : int
        The number of lines thast were skipped
    """

    # Initialize variables used later
    lines_list: list[str] = []
    lines_lists: list[list[str]] = []
    count_lines_to_skip = True
    skipped = 0

    with open(f"{filename}", "r") as file:
        for line in file:
            lines_list.append(line)
            # If the line contains a coordinate, don't skip it
            if len(line.split()) == 4:
                count_lines_to_skip = False
            # Track the number of lines that have been skipped
            elif count_lines_to_skip:
                skipped += 1
            if (
                len(line.split()) != 4
                and not count_lines_to_skip
                and len(lines_list) > skipped
            ):
                last_line = lines_list.pop()
                lines_lists.append(lines_list)
                lines_list = [last_line]
        lines_lists.append(lines_list)

    return lines_lists, skipped


def swap_spins(filename: str) -> tuple[list[list[str]], int]:
    """
    Swap two atoms in the xyz file.

    Parameters
    ----------
    filename : str
        The name of the xyz file that the user would like switched

    Return
    ------
    lines_lists : list[list[str]]
        List of lists containing each section of the file
    skipped : int
        The number of lines thast were skipped
    """

    # Initialize variables used later
    lines_list: list[str] = []
    lines_lists: list[list[str]] = []
    count_lines_to_skip = True
    skipped = 0
    with open(f"{filename}", "r") as file:
        for line in file:
            lines_list.append(line)
            # If the line contains a coordinate, don't skip it
            number_of_columns = len(line.split())
            if number_of_columns == 10:
                count_lines_to_skip = False
            # Track the number of lines that have been skipped
            elif count_lines_to_skip:
                skipped += 1
            is_spin_end = "End scan" in line

            if (is_spin_end):
                lines_lists.append(lines_list)
                lines_list = []

    return lines_lists, skipped


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

    # Get requested file extension
    pre = filename.split(".")[0]
    ext = filename.split(".")[-1]
    with open(f"{pre}_{atom1}_{atom2}.{ext}", "w") as newfile:
        for lines in lines_lists:
            atom1_line = lines[atom1 + skipped - 1]
            atom2_line = lines[atom2 + skipped - 1]
            lines[atom2 + skipped - 1] = atom1_line
            lines[atom1 + skipped - 1] = atom2_line
            for line in lines:
                newfile.write(line)


def pair_swapper():
    print('\n.--------------.')
    print('| PAIR SWAPPER |')
    print('.--------------.\n')
    print('Sometimes atoms get switched between comparing scans.')
    print('This script gives you a way to switch then back.\n')

    filename = input("What is your xyz file name (e.g., 1.xyz, 2.spin)? ")
    if filename.split(".")[-1] == "xyz":
        lines_lists, skipped = swap_xyz(filename)
    if filename.split(".")[-1] == "spin":
        lines_lists, skipped = swap_spins(filename)
    write_scan(filename, lines_lists, skipped)


# Executes the function when run as a script
if __name__ == "__main__":
    pair_swapper()
