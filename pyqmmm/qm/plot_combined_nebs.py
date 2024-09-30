"""Generalizable script for plotting the PES of an xyz trajectory with NEB boundaries."""

import matplotlib.pyplot as plt
import numpy as np
import csv
import time
import os
import re

HARTREE_TO_KCAL = 627.509

def get_xyz_files():
    """
    List all NEB xyz files in the current directory, sorted numerically.
    """
    files = os.listdir('.')
    xyz_files = [f for f in files if re.match(r'^\d+\.xyz$', f)]
    xyz_files.sort(key=lambda x: int(re.match(r'(\d+)', x).group()))
    return xyz_files

def write_energies_to_csv(total_energies, filename="energy_plot_data.csv"):
    """
    Write the energies to a CSV file.

    Parameters
    ----------
    total_energies : list
        List of concatenated energies for all NEBs in kcal/mol.
    filename : str
        The name of the output CSV file.
    """
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Frame", "Energy (kcal/mol)"])
        for i, energy in enumerate(total_energies):
            writer.writerow([i, energy])

def parse_energy(line, software):
    """
    Parse the energy from a line based on the software used.

    Parameters
    ----------
    line : str
        Line from the file containing energy information.
    software: str
        The software used for the calculation.

    Returns
    -------
    float
        The energy extracted from the line, in Hartrees.

    """
    if software == "ORCA-MEP" or software == "ORCA-IRC":
        energy_str = line.split()[5]
    elif software == "ORCA":
        energy_str = line.split()[4]
    elif software == "TeraChem-scan":
        energy_str = line.split()[4]
    elif software == "TeraChem-opt":
        energy_str = line.split()[0]
    else:
        raise ValueError(f"Unsupported software: {software}")

    return float(energy_str)

def get_trajectory_energies(filename, software):
    """
    Parse the energies from an xyz trajectory file.

    Parameters
    ----------
    filename : str
        Path to the trajectory file.
    software: str
        Software used for the calculation.

    Returns
    -------
    tuple
        First value is a list of absolute energies for each frame, in kcal/mol.
        Second value is the first frame energy in kcal/mol.
        Third value is a list of absolute energies in Hartrees.

    """
    energies_hartrees = []
    with open(filename, "r") as f:
        while True:
            line = f.readline()
            if not line:
                break  # end of file

            atom_count = int(line.strip())
            # next line should contain energy
            energy_line = f.readline().strip()
            # parse and append energy
            energies_hartrees.append(parse_energy(energy_line, software))
            # skip atom lines
            for _ in range(atom_count):
                f.readline()

    # Convert energies to kcal/mol (absolute energies)
    energies_kcal_abs = [e * HARTREE_TO_KCAL for e in energies_hartrees]
    first_energy_kcal = energies_kcal_abs[0]

    return energies_kcal_abs, first_energy_kcal, energies_hartrees

def identify_software(line):
    """
    Identify the software used for the calculation from a line.

    Parameters
    ----------
    line : str
        Line from the file.

    Returns
    -------
    str
        Identifier of the software used for the calculation.
    """
    if "ORCA-job qmscript_MEP" in line:
        return "ORCA-MEP"
    elif "ORCA-job qmscript_IRC_Full" in line:
        return "ORCA-IRC"
    elif "ORCA-job qmscript" in line:
        return "ORCA"
    elif "Converged     Job" in line:
        return "TeraChem-scan"
    elif "TeraChem" in line:
        return "TeraChem-opt"
    else:
        raise ValueError(f"Could not identify software from line: {line}")

def format_plot() -> None:
    """
    General plotting parameters.

    """
    font = {"family": "sans-serif", "weight": "bold", "size": 10}
    plt.rc("font", **font)
    plt.rcParams["xtick.major.pad"] = 5
    plt.rcParams["ytick.major.pad"] = 5
    plt.rcParams["axes.linewidth"] = 2
    plt.rcParams["xtick.major.size"] = 7
    plt.rcParams["xtick.major.width"] = 2
    plt.rcParams["ytick.major.size"] = 7
    plt.rcParams["ytick.major.width"] = 2
    plt.rcParams["xtick.direction"] = "in"
    plt.rcParams["ytick.direction"] = "in"
    plt.rcParams["xtick.top"] = True
    plt.rcParams["ytick.right"] = True
    plt.rcParams["svg.fonttype"] = "none"

def collect_data():
    """
    Collect energies from the NEB xyz files and calculate NEB boundaries.

    Returns
    -------
    list
        A list of concatenated absolute energies for all NEBs in kcal/mol.
    float
        The first frame energy of the first NEB in kcal/mol.
    list
        A list of cumulative frame counts where each NEB ends.
    """
    xyz_files = get_xyz_files()
    energies_by_file = {}
    first_energies = []
    frames_per_neb = []

    for idx, filename in enumerate(xyz_files):
        with open(filename, "r") as f:
            # read two lines to get to the software info
            f.readline()
            software_line = f.readline()
            software = identify_software(software_line)

        energies_kcal_abs, first_energy_kcal, energies_hartrees = get_trajectory_energies(filename, software)
        energies_by_file[filename] = energies_kcal_abs
        first_energies.append(first_energy_kcal)

        if idx < len(xyz_files) - 1:
            frames_per_neb.append(len(energies_kcal_abs) - 1)  # Exclude last frame
        else:
            frames_per_neb.append(len(energies_kcal_abs))  # Include last frame for the last NEB

    # Compute cumulative frames to get NEB boundaries
    cumulative_frames = [0]
    for frames in frames_per_neb:
        cumulative_frames.append(cumulative_frames[-1] + frames)

    # NEB boundaries (excluding the final total frame count)
    neb_boundaries = cumulative_frames[1:-1]

    first_energy_kcal_of_first_neb = first_energies[0]

    # Concatenate energies, excluding duplicate frames
    total_energies_abs = []
    for idx, filename in enumerate(xyz_files):
        energies = energies_by_file[filename]
        if idx < len(xyz_files) - 1:
            energies = energies[:-1]  # Exclude last frame except for last NEB
        total_energies_abs.extend(energies)

    return total_energies_abs, first_energy_kcal_of_first_neb, neb_boundaries

def plot_data(total_energies_abs, first_energy_kcal_of_first_neb, dim_list, neb_boundaries):
    """
    Plot the collected energies with NEB boundaries.

    Parameters
    ----------
    total_energies_abs : list
        List of concatenated absolute energies for all NEBs in kcal/mol.
    first_energy_kcal_of_first_neb : float
        The first frame energy of the first NEB in kcal/mol.
    dim_list : list
        Dimensions for the plot.
    neb_boundaries : list
        List of cumulative frame counts where each NEB ends.
    """

    format_plot()
    fig, ax = plt.subplots(figsize=(dim_list[0], dim_list[1]))

    # Adjust energies so that first frame is at 0 kcal/mol
    energies = [e - first_energy_kcal_of_first_neb for e in total_energies_abs]

    x_values = range(len(energies))

    # Plotting the energy line
    ax.plot(
        x_values,
        energies,
        marker="o",
        linestyle="-",
        color='b',
    )

    # Add vertical lines at NEB boundaries
    for boundary in neb_boundaries:
        ax.axvline(x=boundary, color='black', linestyle='-', lw=3, alpha=0.1, zorder=0)

    # Annotate the highest point
    max_energy = max(energies)
    max_energy_frame = energies.index(max_energy)
    ax.annotate(f"{max_energy:.1f}", (max_energy_frame, max_energy),
                textcoords="offset points", xytext=(0, 10), ha='center', va='bottom')

    # Extend y-axis to fit annotation
    y_lim = ax.get_ylim()
    ax.set_ylim(y_lim[0], y_lim[1] + (y_lim[1] - y_lim[0]) * 0.1)  # Adding 10% padding at the top

    ax.set_xlabel("NEB frames", weight="bold")
    ax.set_ylabel("Relative energy (kcal/mol)", weight="bold")

    # Save the figure with enough padding
    extensions = ["png", "svg"]
    for ext in extensions:
        plt.savefig(
            f"energy_plot.{ext}",
            dpi=600,
            bbox_inches="tight",
            format=ext,
        )

def plot_energies():
    """
    Main function that combines previous functions to generate the plot.
    """
    print("\n.---------------------------.")
    print("| WELCOME TO ENERGY PLOTTER |")
    print(".---------------------------.\n")
    print("> Generates a plot of an xyz trajectory.")
    print("> Can handle an arbitrary number of xyz trajectories")

    start_time = time.time()  # Used to report the execution speed

    dim = input("   > What dimensions would you like the plot (e.g. 5,4)? ")
    if dim:
        x_dim = int(dim.split(",")[0])
        y_dim = int(dim.split(",")[1])
        dim_list = [x_dim, y_dim]
    else:
        dim_list = [4, 4]

    total_energies_abs, first_energy_kcal_of_first_neb, neb_boundaries = collect_data()
    write_energies_to_csv(total_energies_abs)  # Write energies to CSV
    plot_data(total_energies_abs, first_energy_kcal_of_first_neb, dim_list, neb_boundaries)

    total_time = round(time.time() - start_time, 3)  # Seconds to run the function
    job_summary = f"""
        --------------------------ENERGY PLOTTER END--------------------------
        RESULT: Plotted energies for combined NEBs.
        OUTPUT: Created a plot called 'energy_plot.png' and a CSV file called 'energy_plot_data.csv' in the current directory.
        TIME: Total execution time: {total_time} seconds.
        --------------------------------------------------------------------\n
        """

    print(job_summary)

if __name__ == "__main__":
    plot_energies()
