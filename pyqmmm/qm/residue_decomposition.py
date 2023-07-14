"""Extract and compare energies from a residue decomposition analysis"""

import os
import re
import pandas as pd
import matplotlib.pyplot as plt

def natural_sort(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', s)]

def get_energy(filename):
    final_energy = None
    with open(filename, 'r') as file:
        for line in file:
            if "FINAL ENERGY:" in line:
                final_energy = float(line.split()[2])
    return final_energy

def process_directory(path, ignore):
    energies = {}
    paths_to_process = []
    for root, dirs, files in os.walk(path):
        if 'qmscript.out' in files and os.path.basename(root) not in ignore:
            paths_to_process.append(root)
            
    for path in paths_to_process:
        dir_name = os.path.basename(path)
        energy = get_energy(os.path.join(path, 'qmscript.out'))
        if energy:
            energies[dir_name] = energy
    return energies

def plot_data(df):
    color_codes = [
        "#FF5733",  # Bright Red Orange
        "#8AD7A5",  # Soft Mint Green
        "#FFD700",  # Golden Yellow
        "#6B2C91",  # Deep Violet
        "#4A8F79",  # Vintage Teal
        "#F08080",  # Light Coral
        "#50B4B7",  # Aqua Marine
        "#8B7765",  # Antique Bronze
        "#6D9EEB",  # Dodger Blue
        "#C27BA0",  # Antique Fuchsia
        "#1D2951",  # Oxford Blue
        "#F4D03F",  # Naples Yellow
        "#64C4ED",  # Baby Blue Eyes
        "#E67F83",  # English Vermillion
        "#D99058"   # Lion
    ]
    fig, ax = plt.subplots()
    ax.axhline(0, color='grey', linewidth=1.5, zorder=1)  # Increased linewidth to 1.5

    for i, (index, row) in enumerate(df.iterrows()):
        legend_label = index.split('_')[1] if '_' in index else index
        if legend_label == 'all':
            ax.plot(row.index, row, label=legend_label, color='black', linewidth=2, zorder=3)  # Draw 0_all trace as bold black line
        else:
            ax.plot(row.index, row, label=legend_label, color=color_codes[i % len(color_codes)], zorder=2)
            
    # Position the legend outside the plot on the right-hand side
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.set_xlabel('pathway intermediate', weight="bold")
    ax.set_ylabel('relative energy (kcal/mol)', weight="bold")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig('energies_plot.svg', bbox_inches='tight')
    plt.savefig('energies_plot.png', dpi=300, bbox_inches='tight')

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

def residue_decomposition():
    ignore = ['0_prep']
    kcal_per_hartree = 627.509  # Replace with the correct conversion factor

    base_path = './'  # Replace with the correct path to the base directory
    data = {}
    for folder_name in sorted(os.listdir(base_path), key=natural_sort):
        if folder_name in ignore:
            continue
        folder_path = os.path.join(base_path, folder_name)
        if os.path.isdir(folder_path):
            data[folder_name] = process_directory(folder_path, ignore)

    df = pd.DataFrame(data)
    df = df.applymap(lambda x: x * kcal_per_hartree if pd.notnull(x) else x)
    
    # Make energies relative to the first energy in each row
    df = df.subtract(df.iloc[:, 0], axis=0)

    # Remove prefix from column names for x-axis labels
    df.columns = [name.split('_')[1] if '_' in name else name for name in df.columns]

    format_plot()
    plot_data(df)
    df.to_csv('energies.csv')

if __name__ == '__main__':
    residue_decomposition()
