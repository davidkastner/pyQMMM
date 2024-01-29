"""Plot the RMSD analysis from CPPTraj"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

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

def dat2df(dat_file, rows_to_skip=1):
    """
    Convert a dat file into a DataFrame.

    Parameters
    ----------
    dat_file : str
        The name of the dat file.

    Returns
    -------
    df : pd.DataFrame
        Dataframe with RMSD data.

    """
    df = pd.read_csv(
        dat_file, sep="\s+", header=None, skiprows=rows_to_skip, index_col=0
    )
    df.index = [x / 500 for x in range(df.shape[0])]
    df = df.iloc[1:, :]
    return df


def get_plot(rmsd_df, yaxis_title, layout='wide'):
    """
    General plotting function for RMSD.

    Parameters
    ----------
    rmsd_df : pd.DataFrame
        Dataframe with RMSD data.
    layout : str
        'square' for square dimensions, 'wide' for default.

    """
    if layout == 'square':
        plt.figure(figsize=(5, 5))
        filename = f"rmsd_{layout}.png"
    if layout == 'wide':
        plt.figure(figsize=(6, 4))
        filename = f"rmsd_{layout}.png"

    plt.scatter(
        rmsd_df.index,
        rmsd_df[1],
        edgecolors="#808080",
        s=9,
        facecolors="none",
        alpha = 0.25
    )

    plt.rc("axes", linewidth=2.5)
    plt.ylabel(f"{yaxis_title}", fontsize=16, weight="bold")
    plt.xlabel("time (ns)", fontsize=16, weight="bold")
    plt.tick_params(labelsize=14)
    plt.tick_params(which="both", bottom=True, top=True, left=True, right=True)
    plt.tick_params(which="minor", length=5, color="k", width=2.5)
    plt.savefig(filename, bbox_inches="tight", dpi=600)


def rmsd_plotter(yaxis_title, layout='wide'):
    # Welcome user and print some instructions
    print("\n.--------------.")
    print("| RMSD PLOTTER |")
    print(".--------------.\n")
    print("This script will search your directory for the following output:")
    print("+ Root mean square deviation > rmsd.dat\n")

    format_plot()

    # Check for required files
    expected_dat = "rmsd.dat"

    # Check the users directory for analyzeable files
    data_file = Path(expected_dat)
    if data_file.exists():
        print("Found {}".format(expected_dat))
    else:
        print("No {}".format(expected_dat))
        print("Please add {} to your directory".format(expected_dat))
        exit()

    rmsd_df = dat2df(expected_dat)
    get_plot(rmsd_df, yaxis_title, layout)


# Execute the function when run as a script
if __name__ == "__main__":
    yaxis_title = "RMSD (Å)"
    layout = "wide"
    rmsd_plotter(yaxis_title, layout)
