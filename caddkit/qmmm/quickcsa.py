"""Performs charge shift analysis (CSA) from TeraChem output.
This script sums the atom-wise partial charges for each residue in the QM region
(for both holo and apo structures) and then calculates the difference (holo minus apo)
for those residues common to both. In advanced CSA for metalloenzymes, some coordinating
residues are mutated to alanine in the apo structure, so the reference for apo charge
calculation is provided via <pdbname>_apo.pdb. Results are saved as CSV files.
"""

import os
import sys
import shutil
import csv
from typing import List

def clean_dir() -> str:
    """
    Searches the current directory for required files and organizes them into a 
    three-folder system: 1_input, 2_temp, and 3_out. Prompts the user for the PDB filename.

    Returns
    -------
    pdb_name : str
        The name of the PDB file (with .pdb extension) as provided by the user.
    """
    pdb_name = input("   > What is the name of your pdb (e.g., 1OS7, 6EDH, etc.)? ")
    if not pdb_name.endswith(".pdb"):
        pdb_name = f"{pdb_name}.pdb"

    file_system = ["./1_input", "./2_temp", "./3_out"]
    for directory in file_system:
        if not os.path.isdir(directory):
            os.mkdir(directory)
    file_mover(True, pdb_name)

    return pdb_name

def file_mover(file_system_exists, pdb_name) -> None:
    """
    Checks the current directory for the required files and moves them into the 
    1_input folder. For the advanced CSA, the apo reference PDB (pdbname_apo.pdb) 
    is also required.

    Parameters
    ----------
    file_system_exists : bool
        Indicator if the folder structure already exists.
    pdb_name : str
        The name of the holo PDB file.
    """
    # Build the name for the apo reference PDB
    base = pdb_name[:-4]
    apo_ref = f"{base}_apo.pdb"
    required_files = [
        pdb_name,
        apo_ref,
        "apo_list",
        "holo_list",
        "apo_charge.xls",
        "holo_charge.xls",
    ]
    for file in required_files:
        if file_system_exists and os.path.isfile(f"./1_input/{file}"):
            continue
        if os.path.isfile(f"./{file}"):
            shutil.move(f"./{file}", f"./1_input/{file}")
        else:
            print(f"{file} is not in your current directory")

def get_mask_res(type) -> List:
    """
    Reads the residue list file for the specified type (apo or holo) and returns a list 
    of residue numbers (as strings) that define the QM region.

    Parameters
    ----------
    type : str
        Specifies whether to use the 'apo' or 'holo' list file.

    Returns
    -------
    mask_list : List[str]
        List of residue numbers (as strings) included in the QM region.
    """
    try:
        with open(f"./1_input/{type}_list") as mask_res_file:
            mask_str = mask_res_file.read().strip()
            mask_list = []
            for part in mask_str.split(","):
                if "-" in part:
                    start, end = map(int, part.split("-"))
                    mask_list.extend(range(start, end+1))
                else:
                    mask_list.append(int(part))
    except FileNotFoundError:
        print(f"   > File {type}_list does not exist")
        sys.exit()

    mask_list = [str(num) for num in mask_list]
    return mask_list

def mask_maker(mask, pdb_name, type) -> None:
    """
    Creates the apo or holo mask file from the appropriate reference PDB.
    For the holo structure, the reference is pdb_name; for the apo structure, it is 
    pdb_name_apo.pdb. Only the residues specified in the mask (from apo_list/holo_list) 
    are extracted.

    Parameters
    ----------
    mask : List[str]
        List of residue numbers (as strings) to be extracted.
    pdb_name : str
        The name of the holo PDB file.
    type : str
        Indicates whether the mask is for 'apo' or 'holo'.
    """
    print(f"   > Creating the {type} mask")
    res_type_array = []
    new_pdb = f"{type}_mask"
    # Select the correct reference PDB for reading atoms.
    if type == "apo":
        # Use the apo reference PDB (e.g., 1OS7_apo.pdb)
        ref = f"{pdb_name[:-4]}_apo.pdb"
    else:
        ref = pdb_name

    with open(f"./2_temp/{new_pdb}", "w") as new_mask:
        with open(f"./1_input/{ref}", "r") as original:
            for line in original:
                # Process only ATOM records
                res_index = line[22:28].strip()
                res_type = line[:4]
                if res_type == "ATOM" and res_index in mask:
                    new_mask.write(line)
                    res_type_array.append(res_index)
                    continue
                if line.startswith("TER"):
                    continue
                if line.startswith("END"):
                    break

    print(f"   > Extracted {len(set(res_type_array))} residues")
    print(f"   > Your new file is named {new_pdb}\n")
    
    # Create temporary empty link file (placeholder)
    open(f"./2_temp/{type}_link_atoms", "w").close()

def collect_charges(type) -> None:
    """
    Collects and sums the partial charges for each residue from the TeraChem charge file.
    It uses the mask file (generated from the correct reference PDB) to map atoms to residues.
    Also processes link atom charges by adding the link atom charge to the following residue.

    Parameters
    ----------
    type : str
        Specifies whether processing 'apo' or 'holo' data.
    """
    mask_atoms = open(f"./2_temp/{type}_mask", "r").readlines()
    link_atoms = open(f"./2_temp/{type}_link_atoms", "r").readlines()
    mull_charges = open(f"./1_input/{type}_charge.xls", "r").readlines()

    prev_res_index = 0
    tot_charge = []
    res_list = []
    tot_charge_link = []
    res_list_link = []

    for index, line in enumerate(mask_atoms):
        mask_atom_info = line.split()
        res_name = mask_atom_info[3]
        res_index = int(mask_atom_info[4])
        if res_index > prev_res_index:
            res_name_index = res_name + str(res_index)
            res_list.append(res_name_index)
            res_list_link.append(res_name_index)
            tot_charge.append(0.0)
            tot_charge_link.append(0.0)
            prev_res_index = res_index

        curr_mull_charges = float(mull_charges[index].split()[2])
        tot_charge[-1] += curr_mull_charges
        tot_charge_link[-1] += curr_mull_charges

    for index, line in enumerate(link_atoms):
        mask_atom_info = line.split()
        res_name = mask_atom_info[3]
        res_index = int(mask_atom_info[4])
        res_combo = res_name + str(res_index + 1)
        if res_combo in res_list:
            res_combo_index = res_list.index(res_combo)
            curr_link_index = res_combo_index + len(mask_atoms) - 1
            link_atom_charge = float(mull_charges[curr_link_index].split()[2])
            tot_charge_link[res_combo_index] += link_atom_charge
            res_list_link[res_combo_index] = res_combo + "*"

    # Write out the residue charges as space-separated files (which will later be read)
    with open(f"./2_temp/{type}.mullres", "w") as mull, open(f"./2_temp/{type}.linkres", "w") as link:
        for idx, res in enumerate(res_list):
            mull.write(f"{res} {tot_charge[idx]}\n")
            link.write(f"{res} {tot_charge_link[idx]}\n")

def get_res_diff() -> List:
    """
    Computes the set difference between the residues present in the holo and apo mullres files.
    These are residues that are in the holo structure but missing in the apo (e.g. substrate).

    Returns
    -------
    res_diff : List[str]
        A list of residue labels (from the holo structure) that are present in holo but not apo.
    """
    holo_mull = open("./2_temp/holo.mullres", "r").readlines()
    apo_mull = open("./2_temp/apo.mullres", "r").readlines()

    holo_residues = [line.strip().split()[0] for line in holo_mull]
    apo_residues = [line.strip().split()[0] for line in apo_mull]

    holo_residues_set = set(holo_residues)
    apo_residues_set = set(apo_residues)
    res_diff = list(holo_residues_set.difference(apo_residues_set))

    return res_diff

def charge_diff(cutoff) -> None:
    """
    Calculates the difference in summed charges (holo minus apo) for residues that are common 
    to both structures, based on the mullres and linkres files. Results are saved as CSV files.
    The residue name in the output is taken from the holo structure.

    Parameters
    ----------
    cutoff : float
        Minimum absolute charge difference to report in the filtered output.
    """
    # Read the mullres files into dictionaries keyed by residue number
    def read_res_file(filename: str) -> dict:
        res_dict = {}
        with open(filename, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) < 2:
                    continue
                res_label = parts[0]      # e.g. "HIS45" or "ALA45"
                charge = float(parts[1])
                # Extract residue number from the label
                res_num = ''.join(ch for ch in res_label if ch.isdigit())
                res_dict[res_num] = (res_label, charge)
        return res_dict

    holo_mull_dict = read_res_file("./2_temp/holo.mullres")
    apo_mull_dict = read_res_file("./2_temp/apo.mullres")
    holo_link_dict = read_res_file("./2_temp/holo.linkres")
    apo_link_dict = read_res_file("./2_temp/apo.linkres")

    common_keys = sorted(set(holo_mull_dict.keys()).intersection(set(apo_mull_dict.keys())), key=lambda x: int(x))

    all_diff_mull = []
    cutoff_diff_mull = []
    all_diff_link = []
    cutoff_diff_link = []

    for key in common_keys:
        holo_label, holo_charge = holo_mull_dict[key]
        _, apo_charge = apo_mull_dict[key]
        diff = holo_charge - apo_charge
        all_diff_mull.append((holo_label, diff))
        if abs(diff) >= cutoff:
            cutoff_diff_mull.append((holo_label, round(diff, 4)))

        # Process link-res data similarly
        if key in holo_link_dict and key in apo_link_dict:
            holo_label_link, holo_charge_link = holo_link_dict[key]
            _, apo_charge_link = apo_link_dict[key]
            diff_link = holo_charge_link - apo_charge_link
            all_diff_link.append((holo_label_link, diff_link))
            if abs(diff_link) >= cutoff:
                cutoff_diff_link.append((holo_label_link, round(diff_link, 2)))

    # Write CSV output for mulliken differences
    with open("./3_out/all_diff_mullres.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Residue", "Charge Difference"])
        writer.writerows(all_diff_mull)
    with open("./3_out/cutoff_diff_mullres.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Residue", "Charge Difference"])
        writer.writerows(cutoff_diff_mull)

    # Write CSV output for link-corrected differences
    with open("./3_out/all_diff_linkmullres.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Residue", "Charge Difference"])
        writer.writerows(all_diff_link)
    with open("./3_out/cutoff_diff_linkmullres.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Residue", "Charge Difference"])
        writer.writerows(cutoff_diff_link)

def quick_csa_intro() -> None:
    """
    Introduces the user to Quick CSA and describes the required input files and naming conventions.
    """
    print("\n.----------------------.")
    print("| WELCOME TO QUICK CSA |")
    print(".----------------------.\n")
    print("Calculate the charge shift from apo and holo charge data.")
    print("Quick CSA expects the following files in the current directory:\n")
    print("  + The PDB of the protein used for QM/MM calculations (e.g., 1OS7.pdb)")
    print("  + The apo reference PDB (e.g., 1OS7_apo.pdb)")
    print("  + Residue list files for the QM regions (apo_list and holo_list)")
    print("  + TeraChem charge output files (apo_charge.xls and holo_charge.xls)")
    print("  + Example files in the tutorials folder\n")

def quick_csa() -> None:
    """
    The central handler for the Quick CSA program. Organizes input files, creates masks using 
    the appropriate PDB references, collects charges, computes charge differences, and outputs the results.
    """
    quick_csa_intro()

    print("CALCULATION")
    print("-----------")
    pdb_name = clean_dir()

    # For both apo and holo, create masks and collect charges
    for mask_name in ["apo", "holo"]:
        mask = get_mask_res(mask_name)
        mask_maker(mask, pdb_name, mask_name)
        collect_charges(mask_name)

    cutoff = float(input("What charge shift threshold would you like (e.g., 0.05)? "))
    charge_diff(cutoff)

    print("RESULTS")
    print("-------")
    print("CSV files with all and cutoff differences have been saved to the './3_out/' directory.")

if __name__ == "__main__":
    quick_csa()
