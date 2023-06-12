import matplotlib.pyplot as plt
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

def plot_energies(energies, ref_energy):
    """
    Plot energy values relative to a reference energy.

    Parameters
    ----------
    energies : list
        A list of energy values from each frame.
    ref_energy : float
        The reference energy value to which other energies are compared.
    """
    # Subtract the reference energy from all energy values
    relative_energies = [energy - ref_energy for energy in energies]

    # Generate x values as frame numbers
    x = list(range(len(relative_energies)))

    plt.plot(x, relative_energies, '-o', markersize=5, color='blue')
    plt.xlabel('Frame', weight="bold")
    plt.ylabel('Energy (kcal/mol)', weight="bold")
    plot_name = "energy_plot.png"
    
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

def process_xyz_files():
    """
    Process xyz files and plot energy values.

    This function assumes that there are files named R.xyz and P.xyz,
    and an arbitrary number of files named IM*.xyz.
    """
    # Process the R.xyz file
    r_energies = read_energy_from_xyz("R.xyz")
    ref_energy = r_energies[0]

    # Process IM*.xyz files
    im_files = sorted(glob.glob("IM*.xyz"))
    im_energies = []
    for im_file in im_files:
        im_energies.extend(read_energy_from_xyz(im_file))

    # Process the P.xyz file
    p_energies = read_energy_from_xyz("P.xyz")

    # Combine all energy values and plot
    all_energies = r_energies + im_energies + p_energies
    format_plot()
    plot_energies(all_energies, ref_energy)

if __name__ == "__main__":
    process_xyz_files()