import re
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

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

def read_data(file_name):
    # Read the second column from the file
    return np.loadtxt(file_name, usecols=[1], skiprows=1)

def get_legend_labels(file):
    atoms = re.split("[.-]", file)[1]
    legend = f"{atoms[0]}···{atoms[1]}"

    return legend


def get_colors(files):
    # Assign the color palette
    if len(files) == 1:
        colors = ['#08415c']
    elif len(files) == 2:
        colors = ['#cc2936', '#08415c']
    elif len(files) == 3:
        colors = ['#cc2936', '#08415c', "#ABABAB"]

    return colors


def get_plot(files):

    colors = get_colors(files)
    legend = []
    for index,file in enumerate(files):
        
        # Read data from the files
        data_NC = read_data(file)

        format_plot()

        # Create a histogram with a KDE line for NC data
        bin_count = 150
        label = get_legend_labels(file)
        legend.append(label)
        sns.histplot(data_NC, bins=bin_count, kde=True, color=colors[index], linewidth=0, alpha=0.55, label=label)

        # Add labels and title if desired
        plt.xlabel('distance (Å)', fontsize=10, weight="bold")
        plt.ylabel('frequency', fontsize=10, weight="bold")
        plt.legend(frameon=False)

    extensions = ["png", "svg"]
    out_name = "_".join(legend)
    for ext in extensions:
        plt.savefig(f"{out_name}.{ext}", bbox_inches="tight", format=ext, dpi=600)

if __name__ == "__main__":
    files = input("What distance files would you like to plot? ").split(",")
    get_plot(files)