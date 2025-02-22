"""Creates a series of KDE plots based on HYSCORE-guided simulations"""

import os.path
import numpy as np
import glob
import sys
import configparser as cp
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.cm as cm
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import MultipleLocator
import matplotlib.ticker as ticker
import matplotlib.colors as mplc
from scipy.stats import gaussian_kde
from matplotlib.patches import Rectangle
from matplotlib.font_manager import FontProperties
from matplotlib import rc, rcParams

mpl.rcParams["pdf.fonttype"] = "42"
mpl.rcParams["ps.fonttype"] = "42"


def config():
    """
    Parses the config file for the users parameters.

    Returns
    -------
    labels : dictionary
        Contains labels section where the key is the name and the values is itself
    plot_params : list
        A list of dictionaries where the index is the plot number and
        the values are the associated floats from the config file

    """
    # Check if the user has provided a config file
    if os.path.isfile("./1_in/config"):
        print("Parameters obtained from config file.")
    else:
        print("Could not find config file.")
        sys.exit()

    # Parse the labels and plot sections of the config file
    labels = {}
    plot_params = []
    config = cp.ConfigParser()
    config.read("./1_in/config")
    for section in config.sections():
        if section == "Labels":
            labels.update(config.items(section))
        else:
            plot_dict = {
                key: config.getint(section, key)
                if key == "size_group"
                else config.get(section, key)
                if key == "color"
                else config.getfloat(section, key)
                for key, _ in config.items(section)
            }
            plot_params.append(plot_dict)
    return labels, plot_params


def combine_inp():
    """
    Combines a CPPTRAJ output file with angles and another with distances.

    Returns
    -------
    combined : file
        Generates a file with the combined distances and angles for each plot.
    file_array : list
        List of all the files that are generated.

    """
    # Determine the number of plots the user wants based on angle and dist files
    num_ang = glob.glob("./1_in/*_angles.dat")
    num_dist = glob.glob("./1_in/*_distances.dat")
    num_plots = len(num_ang)

    # Check if there is a distance file for every angle file
    if num_plots != len(num_dist):
        print("The number of distance and angle files is not the same.")
        sys.exit()

    # Combine the dist and angle files into a single file
    file_array = []
    for num in range(1, num_plots + 1):
        combined_file_path = f"./2_temp/{num}_combined.dat"
        file_array.append(combined_file_path)

        with open(combined_file_path, "w") as combined, open(
            f"./1_in/{num}_angles.dat", "r"
        ) as ang_file, open(f"./1_in/{num}_distances.dat", "r") as dist_file:
            for ang_line, dist_line in zip(ang_file, dist_file):
                if "#" in ang_line:
                    continue

                angle = ang_line.split()[1]
                dist = dist_line.split()[1]
                combined.write(f"{dist} {angle}\n")

    return file_array


def get_xy_data(filename):
    """
    Takes a combined file and destructures it into arrays.

    Parameters
    ----------
    filename : str
        The name of the file.

    Returns
    -------
    x : array
        The x-values, most likely a list of distances.
    y : array
        The y-values, most likely a list of angles.

    """
    # Read data from file and split by white space
    with open(filename, "r") as file:
        data = np.loadtxt(file)

    # Separate x and y values
    x = data[:, 0]
    y = data[:, 1]

    return x, y


def collect_xyz_data(filenames):
    """
    Retrieves the x and y data from the files.

    Parameters
    ----------
    filenames : list
        List of the combined file names that were generated.

    Returns
    -------
    x_data : array
        A list of values in the x dimension
    y_data : array
        A list of values in the y dimension
    z_data : array
        A list of values in the z dimension

    """
    # Collect data
    print("Starting data collection.")
    x_data = []
    y_data = []
    z_data = []

    for filename in filenames:
        # Unpack the x and y values from the combined file
        x, y = get_xy_data(filename)

        # Calculate the point density using Gaussian kernel density estimation
        xy_matrix = np.vstack([x, y])
        z = gaussian_kde(xy_matrix)(xy_matrix)

        # Sort x, y, and z arrays by z values
        index = z.argsort()
        x_data.append(x[index])
        y_data.append(y[index])
        z_data.append(z[index])

    return x_data, y_data, z_data


def compare_patch_limits(x_data, y_data, patch_params):
    """
    Checks all the data sets and decides what the x and y bounds should be.

    Parameters
    ----------
    x_data : list
        A list of lists with the x data for each plot as a list within the list
    y_data : list
        A list of lists with the y data for each plot as a list within the list
    patch_params : list
        The dimensions of the patch as min and max for the height and width

    Returns
    -------
    xlim : list
        The lowest and highest values on the x-axis
    ylim : list
        The lowest and highest values on the y-axis

    """
    # Unpack the dimensions of the patch
    height_min, height_max, width_min, width_max = patch_params

    # Identify max and min values from x and y data sets
    x_min, x_max = np.min(x_data), np.max(x_data)
    y_min, y_max = np.min(y_data), np.max(y_data)

    # Check if the dataset limits are more extreme than the patch limits
    xlim = [min(x_min, width_min), max(x_max, width_max)]
    ylim = [min(y_min, height_min), max(y_max, height_max)]

    # Calculate the padding around the data as one-seventh the spread
    x_pad, y_pad = (xlim[1] - xlim[0]) / 7, (ylim[1] - ylim[0]) / 7

    # Add the padding to the min and max values
    xlim = [xlim[0] - x_pad, xlim[1] + x_pad]
    ylim = [ylim[0] - y_pad, ylim[1] + y_pad]

    return xlim, ylim


def get_plot_limits(x_data, y_data, plot_params):
    group_curr_max_min = {}
    size_group_list = []

    for i, (x, y) in enumerate(zip(x_data, y_data)):
        patch_params = [
            plot_params[i][key]
            for key in ["height_min", "height_max", "width_min", "width_max"]
        ]
        size_group = plot_params[i]["size_group"]
        size_group_list.append(size_group)

        xlim, ylim = compare_patch_limits(x, y, patch_params)

        if size_group not in group_curr_max_min:
            group_curr_max_min[size_group] = [xlim, ylim]
        else:
            group_xlim, group_ylim = group_curr_max_min[size_group]
            group_curr_max_min[size_group] = [
                [min(xlim[0], group_xlim[0]), max(xlim[1], group_xlim[1])],
                [min(ylim[0], group_ylim[0]), max(ylim[1], group_ylim[1])],
            ]

    xlims, ylims = zip(*[group_curr_max_min[size] for size in size_group_list])

    return xlims, ylims


def graph_datasets(x_data, y_data, z_data, labels, plot_params, show_crosshairs):
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.weight": "bold",
            "font.size": 18,
            "svg.fonttype": "none",
            "axes.linewidth": 2.5,
            "xtick.major.size": 10,
            "xtick.major.width": 2.5,
            "ytick.major.size": 10,
            "ytick.major.width": 2.5,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "mathtext.default": "regular",
        }
    )

    color_map = {
        "blue": mpl.cm.Blues(np.linspace(0, 1, 20)),
        "orange": mpl.cm.Oranges(np.linspace(0, 1, 20)),
        "red": mpl.cm.Reds(np.linspace(0, 1, 20)),
        "grey": mpl.cm.Greys(np.linspace(0, 1, 20)),
        "green": mpl.cm.Greens(np.linspace(0, 1, 20)),
    }
    fig, ax = plt.subplots()
    fig.text(0.5, -0.03, labels["xlabel"], ha="center")
    plt.ylabel(labels["ylabel"], fontweight="bold")
    xlims, ylims = get_plot_limits(x_data, y_data, plot_params)

    for i, (x, y, z) in enumerate(zip(x_data, y_data, z_data)):
        cmap = mpl.colors.ListedColormap(color_map[plot_params[i]["color"]][5:, :-1])
        ax.scatter(x, y, c=z, s=40, vmin=0.0, vmax=0.3, cmap=cmap)

        if show_crosshairs:
            height_min, height_max, width_min, width_max = [
                plot_params[i][key]
                for key in ["height_min", "height_max", "width_min", "width_max"]
            ]
            anchor, width, height = (
                (width_min, height_min),
                width_max - width_min,
                height_max - height_min,
            )
            ax.add_patch(
                Rectangle(
                    anchor,
                    width,
                    height,
                    fill=False,
                    color="k",
                    linestyle="--",
                    linewidth=2.0,
                )
            )
            ax.plot(
                (width_min, width_max),
                (np.mean([height_min, height_max]),) * 2,
                color="k",
                linewidth=2.0,
            )
            ax.plot(
                (np.mean([width_min, width_max]),) * 2,
                (height_min, height_max),
                color="k",
                linewidth=2.0,
            )

        ax.set_xlim(2.8, 5)
        ax.set_ylim(10, 125)
        ax.xaxis.set_ticks(np.arange(3, 5, 0.5))
        ax.xaxis.set_ticks(np.arange(2.8, 5, 0.1), minor=True)
        ax.yaxis.set_ticks(np.arange(20, 121, 20))
        ax.yaxis.set_ticks(np.arange(10, 126, 10), minor=True)
        ax.tick_params(which="both", bottom=True, top=True, left=True, right=True)
        ax.tick_params(which="minor", length=5, color="k", width=2.5)

    plt.savefig(
        "./3_out/restraints_kde.png", dpi=600, bbox_inches="tight", transparent=True
    )


def restraint_plots():
    print("\n.--------------------------.")
    print("|WELCOME TO RESTRAINT PLOTS|")
    print(".--------------------------.\n")
    print("Generates a series of KDE plots for hyscore-guided simulations.")
    print("This the goal of RESTRAINT PLOTS is to:")
    print("+ Vizualize a simulation against two order parameters.")
    print("+ Compare the results to the experimentally expected values.")
    print("+ An example config file can be found in CADDKit/tutorials/restraint_plotter.\n")

    # Uncomment the following line if you want to ask the user for input.
    # show_crosshairs = input('Would you like crosshairs (y/n)?  ') == 'y'
    show_crosshairs = "n"

    # Get filenames from output directory
    filenames = combine_inp()

    # Get coordinates from config file
    labels, plot_params = config()

    # Execute the main functions and generate plot
    x_data, y_data, z_data = collect_xyz_data(filenames)
    graph_datasets(x_data, y_data, z_data, labels, plot_params, show_crosshairs)


# Execute the Quick CSA when run as a script but not if used as a pyQM/MM module
if __name__ == "__main__":
    restraint_plots()
