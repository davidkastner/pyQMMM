"""Generate a DSSP plot from CPPTraj analysis"""

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import pandas as pd
import numpy as np

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


def process_data(file):
    df = pd.read_csv(file, sep='\\s+')

    chunk_size = 125000 # Number of frames per replicate

    # Create an empty list to hold the counts for each chunk
    counts_list = []

    # Loop over the DataFrame in chunks
    for i in range(0, df.shape[0], chunk_size):
        chunk = df.iloc[i:i+chunk_size]
        count = (chunk == 4).sum()
        count = count.reindex(df.columns, fill_value=0)
        counts_list.append(count)

    counts_df = pd.concat([count.to_frame().T for count in counts_list], ignore_index=True)

    # Save the DataFrame to a CSV file
    counts_df.to_csv('replicates.csv', index=False)

    return counts_df


def plot_data(dfs):
    format_plot()

    # Determine the global min and max across all dataframes
    global_min = min(df.min().min() for df in dfs)
    global_max = max(df.max().max() for df in dfs)

    for i, counts_df in enumerate(dfs):
        fig, ax = plt.subplots(figsize=(10, 5))  # Create a subplot for each dataframe
        cax = ax.imshow(counts_df, cmap='viridis', interpolation='nearest', vmin=global_min, vmax=global_max)

        # Set the x-ticks and y-ticks
        plt.sca(ax)  # Set the current Axes instance to 'ax'
        plt.xticks(range(len(counts_df.columns)), np.arange(1, len(counts_df.columns)+1))
        plt.yticks(range(len(counts_df)), np.arange(1, len(counts_df)+1))

        plt.xlabel("residue number", fontweight="bold")
        plt.ylabel("trajectory number", fontweight="bold")

        # Create the colorbar
        cbar = fig.colorbar(cax, ax=ax)
        cbar.set_label("#Frames DSSP Helix", weight='bold')

        # Save each heatmap as a separate PNG file
        ext = "png"
        plt.savefig(f"dssp_{i+1}.{ext}", bbox_inches="tight", format=ext, dpi=300)
        plt.close()


def combine_dssp_files():
    files = ["dssp_1.dat", "dssp_2.dat", "dssp_3.dat"]
    df_list = [process_data(file) for file in files]
    plot_data(df_list)


if __name__ == "__main__":
    # Run the command-line interface when this script is executed
    combine_dssp_files()
