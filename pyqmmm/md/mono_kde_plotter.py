"""Function for generating combined KDE plot"""

import numpy as np
import glob
import sys
import os.path
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
import matplotlib.font_manager

matplotlib.rcParams["pdf.fonttype"] = "42"
matplotlib.rcParams["ps.fonttype"] = "42"


def config():
    """
    Parses the config file for the users parameters.

    Returns
    -------
    labels : dictionary
        Contains labels section where the key is the name and the values is itself.
    plot_params : list
        A list of dictionaries where the index is the plot number and the values are the associated floats from the config file
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
            for key, value in config.items(section):
                labels[key] = value
        else:
            plot_dict = {}
            for key, _ in config.items(section):
                if key == "size_group":
                    plot_dict[key] = config.getint(section, key)
                if key == "color":
                    plot_dict[key] = config.get(section, key)
                else:
                    plot_dict[key] = config.getfloat(section, key)
            plot_params.append(plot_dict)
    return labels, plot_params


def combine_inp():
    """
    Combines a CPPTraj output file with angles and another with distances.

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
        file_array.append("./2_temp/{}_combined.dat".format(num))
        with open("./2_temp/{}_combined.dat".format(num), "w") as combined:
            with open("./1_in/{}_angles.dat".format(num), "r") as ang_file:
                with open("./1_in/{}_distances.dat".format(num), "r") as dist_file:
                    for ang_line, dist_line in zip(ang_file, dist_file):
                        if "#" in ang_line:
                            continue
                        angle = ang_line.split()[1]
                        dist = dist_line.split()[1]
                        combined.write("{} {}\n".format(dist, angle))

    return file_array


def get_xy_data(filename):
    """
    Takes a combined files and destructures it into arrays.

    Parameters
    ----------
    filename : str
        The name of the file.

    Returns
    -------
    x : array
        The x-values most likely a list of distances.
    y : array
        The y-values most likely a list of angles.
    """

    # Open a file and loop through it splitting by white space
    with open(filename, "r") as file:
        x = []
        y = []
        for line in file:
            dist, ang = line.split(" ")
            x.append(dist)
            y.append(ang)
        # Convert the compiled lists into a numpy array
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)

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
        A list of values in the x dimension.
    y_data : array
        A list of values in the y dimension.
    z_data : array
        A list of values in the z dimension.
    """

    # Collect data
    print("Starting data collection.")
    x_data = []
    y_data = []
    z_data = []
    for filename in filenames:
        # Unpack the x and y values from the combined file
        x, y = get_xy_data(filename)
        # Makes a color 2D scatter and class calculate the point density
        xy_matrix = np.vstack([x, y])
        # Evaluate the estimated pdf for xy_matrix
        z = gaussian_kde(xy_matrix)(xy_matrix)
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
        A list of lists with the x data for each plot as a list within the list.
    y_data : list
        A list of lists with the y data for each plot as a list within the list.
    patch_param : list
        The dimensions of the patch as min and max for the the height and width.

    Returns
    -------
    xlim : list
        The lowest and highest values on the x-axis.
    ylim : list
        The lowest and highest values on the y-axis.
    """

    # Unpack the dimensions of the patch
    height_min, height_max, width_min, width_max = patch_params
    # Identify max and min values from x and y data sets
    x_max = max(x_data)
    x_min = min(x_data)
    y_max = max(y_data)
    y_min = min(y_data)
    # Check if the dataset limits are more extreme than the patch limits
    xlim_min = x_min if x_min < width_min else width_min
    xlim_max = x_max if x_max > width_max else width_max
    ylim_min = y_min if y_min < height_min else height_min
    ylim_max = y_max if y_max > height_max else height_max
    # Calculate the padding around the data as one seventh the spread
    y_pad = (ylim_max - ylim_min) / 7
    x_pad = (xlim_max - xlim_min) / 7
    # Add the padding to the min and max values
    xlim_min -= x_pad
    xlim_max += x_pad
    ylim_min -= y_pad
    ylim_max += y_pad
    # Define the x and y limits as arrays
    xlim = [xlim_min, xlim_max]
    ylim = [ylim_min, ylim_max]

    return xlim, ylim


def get_plot_limits(x_data, y_data, plot_params):
    """
    Calculate the x and y limits for the plot.

    Returns
    -------
    hyscore_kde.png : PNG
        A PNG depicting the KDE analysis at 300 dpi.
    """
    # size group extremes
    group_curr_max_min = {}
    size_group_list = []
    xlims = []
    ylims = []
    for i in range(len(x_data)):
        # Set the max and min values of the current plot as variables
        height_min = plot_params[i]["height_min"]
        height_max = plot_params[i]["height_max"]
        width_min = plot_params[i]["width_min"]
        width_max = plot_params[i]["width_max"]
        size_group = plot_params[i]["size_group"]
        patch_params = [height_min, height_max, width_min, width_max]

        # Save the size groups in the order that they come up as reference
        size_group_list.append(size_group)

        # Get the min and max values for the axis
        xlim, ylim = compare_patch_limits(x_data[i], y_data[i], patch_params)

        # Set the size group so panels indicated in the config file match
        if size_group not in group_curr_max_min:
            group_curr_max_min[size_group] = [xlim, ylim]
        else:
            xlim_min, xlim_max = xlim
            ylim_min, ylim_max = ylim
            group_xlim, group_ylim = group_curr_max_min[size_group]
            group_xlim_min, group_xlim_max = group_xlim
            group_ylim_min, group_ylim_max = group_ylim
            # Check if the dataset limits are more extreme than the group limits
            xlim_min = xlim_min if xlim_min < group_xlim_min else group_xlim_min
            xlim_max = xlim_max if xlim_max > group_xlim_max else group_xlim_max
            ylim_min = ylim_min if ylim_min < group_ylim_min else group_ylim_min
            ylim_max = ylim_max if ylim_max > group_ylim_max else group_ylim_max
            # set new mins and maxes
            xlim = [xlim_min, xlim_max]
            ylim = [ylim_min, ylim_max]
            group_curr_max_min[size_group] = [xlim, ylim]

    # We have the max and min for each size group and can now return them
    for size in size_group_list:
        [xlim, ylim] = group_curr_max_min[size]
        xlims.append(xlim)
        ylims.append(ylim)

    return xlims, ylims


def graph_datasets(x_data, y_data, z_data, labels, plot_params, show_crosshairs):
    """
    Generate the plot.

    Returns
    -------
    hyscore_kde.png : PNG
        A PNG depicting the KDE analysis at 300 dpi.
    """

    # Lab styling graph properties
    # Font properties
    font = {"family": "sans-serif", "weight": "bold", "size": 18}
    plt.rc("font", **font)
    plt.rcParams["svg.fonttype"] = "none"
    # Tick properties
    plt.rcParams["axes.linewidth"] = 2.5
    plt.rcParams["xtick.major.size"] = 10
    plt.rcParams["xtick.major.width"] = 2.5
    plt.rcParams["ytick.major.size"] = 10
    plt.rcParams["ytick.major.width"] = 2.5
    plt.rcParams["xtick.direction"] = "in"
    plt.rcParams["ytick.direction"] = "in"
    plt.rcParams["mathtext.default"] = "regular"

    # Plot subfigures
    fig, ax = plt.subplots()

    # Titles and axes titles
    fig.text(0.5, -0.03, labels["xlabel"], ha="center")
    # The y-axis title must be set manually until version 3.4
    plt.ylabel(labels["ylabel"], fontweight="bold")

    # Get x and y limits
    xlims, ylims = get_plot_limits(x_data, y_data, plot_params)

    # Y-axis is the same so we set it before entering the Loop
    ymax = max([i for lis in ylims for i in lis])
    ymin = min([i for lis in ylims for i in lis])
    ymax_spread = [ymin, ymax]

    # Loop through the the data associated with each plot
    for i in range(len(x_data)):

        # Parse the config dictionary for the color of each plot
        color = plot_params[i]["color"]
        if color == "blue":
            cmap = mpl.cm.Blues(np.linspace(0, 1, 20))
            cmap = mpl.colors.ListedColormap(cmap[5:, :-1])
            # cmap = LinearSegmentedColormap.from_list('my_gradient', (
            # # Edit this gradient at https://eltos.github.io/gradient/#C5F4FF-0000FF-00008B
            #     (0.000, (0.773, 0.957, 1.000)),
            #     (0.500, (0.000, 0.000, 1.000)),
            #     (1.000, (0.000, 0.000, 0.545))), N=20)
        elif color == "orange":
            cmap = mpl.cm.Oranges(np.linspace(0, 1, 20))
            cmap = mpl.colors.ListedColormap(cmap[5:, :-1])
        elif color == "red":
            cmap = mpl.cm.Reds(np.linspace(0, 1, 20))
            cmap = mpl.colors.ListedColormap(cmap[5:, :-1])
            # cmap = LinearSegmentedColormap.from_list('my_gradient', (
            #     # Edit this gradient at https://eltos.github.io/gradient/#FFCACA-FF0000-590000
            #     (0.000, (1.000, 0.800, 0.796)),
            #     (0.500, (1.000, 0.000, 0.000)),
            #     (1.000, (0.545, 0.000, 0.000))), N=15)
        elif color == "grey":
            cmap = mpl.cm.Greys(np.linspace(0, 1, 20))
            cmap = mpl.colors.ListedColormap(cmap[5:, :-1])
        elif color == "green":
            cmap = mpl.cm.Greens(np.linspace(0, 1, 20))
            cmap = mpl.colors.ListedColormap(cmap[5:, :-1])
        # cmap = mpl.colors.ListedColormap(cmap[5:, :-1])

        # Set the max and min values of the current plot as variables
        height_min = plot_params[i]["height_min"]
        height_max = plot_params[i]["height_max"]
        width_min = plot_params[i]["width_min"]
        width_max = plot_params[i]["width_max"]

        # Get xlim and ylim
        xlim = xlims[i]
        # ylim = ylims[i]

        # Create a scatter plot
        ax.scatter(
            x_data[i], y_data[i], c=z_data[i], s=40, vmin=0.0, vmax=0.3, cmap=cmap
        )

        if show_crosshairs:
            # Calculate the dimensions for the patch and define patch
            anchor = (width_min, height_min)
            width = width_max - width_min
            height = height_max - height_min
            ax.add_patch(
                Rectangle(
                    anchor,
                    width,
                    height,
                    fill=False,
                    color="k",
                    linestyle="--",
                    linewidth=2.0,
                    joinstyle="miter",
                )
            )

            # Define where to place the crosshairs of the patch
            width_avg = np.average([width_max, width_min])
            height_avg = np.average([height_max, height_min])
            ax.plot(
                (width_min, width_max),
                (height_avg, height_avg),
                color="k",
                linewidth=2.0,
            )
            ax.plot(
                (width_avg, width_avg),
                (height_min, height_max),
                color="k",
                linewidth=2.0,
            )

        # Set x-axis tick options
        xlim_min, xlim_max = xlim
        xlim_min = 2.8
        xlim_max = 5.0
        major_xticks = np.arange(xlim_min + 0.2, xlim_max, 0.5)
        minor_xticks = np.arange(xlim_min, xlim_max, 0.1)
        ax.xaxis.set_ticks(major_xticks)
        ax.xaxis.set_ticks(minor_xticks, minor=True)
        ax.set_xlim(2.8, 5)

        # Set y-axis tick options
        major_yticks = np.arange(20, 121, 20)
        minor_yticks = np.arange(10, 126, 10)
        ax.yaxis.set_ticks(major_yticks)
        ax.yaxis.set_ticks(minor_yticks, minor=True)
        ax.set_ylim(10, 125)

        ax.tick_params(which="both", bottom=True, top=True, left=True, right=True)
        ax.tick_params(which="minor", length=5, color="k", width=2.5)

    plt.savefig(
        "./3_out/restraints_kde.png", dpi=600, bbox_inches="tight", transparent=True
    )
    # plt.savefig("./3_out/restraints_kde.svg", bbox_inches="tight", format="svg")


def restraint_plots():
    # Introduce user to HyScore Eval functionality
    print("\n.------------------.")
    print("| MONO KDE PLOTTER |")
    print(".------------------.\n")
    print("Generates a single KDE plot for hyscore-guided simulations:")
    print("+ Vizualize a simulation against two order parameters.")
    print("+ Compare the results to the experimentally expected values.")
    print("+ Tick settings in graph_datasets need to be updated manually")
    print("\n")

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
