import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def format_plot():
    """
    Set general plot formatting parameters for consistent aesthetics.
    Intended for use in the Kulik Lab plotting style.
    """
    font = {"family": "sans-serif", "weight": "bold", "size": 10}
    plt.rc("font", **font)
    plt.rcParams.update({
        "xtick.major.pad": 5,
        "ytick.major.pad": 5,
        "axes.linewidth": 2,
        "xtick.major.size": 7,
        "xtick.major.width": 2,
        "ytick.major.size": 7,
        "ytick.major.width": 2,
        "xtick.minor.size": 4,
        "xtick.minor.width": 2,
        "ytick.minor.size": 4,
        "ytick.minor.width": 2,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.top": True,
        "ytick.right": True,
        "svg.fonttype": "none"
    })

def load_rmsf_csv_files(pattern="*.csv"):
    """
    Load RMSF data from CSV files matching the given pattern.

    Returns:
        list of (str, pd.DataFrame): List of tuples containing filename and corresponding DataFrame.
    """
    files = sorted(glob.glob(pattern))
    data = [(file, pd.read_csv(file)) for file in files]
    return data

def plot_rmsf(dataframes, output_basename="rmsf_plot", colors=None):
    """
    Plot RMSF data from multiple dataframes on the same axes.

    Args:
        dataframes (list): List of (filename, dataframe) tuples.
        output_basename (str): Base name for the saved plots.
        colors (list): Optional list of colors for each plot.
    """
    format_plot()
    fig, ax = plt.subplots(figsize=(6, 4))

    if not colors:
        colors = ["red", "blue", "green", "purple", "orange", "teal"]  # extendable

    for (file, df), color in zip(dataframes, colors):
        label = os.path.splitext(os.path.basename(file))[0]
        ax.plot(df['ResID'], df['Avg. RMSF'], color=color, label=label)
        ax.fill_between(df['ResID'],
                        df['Avg. RMSF'] - df['Avg. Std. Dev'],
                        df['Avg. RMSF'] + df['Avg. Std. Dev'],
                        color=color, alpha=0.1, linewidth=2)

    ax.set_xlabel("residue number", weight="bold", fontsize=12)
    ax.set_ylabel("RMSF (Å)", weight="bold", fontsize=12)
    ax.legend()

    # Use last DataFrame to determine x-axis limits
    last_df = dataframes[-1][1]
    ax.set_xlim(last_df['ResID'].min() - 1, last_df['ResID'].max() + 1)

    ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(2))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(1))

    plt.savefig(f"{output_basename}.svg", bbox_inches="tight")
    plt.savefig(f"{output_basename}.png", bbox_inches="tight", dpi=300)

def main():
    """
    Main execution function to load RMSF CSV files and plot them.
    """
    data = load_rmsf_csv_files()
    if not data:
        print("No CSV files found in the current directory.")
        return
    plot_rmsf(data)

if __name__ == "__main__":
    main()
