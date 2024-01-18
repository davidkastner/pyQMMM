import matplotlib.pyplot as plt
import pandas as pd

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
    data = []
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
                    data.append((distance, relative_energy))
                except ValueError:
                    break
            else:
                break
    df = pd.DataFrame(data, columns=['Distance', 'Relative Energy'])

    return df

def plot_energy(df, atom_1, atom_2):
    format_plot()
    
    # Create a figure with adjustable size
    fig = plt.figure(figsize=(4, 4))  # Start with a larger figure size
    ax = fig.add_subplot(111)

    # Plot the data
    ax.plot(df['Distance'], df['Relative Energy'], marker='o', color='b')
    ax.set_xlabel(f"{atom_1}···{atom_2} distance (Å)", weight="bold")
    ax.set_ylabel("relative energy (kcal/mol)", weight="bold")

    # Set x-axis and y-axis limits explicitly based on the data range
    x_min, x_max = df['Distance'].min(), df['Distance'].max()
    y_min, y_max = df['Relative Energy'].min(), df['Relative Energy'].max()
    x_range = x_max - x_min
    y_range = y_max - y_min
    ax.set_xlim(x_min - 0.05 * x_range, x_max + 0.05 * x_range)
    ax.set_ylim(y_min - 0.05 * y_range, y_max + 0.05 * y_range)

    # Adjust the aspect ratio of the plot area to be square based on data ranges
    ratio = x_range / y_range
    ax.set_aspect(ratio, adjustable='box')

    plt.savefig("energy_scan.png", bbox_inches="tight", dpi=600)
    plt.savefig("energy_scan.svg", bbox_inches="tight", format="svg")

if __name__ == "__main__":
    atom_1 = input("   > What is your first atom being scanned? ")
    atom_2 = input("   > What is your second atom being scanned? ")

    df = read_orca_output("orca.out")
    plot_energy(df, atom_1, atom_2)
