import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm
import numpy as np
import glob
import os
import re

# Define constant
HARTREE_TO_KCAL = 627.509

def read_energy_from_xyz(filename):
    """
    Extract energy values from an xyz file.

    Parameters
    ----------
    filename : str
        The name of the xyz file.

    Returns
    -------
    energies : list
        A list of energy values from each frame in the file.
    """
    energies = []
    with open(filename, "r") as file:
        for line in file:
            if line.startswith("Converged"):
                energy_hartree = float(line.split()[4])
                energy_kcal = energy_hartree * HARTREE_TO_KCAL
                energies.append(energy_kcal)
    return energies

def format_plot() -> None:
    """
    General plotting parameters for the Kulik Lab.

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

def plot_group_energies(group_files, ref_energy, offset, color):
    """
    Process a group of related intermediate files and plot their energies.

    Parameters
    ----------
    group_files : list
        A list of filenames related to a single intermediate step.
    ref_energy : float
        The reference energy value to which other energies are compared.
    offset : int
        The current frame offset for the x-axis.
    color : str
        The color to use when plotting this group's energies.

    Returns
    -------
    offset : int
        The updated frame offset for the x-axis.
    """
    for filename in group_files:
        energies = read_energy_from_xyz(filename)
        relative_energies = [energy - ref_energy for energy in energies]
        x = list(range(offset, offset + len(relative_energies)))
        plt.plot(x, relative_energies, '-o', markersize=5, color=color, label=os.path.splitext(filename)[0])
        offset += len(relative_energies)
    return offset

def read_files():
    """
    Read xyz files and group them by base name.
    """
    files = sorted(glob.glob("*.xyz"), key=lambda x: (x.split(".")[0].split("-")[0], len(x), x))

    grouped_files = {}
    for file in files:
        group_name = re.findall(r'(R|P|IM\d+)', file)[0]  # Updated regex to capture "R", "P", "IM1", "IM2", etc.
        if group_name not in grouped_files:
            grouped_files[group_name] = []
        grouped_files[group_name].append(file)

    return grouped_files

def process_xyz_files():
    """
    Process xyz files and generate plot data.
    """
    grouped_files = read_files()
    plot_data = []
    max_versions = max([len(group) for group in grouped_files.values()])  # Maximum number of versions in any group

    # Process the R.xyz file first to get the reference energy
    r_energies = read_energy_from_xyz("R.xyz")
    ref_energy = r_energies[0]  # Reference energy is the first energy of the R scan
    plot_data.append(('R', list(range(len(r_energies))), [energy - ref_energy for energy in r_energies], 0))  # Adding data to plot

    # Initial offset is just after the R scan
    offset = len(r_energies)

    # Process each group of files, excluding 'R' which we already processed
    total_groups = len(grouped_files) - 1  # '-1' to exclude 'R'
    group_number = 1  # '1' to give unique color to R
    for group_name, group in grouped_files.items():
        if group_name == 'R':
            continue
        for i, filename in enumerate(sorted(group)):  # Ensure files are processed in order
            energies = read_energy_from_xyz(filename)
            relative_energies = [energy - ref_energy for energy in energies]
            x = list(range(offset, offset + len(relative_energies)))
            color = (group_number * max_versions + i) / (total_groups * max_versions)  # Save color index
            plot_data.append((os.path.splitext(filename)[0], x, relative_energies, color))
            offset += len(relative_energies) if 'v' not in filename else 0  # if a versioned intermediate, don't advance the offset
        group_number += 1

    return plot_data

def generate_plot(color_scheme):
    """
    Generate plot using processed data.
    """
    plt.figure(figsize=(7,4))
    plot_data = process_xyz_files()
    format_plot()
    all_cmap_names = set(matplotlib.cm.cmaps_listed.keys()) | set(matplotlib.cm.datad.keys())

    if color_scheme == "":
        colormap = lambda x: 'blue'  # if no input, use 'blue' for all
    elif color_scheme in all_cmap_names:
        colormap = plt.get_cmap(color_scheme)  # use the specified colormap if it exists
    else:
        print(f"Unrecognized color scheme {color_scheme}. Defaulting to 'tab20'")
        colormap = plt.cm.tab20  # default to 'tab20' if the colormap isn't recognized

    for (label, x, relative_energies, color_index) in plot_data:
        plt.plot(x, relative_energies, '-o', markersize=3, color=colormap(color_index), label=label)

    plt.xlabel('Frame', weight="bold")
    plt.ylabel('Energy (kcal/mol)', weight="bold")
    
    # Legend outside the plot on the right side
    plt.legend(bbox_to_anchor=(1.04,0.5), loc="center left", borderaxespad=0)

    # Save plot as PNG
    plot_name_png = "energy_plot.png"
    plt.savefig(
        plot_name_png,
        dpi=300,
        bbox_inches="tight",
    )
    
    # Save plot as SVG
    plot_name_svg = "energy_plot.svg"
    plt.savefig(
        plot_name_svg,
        dpi=300,
        bbox_inches="tight",
    )
    
if __name__ == "__main__":
    color_scheme = input("What color scheme would you like (e.g., tab20, viridis)? ")
    generate_plot(color_scheme)