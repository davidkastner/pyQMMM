import numpy as np
import pandas as pd
import seaborn as sns
from typing import List
import matplotlib.pyplot as plt

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

def heatmap(data: str, residues: List[str], delete: List[int] = [], 
            out_file: str = "heatmap", v=[-0.4, 0.4]) -> None:
    
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

    Examples
    --------
    heatmap(data="cacovar.dat", protein="mc6sa", delete=[0,15,16,27,28,29], out_file="matrix_geom.svg")

    """

    # General styling variables
    light_gray = "#8e8e8e"
    dark_gray = "#7e7e7e"
    
    # Sort the delete list
    delete.sort()
    
    # Delete residues
    residues = [item for index, item in enumerate(residues) if index not in delete]

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

    # Drop rows and columns
    if len(delete) > 0:
        df = df.drop(delete, axis=0)
        df = df.drop(delete, axis=1)

    df.columns = residues
    df.index = residues

    # Apply base Kulik plot parameters
    format_plot()

    # Set cmap
    cmap = "RdBu" if any(x < 0 for x in v) else "Blues"

    # Generate plot
    ax = sns.heatmap(
        df,
        cmap=cmap,
        vmin=v[0],
        vmax=v[1],
        xticklabels=True,
        yticklabels=True,
        linewidth=0.03,
        linecolor=light_gray,
    )
    ax.get_yaxis().set_tick_params(direction="out")
    plt.ylabel("residues", fontsize=10, weight="bold")
    plt.xlabel("residues", fontsize=10, weight="bold")
    plt.tick_params(axis="y", which="major", labelsize=8, rotation=0, length=0)
    plt.tick_params(axis="x", which="major", labelsize=8, rotation=90, length=0)
    ax.xaxis.tick_top()  # x axis on top
    ax.xaxis.set_label_position("top")
    # Add lines every five residues
    ax.hlines([5, 10, 15, 20, 25], colors=dark_gray, *ax.get_xlim(), linewidth=1.5)
    ax.vlines([5, 10, 15, 20, 25], colors=dark_gray, *ax.get_ylim(), linewidth=1.5)
    # Add broders
    ax.hlines([0, len(residues)], colors="k", *ax.get_xlim(), linewidth=3.5)
    ax.vlines([0, len(residues)], colors="k", *ax.get_ylim(), linewidth=3.5)

    extensions = ["png", "svg"]
    for ext in extensions:
        plt.savefig(f"{out_file}.{ext}", bbox_inches="tight", format=ext, dpi=300)
    plt.close()

if __name__ == "__main__":
    pdb_path = f"../1_cluster/1/rep.c0.pdb"
    residues = qa.process.get_protein_sequence(pdb_path)
    delete = []
    heatmap(
        data="cacovar.dat",
        residues=residues,
        delete=delete,
        out_file="matrix_geom.png",
    )