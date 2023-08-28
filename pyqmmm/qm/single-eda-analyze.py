import re
import sys
import glob
import pandas as pd
import matplotlib.pyplot as plt

kj_to_kcal = 0.239006  # Conversion factor from kJ/mol to kcal/mol

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

def read_data_from_csv() -> dict:
    """
    Reads the only .csv in the working directory and returns a dictionary of energies.
    
    """
    csv_files = glob.glob("*.csv")
    
    if len(csv_files) != 1:
        print("Expected exactly one CSV file in the directory.")
        sys.exit(1)
    
    data = pd.read_csv(csv_files[0])
    
    # Convert energies to kcal/mol
    for column in data.columns:
        data[column] = data[column] * kj_to_kcal
    
    return data.to_dict(orient="records")[0]  # Return the first (and only) row as a dictionary

def plot_energies():
    residue_name = input("What is the name of you residue? ")
    format_plot()
    energies_dict = read_data_from_csv()
    labels = list(energies_dict.keys())
    values = list(energies_dict.values())
    colors = ['#8ecae6', '#219ebc', '#023047', '#ffb703', '#fb8500', '#DD1C1A']

    fig, ax = plt.subplots(figsize=(4.5, 4.5))

    # Plot bars with labels for legend
    for label, value, color in zip(labels, values, colors):
        ax.bar(label, value, color=color, label=label)

    ax.set_ylabel('Energy (kcal/mol)', weight="bold")
    ax.axhline(0, linewidth=2, color="gray")
    plt.legend(
        bbox_to_anchor=(1.04, 0.8), loc="center left", borderaxespad=0, frameon=False
    )

    # Save figures
    plt.savefig(f"ALMO-EDA_{residue_name}.png", bbox_inches="tight", dpi=300, transparent=True)
    plt.savefig(f"ALMO-EDA_{residue_name}.svg", bbox_inches="tight")

if __name__ == "__main__":
    plot_energies()