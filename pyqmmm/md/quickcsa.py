"""Performs charge shift analysis (CSA) form TeraChem output."""

import os
import sys
import shutil


def clean_dir() -> str:
    """
    Searches the current directory for files, prints missing file alerts.

    Cleans the directory into a three-folder system: 1_input, 2_temp, and 3_out.

    Parameters
    ----------
    pdb_name : str
        The name of the PDB that the user would like processed.

    Returns
    -------
    pdb_name: str
        The name of the PDB that the user would like processed.


    """
    # Asks the user for the name of the pdb that they would like to process
    pdb_name = input("What is the name of your pdb (e.g., 1OS7, 6EDH, etc.)? ")
    extension = pdb_name[-4:]
    if extension != ".pdb":
        pdb_name = "{}.pdb".format(pdb_name)

    # Directory and required file names for the file system
    file_system = ["./1_input", "./2_temp", "./3_out"]
    # Create the three file system for the user for cleaner file management
    file_system_exists = False
    for dir in file_system:
        if os.path.isdir(dir):
            file_system_exists = True
        else:
            os.mkdir(dir)
    file_mover(file_system_exists, pdb_name)

    return pdb_name


def file_mover(file_system_exists, pdb_name) -> None:
    """
    Check the current directory for the five required files and move them.

    Parameters
    ----------
    file_system_exists : boolean
        The path of the user's full PDB.
    """
    required_files = [
        pdb_name,
        "apo_list",
        "holo_list",
        "apo_charge.xls",
        "holo_charge.xls",
    ]
    for file in required_files:
        file_already_moved = False
        if file_system_exists:
            if os.path.isfile("./1_input/{}".format(file)):
                file_already_moved = True

        if file_already_moved == False:
            if os.path.isfile("./{}".format(file)):
                shutil.move("./{}".format(file), "./1_input/{}".format(file))
            else:
                print("{} is not in your current directory".format(file))


def get_mask_res(type) -> List[]:
    """
    Create a list of the residues that should belong to the holo/apo regions.

    Parameters
    ----------
    type : str
        Tell function if it is the holo or apo list.

    Returns
    -------
    mask_list : List[]
        An array of all the residues that the user wants included in their mask.
    """
    try:
        with open("./1_input/{}_list".format(type)) as mask_res_file:
            mask_list = mask_res_file.read().strip().split(",")
    except SystemExit:
        print("File {}_list does not exist".format(type))
        sys.exit()

    return mask_list


def mask_maker(mask, pdb_name, type) -> None:
    """
    Create the apo and holo masks from the original PDB file.

    Parameters
    ----------
    raw_mask : str
        A list of residues that the user wants pulled from the original PDB.
    pdb_name : str
        The name of the user's original PDB file from which we create the mask.
    type : str
        Tell function if it is the holo or apo mask.
    """

    print("Creating the {} mask".format(type))
    # Create a list from the users input
    # The code for Mask Maker begins here
    res_type_array = []
    new_pdb = "{}_mask".format(type)
    with open("./2_temp/{}".format(new_pdb), "w") as new_mask:
        with open("./1_input/{}".format(pdb_name), "r") as original:
            for line in original:
                # Start checking once we reach the ATOM section
                res_index = line[22:28].strip()
                res_type = line[:4]
                if res_type == "ATOM" and res_index in mask:
                    new_mask.write(line)
                    res_type_array.append(res_index)
                    continue
                # We don't won't to count chain breaks as a discarded residue
                if line[:3] == "TER":
                    continue
                # We don't want to include the last line so we watch for END
                if line[:3] == "END":
                    break

    # Print important statistics for the user
    print(f"Extracted {len(set(res_type_array))} residues")
    print("Your new file is named {}\n".format(new_pdb))
    
    # Make temporary empty link files
    open("./2_temp/{}_link_atoms".format(type), "w")  # TODO: add section


def collect_charges(type) -> None:
    """
    Collect the charges from the charge.xls file.

    Parameters
    ----------
    type : str
        Tell function if it is the holo or apo mask.
    """
    # Open the mask atoms and link atoms files
    mask_atoms = open("./2_temp/{}_mask".format(type), "r").readlines()
    link_atoms = open("./2_temp/{}_link_atoms".format(type), "r").readlines()

    # Initialize variables and lists
    prev_res_index = 0
    tot_charge = []
    res_list = []
    tot_charge_link = []
    res_list_link = []
    mull_charges = open("./1_input/{}_charge.xls".format(type), "r").readlines()

    # Loop through each atom in mask file and get residue name and its index
    for index, line in enumerate(mask_atoms):
        mask_atom_info = line.split()
        res_name = mask_atom_info[3]
        res_index = int(mask_atom_info[4])

        # For each new residue, record the current residue and set as previous
        if res_index > prev_res_index:
            res_name_index = res_name + str(res_index)
            res_list.append(res_name_index)
            res_list_link.append(res_name_index)
            tot_charge.append(0.0)
            tot_charge_link.append(0.0)
            prev_res_index = res_index

        # Create running list of all charges in charge.xls
        curr_mull_charges = float(mull_charges[index].split()[2])
        tot_charge[-1] += curr_mull_charges
        tot_charge_link[-1] += curr_mull_charges

    # Get residue name and index for each line
    for index, line in enumerate(link_atoms):
        mask_atom_info = line.split()
        res_name = mask_atom_info[3]
        res_index = int(mask_atom_info[4])
        res_combo = res_name + str(res_index + 1)

        # If the same residues types are side-by-side get the link atom charge
        if res_combo in res_list:
            res_combo_index = res_list.index(res_combo)
            curr_link_index = res_combo_index + len(mask_atoms) - 1
            link_atom_charge = float(mull_charges[curr_link_index].split()[2])
            tot_charge_link[res_combo_index] += link_atom_charge
            res_list_link[res_combo_index] = res_combo + "*"

    # Create files for link and mulliken residue data
    # Write residues to files
    mull = open("./2_temp/{}.mullres".format(type), "w")
    link = open("./2_temp/{}.linkres".format(type), "w")

    for idx, res in enumerate(res_list):
        mull.write("{} {}\n".format(res, tot_charge[idx]))
        link.write("{} {}\n".format(res, tot_charge_link[idx]))

    mull.close()
    link.close()


def get_res_diff() -> List[]:
    """
    Calculate the charge difference for the apo and holo residue list files.

    Returns
    -------
    res_diff : list
        A list of the residues that were removed in the holo structure.
    """
    holo_mull = open("./2_temp/holo.mullres", "r").readlines()
    apo_mull = open("./2_temp/apo.mullres", "r").readlines()

    # Loop thorugh the mullres files and get the holo residues
    holo_residues = []
    for line in holo_mull:
        holo_res = line.strip("\n").split()[0]
        holo_residues.append(holo_res)

    # Loop thorugh the mullres files and get the apo residues
    apo_residues = []
    for line in apo_mull:
        apo_res = line.strip("\n").split()[0]
        apo_residues.append(apo_res)

    # Get the difference between the two lists
    holo_residues_set = set(holo_residues)
    apo_residues_set = set(apo_residues)
    res_diff = list(holo_residues_set.difference(apo_residues_set))

    return res_diff


def charge_diff() -> None:
    """
    Calculate the difference in the charges for the apo and holo residue lists.

    Parameters
    ----------
    ns_res_list : list
        A list of the residues that were removed in the holo structure.
    """
    # Get the differences in the charges for the holo and apo structures
    res_diff = get_res_diff()
    # Open recently created holo and apo charge files
    holo_mull = open("./2_temp/holo.mullres", "r").readlines()
    holo_link = open("./2_temp/holo.linkres", "r").readlines()
    apo_mull = open("./2_temp/apo.mullres", "r").readlines()
    apo_link = open("./2_temp/apo.linkres", "r").readlines()

    # Initialize variables
    diff_charge = []
    res_list = []
    diff_charge_link = []
    res_list_link = []
    n = 0

    # Calculate the differences in the charges for the holo and apo
    for idx, line in enumerate(holo_mull):
        holo_mull_res, holo_mull_charge = line.strip("\n").split()
        holo_link_res, holo_link_charge = holo_link[idx].strip("\n").split()
        if holo_mull_res in res_diff:
            n -= 1
        else:
            _, apo_mull_charge = apo_mull[idx + n].strip("\n").split()
            _, apo_link_charge = apo_link[idx + n].strip("\n").split()
            diff = float(holo_mull_charge) - float(apo_mull_charge)
            diff_link = float(holo_link_charge) - float(apo_link_charge)
            res_list.append(holo_mull_res)
            res_list_link.append(holo_link_res)
            diff_charge.append(diff)
            diff_charge_link.append(diff_link)

    # Create final files with the differences in charges for all residues
    diff_all = open("./3_out/all.diffmullres", "w")
    diff_link_all = open("./3_out/all.difflinkmullres", "w")

    # Create final files with the differences in charges for differences > 0.05
    diff_cutoff = open("./3_out/cutoff.diffmullres", "w")
    diff_link_cutoff = open("./3_out/cutoff.difflinkmullres", "w")

    # Write the final charge differences out to a new file
    for res in range(len(apo_mull)):
        diff_all.write("{} {}\n".format(res_list[res], diff_charge[res]))
        diff_link_all.write("{} {}\n".format(res_list_link[res], diff_charge_link[res]))

    # Check if the absolute value is greater than our cutoff of 0.05
    cutoff = 0.05
    for res in range(len(apo_mull)):
        if abs(diff_charge[res]) >= cutoff:
            diff_cutoff.write("{} {}\n".format(res_list[res], diff_charge[res]))
        if abs(diff_charge_link[res]) >= cutoff:
            diff_link_cutoff.write(
                "{} {}\n".format(res_list_link[res], diff_charge_link[res])
            )


def quick_csa_intro() -> None:
    """
    Introduces the user to Quick CSA and provides information on how it is run.
    Contains information about the required files and the naming conventions.
    """
    print("\n.----------------------.")
    print("| WELCOME TO QUICK CSA |")
    print(".----------------------.\n")
    print("Calculate the charge shift from apo and holo charge data.")
    print("Quick CSA looks for the following files in the current directory:\n")
    print("+ The complete PDB of the protein of interest")
    print("   - Quick CSA will look for the extension .pdb")
    print("+ A list of the residues for the apo and holo regions")
    print("   - Apo list file should be called apo_list")
    print("   - Holo list file should be called holo_list")
    print("+ The TeraChem charge output files")
    print("   - Apo file should be called apo_charge.xls")
    print("   - Holo file should be called holo_cahrge.xls\n")


def quick_csa() -> None:
    """
    The central handler funtion for the Quick CSA program.
    This function is also provided as a module in the pyQM/MM package.
    """
    # Introduce user to Quick CSA
    quick_csa_intro()

    # Get the user's full PDB
    print("CALCULATION")
    print("-----------")
    pdb_name = clean_dir()

    # Get mask arrays from user-provided input difflinkmullres
    mask_list = ["apo", "holo"]
    for mask_name in mask_list:
        mask = get_mask_res(mask_name)
        # Create apo and holo mask files
        mask_maker(mask, pdb_name, mask_name)
        # Create list of residues with their associated charges for apo and holo_link
        collect_charges(mask_name)

    # Create the final output file with the charge differences for all residues
    # Create output files for only the residues with a charge differences > 0.050.
    charge_diff()

    # Print the user's results
    print("RESULTS")
    print("-------")
    with open("./3_out/cutoff.diffmullres", "r") as results:
        print(results.read())


# Execute the Quick CSA when run as a script but not if used as a pyQM/MM module
if __name__ == "__main__":
    quick_csa()
