"""Plots a clustered trajectory by RMSD and identifies the centroid"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def dat2df(dat_file, rows_to_skip=1):
    """
    Convert a the cluster data dat file into a DataFrame.

    Parameters
    ----------
    dat_file : str
        The name of the dat file.

    Returns
    -------
    df : pd.DataFrame
        Dataframe with clustering data.

    """
    df = pd.read_csv(
        dat_file, sep="\s+", header=None, skiprows=rows_to_skip, index_col=0
    )
    df.index = [x / 500 for x in range(df.shape[0])]
    df = df.iloc[1:, :]
    return df


def get_plot(final_df, centroid_frame_ns, yaxis_title, cluster_count, layout='wide'):
    """
    General plotting function.

    Parameters
    ----------
    final_df : pd.DataFrame
        Dataframe with clustering data.
    centroid_frame_ns : int
        The frame number of the computed centroid.
    layout : str
        'square' for square dimensions, 'wide' for default.

    """
    if layout == 'square':
        plt.figure(figsize=(5, 5))
        filename = "clus_rmsd_square.png"
    else:
        filename = "clus_rmsd.png"

    font = {"family": "sans-serif", "weight": "bold", "size": 10}
    plt.rc("font", **font)
    plt.rcParams["axes.linewidth"] = 2.5
    plt.rcParams["xtick.major.size"] = 10
    plt.rcParams["xtick.major.width"] = 2.5
    plt.rcParams["ytick.major.size"] = 10
    plt.rcParams["ytick.major.width"] = 2.5
    plt.rcParams["xtick.direction"] = "in"
    plt.rcParams["ytick.direction"] = "in"
    plt.rcParams["mathtext.default"] = "regular"

    clusters = range(cluster_count)
    # Define colors and labels for clusters
    if cluster_count < 5:
        colors = ["#e63946", "#a8dadc", "#457b9d", "#1d3557", "#808080"]
        labels = ["C1", "C2", "C3", "C4", "Other"]
    elif cluster_count >= 5:
        colors = ["#001219", "#005f73", "#0a9396", "#94d2bd", "#e9d8a6", "#ee9b00", "#ca6702", "#bb3e03", "#ae2012", "#9b2226", "#808080"]
        labels = ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10", "Other"]

    max_cluster_index = max(cluster_count, final_df["Cluster"].max())
    other_label_added = False

    for cluster in range(max_cluster_index + 1):
        indicesToKeep = final_df["Cluster"] == cluster
        color = colors[cluster] if cluster < len(colors) else "#808080"
        label = labels[cluster] if cluster < len(labels) else "Other"

        if label == "Other" and other_label_added:
            label = None

        plt.scatter(
            final_df.loc[indicesToKeep, "Frame"],
            final_df.loc[indicesToKeep, "RMSD"],
            edgecolors=color,
            s=9,
            facecolors="none",
            label=label
        )

        if label == "Other":
            other_label_added = True

    if cluster_count < 5:
        indicesToKeep = final_df["Frame"] == centroid_frame_ns
        plt.scatter(
            final_df.loc[indicesToKeep, "Frame"],
            final_df.loc[indicesToKeep, "RMSD"],
            facecolors="k",
            marker="+",
            s=290,
            linewidths=2.5,
        )

    plt.rc("axes", linewidth=2.5)
    plt.ylabel(f"{yaxis_title}", fontsize=16, weight="bold")
    plt.xlabel("time (ns)", fontsize=16, weight="bold")
    plt.tick_params(labelsize=14)
    plt.tick_params(which="both", bottom=True, top=True, left=True, right=True)
    plt.tick_params(which="minor", length=5, color="k", width=2.5)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)
    plt.savefig(filename, bbox_inches="tight", dpi=600)


def rmsd_clusters_colorcoder(yaxis_title, cluster_count, layout='wide'):
    # Welcome user and print some instructions
    print("\n.--------------------------.")
    print("| RMSD CLUSTERS COLORCODER |")
    print(".--------------------------.\n")
    print("This script will search your directory for the following output:")
    print("+ CCPTraj RMSD file > rmsd.dat")
    print("+ List of frames assigned clusters > cnumvtime.dat")
    print("+ Root mean square deviation > rmsd.dat\n")

    # Check for required files
    expected_dat = ["rmsd.dat", "cnumvtime.dat", "summary.dat"]

    # Check the users directory for analyzeable files
    for dat in expected_dat:
        data_file = Path(dat)
        if data_file.exists():
            print("Found {}".format(dat))
        else:
            print("No {}".format(dat))
            print("Please add {} to your directory".format(dat))
            exit()

    rmsd_df = dat2df(expected_dat[0])
    clus_df = dat2df(expected_dat[1])
    summary_df = dat2df(expected_dat[2], 0)
    centroid_frame_ns = float(summary_df[5].iloc[0]) / 500

    final_df = pd.concat([rmsd_df, clus_df], axis=1)
    final_df.columns = ["RMSD", "Cluster"]
    final_df["Frame"] = final_df.index
    get_plot(final_df, centroid_frame_ns, yaxis_title, cluster_count, layout)


# Execute the function when run as a script but not if used as a pyQM/MM module
if __name__ == "__main__":
    cluster_count = int(input("How many cluster would you like plotted? "))
    yaxis_title="trajectory 1"
    layout="square"
    rmsd_clusters_colorcoder(yaxis_title, cluster_count, layout)
