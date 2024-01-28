import numpy as np
import pandas as pd
import seaborn as sns
from typing import List
import matplotlib.pyplot as plt
from matplotlib import patches

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

def heatmap(data: str, delete: List[int] = [], out_file: str = "heatmap", v=[-0.4, 0.4]) -> None:
    """
    Generates formatted heat maps.
    Uses the Kulik Lab figure formatting standards.
    Parameters
    ----------
    data: str
        The name of the data file, which can be a data or a dat file.
    delete: List[int]
        A list of the amino acids you would like removed indexed at zero.
    out_file: str
        The name you would like the image saved as.
    """

    # Sort the delete list
    delete.sort()

    # Identify matrix format and read in
    contents = open(data, "r").readlines()
    contents_joined = " ".join(contents)  # Create a single string for parsing
    if "," in contents_joined:  # If a csv file
        matrix = np.genfromtxt(data, delimiter=",")
    elif " " in contents_joined:  # If a dat file
        matrix = []
        for line in contents:
            matrix.append(line.split())
        matrix = [[float(j) for j in i] for i in matrix]  # Strings to float
        matrix = np.array(matrix)

    np.fill_diagonal(matrix, 0)  # Set the diagonal to zero as they are trivial

    df = pd.DataFrame(matrix)

    # Remove specific rows and columns from non-residues
    if len(delete) > 0:
        df = df.drop(delete, axis=0)
        df = df.drop(delete, axis=1)

    # Apply base Kulik plot parameters
    format_plot()

    # Set cmap
    cmap = "RdBu" if any(x < 0 for x in v) else "Blues"

    # Generate plot
    ax = sns.heatmap(
        df,
        cmap=cmap,
        vmin=v[0],
        vmax=v[1]
    )

    # Set labels at every 25th point, starting from 25
    label_interval = 25
    tick_positions = [i for i in range(0, len(df.columns), label_interval)]
    labels = [i if i != 0 else '' for i in tick_positions]  # Replace 0 with an empty string

    ax.set_xticks(tick_positions)
    ax.set_yticks(tick_positions)
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)

    plt.ylabel("residues", fontsize=10, weight="bold")
    plt.xlabel("residues", fontsize=10, weight="bold")
    plt.tick_params(axis="y", which="major", direction='in', labelsize=8, rotation=0, length=6)
    plt.tick_params(axis="x", which="major", direction='in', labelsize=8, rotation=90, length=6)
    ax.xaxis.tick_top()  # x axis on top
    ax.xaxis.set_label_position("top")

    # Add a black frame as a rectangle patch
    frame_linewidth = 3
    rect = patches.Rectangle((-0.5 - frame_linewidth/2, -0.5 - frame_linewidth/2), 
                             len(df.columns) + frame_linewidth, 
                             len(df.index) + frame_linewidth, 
                             linewidth=frame_linewidth, 
                             edgecolor='black', 
                             facecolor='none')
    ax.add_patch(rect)

    extensions = ["png", "svg"]
    for ext in extensions:
        plt.savefig(f"{out_file}.{ext}", format=ext, dpi=300)
    plt.close()

if __name__ == "__main__":
    heatmap(
        data="cacovar.dat",
        delete=[],
        out_file="matrix_geom",
    )
