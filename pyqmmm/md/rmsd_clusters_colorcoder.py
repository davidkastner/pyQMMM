import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def dat2df(dat_file, rows_to_skip=1):
    df = pd.read_csv(
        dat_file, sep="\s+", header=None, skiprows=rows_to_skip, index_col=0
    )
    df = df.iloc[1:, :]
    return df

def get_plot(final_df, centroid_time_ns, yaxis_title, cluster_count, layout='wide', show_legend=True):
    # Determine plot size and output filename
    if layout == 'square':
        figsize = (5, 5)
        filename = "clus_rmsd_square.png"
    elif "," in layout:
        try:
            w, h = map(float, layout.split(","))
            figsize = (w, h)
            filename = f"clus_rmsd_{int(w)}x{int(h)}.png"
        except ValueError:
            print("Invalid layout format. Use 'square' or 'width,height' like '5,4'.")
            return
    else:
        figsize = (6, 4)
        filename = "clus_rmsd.png"

    plt.figure(figsize=figsize)

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

    colors = ["#e63946", "#a8dadc", "#457b9d", "#1d3557", "#808080"] if cluster_count < 5 else [
        "#001219", "#005f73", "#0a9396", "#94d2bd", "#e9d8a6", "#ee9b00",
        "#ca6702", "#bb3e03", "#ae2012", "#9b2226", "#808080"
    ]

    max_cluster_index = max(cluster_count, final_df["Cluster"].max())
    other_label_added = False
    use_hollow_circles = final_df.shape[0] > 5000
    circle_size = 18 if not use_hollow_circles else 9

    for cluster in range(max_cluster_index + 1):
        indicesToKeep = final_df["Cluster"] == cluster
        color = colors[cluster] if cluster < len(colors) else "#808080"
        label = f"C{cluster + 1}" if cluster < len(colors) else "Other"
        
        if label == "Other" and other_label_added:
            label = None
        
        plt.scatter(
            final_df.loc[indicesToKeep, "Time_ns"],
            final_df.loc[indicesToKeep, "RMSD"],
            edgecolors=color,
            s=circle_size,
            facecolors="none" if use_hollow_circles else color,
            label=label
        )
        
        if label == "Other":
            other_label_added = True

    if cluster_count < 5:
        indicesToKeep = final_df["Time_ns"] == centroid_time_ns
        plt.scatter(
            final_df.loc[indicesToKeep, "Time_ns"],
            final_df.loc[indicesToKeep, "RMSD"],
            facecolors="k",
            marker="+",
            s=290,
            linewidths=2.5,
        )
    
    plt.ylabel(f"{yaxis_title}", fontsize=16, weight="bold")
    plt.xlabel("time (ns)", fontsize=16, weight="bold")
    plt.tick_params(
        axis='both',
        which='major',
        direction='in',
        length=10,
        width=2.5,
        top=True,
        right=True,
        labelsize=14
    )

    if show_legend:
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)

    plt.savefig(filename, bbox_inches="tight", dpi=600)

def rmsd_clusters_colorcoder(yaxis_title, cluster_count, layout='wide', show_legend=True):
    expected_dat = ["rmsd.dat", "cnumvtime.dat", "summary.dat"]
    for dat in expected_dat:
        data_file = Path(dat)
        if not data_file.exists():
            print(f"Missing required file: {dat}")
            exit()

    total_ns = float(input("Enter total simulation time in nanoseconds: "))
    rmsd_df = dat2df(expected_dat[0])
    clus_df = dat2df(expected_dat[1])
    summary_df = dat2df(expected_dat[2], 0)
    
    num_frames = rmsd_df.shape[0]
    time_per_frame = total_ns / num_frames
    
    centroid_frame = int(summary_df[5].iloc[0])
    centroid_time_ns = centroid_frame * time_per_frame
    
    final_df = pd.concat([rmsd_df, clus_df], axis=1)
    final_df.columns = ["RMSD", "Cluster"]
    final_df["Time_ns"] = final_df.index * time_per_frame
    
    get_plot(final_df, centroid_time_ns, yaxis_title, cluster_count, layout, show_legend)

if __name__ == "__main__":
    cluster_count = int(input("How many clusters would you like plotted? "))
    layout = input("Enter layout (e.g., 'square', '5,4', or press enter for default): ").strip() or "wide"
    legend_input = input("Show legend? (y/n): ").strip().lower()
    show_legend = legend_input != 'n'
    rmsd_clusters_colorcoder("trajectory 1", cluster_count, layout, show_legend)
