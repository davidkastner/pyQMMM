"""
Plots the results of an ORCA scan.

This script was difficult to write because of a strange matplotlib issue.
No matter how I entered the data, maplotlib would autosort the x-axis.
To fix this, I had to manually set the axes and add padding.
"""

import matplotlib.pyplot as plt

HARTREE_TO_KCAL_MOL = 627.509

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

def read_orca_output(file_name):
    with open(file_name, 'r') as file:
        lines = file.readlines()
    
    start_reading = False
    distances = []
    relative_energies = []
    first_energy_kcal_mol = None

    for line in lines:
        if "The Calculated Surface using the 'Actual Energy'" in line:
            start_reading = True
            continue
        if start_reading:
            if line.strip():
                parts = line.split()
                try:
                    distance = float(parts[0])
                    energy_hartree = float(parts[1])
                    energy_kcal_mol = energy_hartree * HARTREE_TO_KCAL_MOL
                    if first_energy_kcal_mol is None:
                        first_energy_kcal_mol = energy_kcal_mol
                    relative_energy = energy_kcal_mol - first_energy_kcal_mol
                    distances.append(distance)
                    relative_energies.append(relative_energy)
                except ValueError:
                    break
            else:
                break

    return distances, relative_energies

def plot_energy(distances, relative_energies, atom_1, atom_2):
    format_plot()

    # Create a figure with adjustable size
    fig, ax = plt.subplots(figsize=(4, 4))

    # Plot the data using lists
    ax.plot(distances, relative_energies, color='b')
    ax.scatter(distances, relative_energies, marker='o', color='b')

    # Find and annotate the highest energy point
    max_energy_index = relative_energies.index(max(relative_energies))
    max_energy = relative_energies[max_energy_index]
    max_distance = distances[max_energy_index]
    ax.annotate(f"{max_energy:.1f}", (max_distance, max_energy),
                textcoords="offset points", xytext=(0, 5), ha='center', va='bottom')

    # Set the x-axis and y-axis limits with padding
    x_range = max(distances) - min(distances)
    y_range = max(relative_energies) - min(relative_energies)
    x_padding = x_range * 0.06
    y_padding = y_range * 0.15  # Adjusted to give more room

    # Check if it's ascending or descending to add padding
    ax.set_ylim([min(relative_energies) - y_padding, max(relative_energies) + y_padding])
    if distances[0] < distances[-1]:
        ax.set_xlim([distances[0] - x_padding, distances[-1] + x_padding])
    else: 
        ax.set_xlim([distances[0] + x_padding, distances[-1] - x_padding])
    
    ax.set_xlabel(f"{atom_1}···{atom_2} distance (Å)", weight="bold")
    ax.set_ylabel("Relative energy (kcal/mol)", weight="bold")

    plt.savefig("energy_scan.png", bbox_inches="tight", dpi=600)
    plt.savefig("energy_scan.svg", bbox_inches="tight", format="svg")

# Main execution
if __name__ == "__main__":
    atom_1 = input("   > What is your first atom being scanned? ")
    atom_2 = input("   > What is your second atom being scanned? ")

    distances, relative_energies = read_orca_output("orca.out")
    print(f"   > Start distance: {distances[0]}, End distance: {distances[-1]}\n")
    plot_energy(distances, relative_energies, atom_1, atom_2)

