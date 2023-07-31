import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def format_plot():
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
    plt.rcParams["xtick.minor.size"] = 4  # Set minor tick size
    plt.rcParams["xtick.minor.width"] = 2  # Set minor tick width
    plt.rcParams["ytick.minor.size"] = 4  # Set minor tick size
    plt.rcParams["ytick.minor.width"] = 2  # Set minor tick width
    plt.rcParams["xtick.direction"] = "in"
    plt.rcParams["ytick.direction"] = "in"
    plt.rcParams["xtick.top"] = True
    plt.rcParams["ytick.right"] = True
    plt.rcParams["svg.fonttype"] = "none"

# Create a new figure with square dimensions
format_plot()
fig, ax = plt.subplots(figsize=(6,4))

# Define the colors for the plots
colors = ["red", "blue", "green"]

# Get all .csv files in the current directory
files = glob.glob("*.csv")

for file, color in zip(files, colors):
    # Load the data
    rmsf_df = pd.read_csv(file)

    # Plot the average RMSF
    ax.plot(rmsf_df['ResID'], rmsf_df['Avg. RMSF'], color=color, label=os.path.splitext(file)[0])

    # Plot the standard deviation as a transparent range for the background
    ax.fill_between(rmsf_df['ResID'], rmsf_df['Avg. RMSF'] - rmsf_df['Avg. Std. Dev'],
                 rmsf_df['Avg. RMSF'] + rmsf_df['Avg. Std. Dev'], color=color, alpha=0.1, linewidth=2,)

# Add labels and a legend in bold
ax.set_xlabel('residue number', weight="bold", fontsize=12)
ax.set_ylabel('RMSF (Å)', weight="bold", fontsize=12)
ax.legend()

# Adjust the x-axis limits for equal whitespace around the plot
ax.set_xlim(rmsf_df['ResID'].min() - 1, rmsf_df['ResID'].max() + 1)

# Set major and minor ticks for the x-axis
ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))

# Set major and minor ticks for the y-axis
ax.yaxis.set_major_locator(ticker.MultipleLocator(2))
ax.yaxis.set_minor_locator(ticker.MultipleLocator(1))

# Save the plot to a file
plt.savefig("rmsf_plot.svg", bbox_inches="tight")
plt.savefig("rmsf_plot.png", bbox_inches="tight", dpi=300)