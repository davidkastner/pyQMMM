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
    
    plt.figure(figsize=(5, 4))
    plt.plot(df['Distance'], df['Relative Energy'], marker='o', color='b')
    plt.xlabel(f"{atom_1}···{atom_2} distance (Å)", weight="bold")
    plt.ylabel("relative energy (kcal/mol)", weight="bold")

    # Set x-axis limits explicitly based on the data range
    x_min, x_max = df['Distance'].min(), df['Distance'].max()
    x_range = x_max - x_min
    plt.xlim(x_max + 0.05 * x_range, x_min - 0.05 * x_range)

    plt.savefig("energy_scan.png", bbox_inches="tight", dpi=600)
    plt.show()

if __name__ == "__main__":
    atom_1 = input("   > What is your first atom being scanned? ")
    atom_2 = input("   > What is your second atom being scanned? ")

    df = read_orca_output("orca.out")
    plot_energy(df, atom_1, atom_2)
