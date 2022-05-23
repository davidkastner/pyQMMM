"""Analyze data from hydrogen bonding analysis."""

import pandas as pd
import matplotlib.pyplot as plt

# Create dataframes for hbonding data
taud = pd.DataFrame(
    {
        "His70": [74, 54],
        "Val102": [65, 31],
        "Arg270": [64, 48],
        "Asn95": [25, 39],
        "Phe206": [4, 12],
        "Asp101": [0, 14],
    },
    index=["Acute", "Obtuse"],
).T
vioc = pd.DataFrame(
    {
        "Asp268": [96, 95],
        "Ser158": [85, 0],
        "Leu156": [74, 26],
        "Arg334": [65, 19],
        "Glu170": [0, 28],
        "Asp222": [22, 31],
        "Asp171": [0, 57],
    },
    index=["Acute", "Obtuse"],
).T
besd = pd.DataFrame(
    {
        "Trp231": [49, 35],
        "Arg67": [34, 66],
        "Glu113": [8, 30],
        "Thr214": [6, 5],
        "His127": [5, 87],
        "Trp131": [3, 25],
    },
    index=["Acute", "Obtuse"],
).T
welo5 = pd.DataFrame(
    {
        "Val71": [12, 0],
        "Thr141": [10, 0],
        "Arg143": [1, 1],
        "Ala78": [1, 7],
        "Phe266": [0, 2],
        "Met211": [0, 2],
    },
    index=["Acute", "Obtuse"],
).T
welo5_ax = pd.DataFrame(
    {
        "Ala72": [6, 7],
        "Met211": [1, 1],
        "Phe159": [1, 1],
        "Ile151": [2, 1],
        "Phe266": [0, 2],
    },
    index=["Acute", "Obtuse"],
).T
# Define lists that we can loop over
filenames = ["taud.pdf", "vioc.pdf", "besd.pdf", "welo5.pdf", "welo5_ax.pdf"]
enzymes = [taud, vioc, besd, welo5, welo5_ax]

# Set the lab plot formatting settings


def figure_formatting():
    font = {"family": "sans-serif", "weight": "bold", "size": 18}
    plt.rc("font", **font)
    plt.rcParams['svg.fonttype'] = 'none'
    plt.rcParams["axes.linewidth"] = 2.5
    plt.rcParams["xtick.major.size"] = 10
    plt.rcParams["xtick.major.width"] = 2.5
    plt.rcParams["ytick.major.size"] = 10
    plt.rcParams["ytick.major.width"] = 2.5
    plt.rcParams["xtick.direction"] = "in"
    plt.rcParams["ytick.direction"] = "in"
    plt.rcParams["mathtext.default"] = "regular"
    plt.legend(bbox_to_anchor=(1.05, 1.0), loc="upper left")


# Plot a double barplot
def plot_multi_total_gbsa(hbonds, name):
    figure_formatting()
    new_df = pd.DataFrame(hbonds)
    print(new_df)
    ax = new_df.plot.bar(color=["SkyBlue", "IndianRed"])
    ax.set_ylabel("Percent occurrence", weight="bold")
    ax.set_xlabel("Residue", weight="bold")
    plt.savefig(name, bbox_inches="tight", transparent=True)
    plt.show()


# Run the functions for all the enzymes
for filename, enzyme in zip(filenames, enzymes):
    plot_multi_total_gbsa(enzyme, filename)
