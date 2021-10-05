'''
Docs: https://github.com/davidkastner/hyscore-plotter/blob/main/README.md
DESCRIPTION
   Creates a series of KDE plots based on HYSCORE-guided simulations.
   Author: David Kastner
   Massachusetts Institute of Technology
   kastner (at) mit . edu
SEE ALSO
    N/A
'''
################################ DEPENDENCIES ##################################
import numpy as np
import time
import glob
import sys
import os.path
import configparser as cp
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.ticker as ticker
import matplotlib.colors as mplc
import matplotlib.cm as cm
from scipy.stats import gaussian_kde
from matplotlib.patches import Rectangle
################################## FUNCTIONS ###################################
'''
Parses the config file for the users parameters
Parameters
----------

Returns
-------
labels : dictionary
    Contains labels section where the key is the name and the values is itself
plot_params : list
    A list of dictionaries where the index is the plot number and 
    the values are the associated floats from the config file
'''


def config():
    # Check if the user has provided a config file
    if os.path.isfile('./1_in/config'):
        print('Parameters obtained from config file.')
    else:
        print('Could not find config file.')
        sys.exit()
    # Parse the labels and plot sections of the config file
    labels = {}
    plot_params = []
    config = cp.ConfigParser()
    config.read('./1_in/config')
    for section in config.sections():
        if section == "Labels":
            for key, value in config.items(section):
                labels[key] = value;
        else:
            plot_dict = {}
            for key, _ in config.items(section):
                if key == 'size_group':
                    plot_dict[key] = config.getint(section, key)
                else:
                    plot_dict[key] = config.getfloat(section, key)
            plot_params.append(plot_dict)
    return labels, plot_params


'''
Combines a CPPTraj output file with angles and another with distances.
Parameters
----------
N/A
Returns
-------
combined : file
    Generates a file with the combined distances and angles for each plot.
file_array : list
    List of all the files that are generated.
'''


def combine_inp():
    # Determine the number of plots the user wants based on angle and dist files
    num_ang = glob.glob('./1_in/*_angles.dat')
    num_dist = glob.glob('./1_in/*_distances.dat')
    num_plots = len(num_ang)
    # Check if there is a distance file for every angle file
    if num_plots != len(num_dist):
        print('The number of distance and angle files is not the same.')
        sys.exit()
    # Combine the dist and angle files into a single file
    file_array = []
    for num in range(1,num_plots+1):
        file_array.append('./2_temp/{}_combined.dat'.format(num))
        with open('./2_temp/{}_combined.dat'.format(num), 'w') as combined:
            with open('./1_in/{}_angles.dat'.format(num), 'r') as ang_file:
                with open('./1_in/{}_distances.dat'.format(num), 'r') as dist_file:
                    for ang_line, dist_line in zip(ang_file, dist_file):
                        if "#" in ang_line:
                            continue
                        angle = ang_line.split()[1]
                        dist = dist_line.split()[1]
                        combined.write('{} {}\n'.format(dist, angle))

    return file_array


'''
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
'''


def get_xy_data(filename):
    # Open a file and loop through it splitting by white space
    with open(filename, 'r') as file:
        x = []
        y = []
        for line in file:
            dist, ang = line.split(' ')
            x.append(dist)
            y.append(ang)
        # Convert the compiled lists into a numpy array
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)

        return x, y


'''
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
'''


def collect_xyz_data(filenames):
    # Collect data
    print('Starting data collection.')
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


'''
Checks all the data sets and decides what the x and y bounds should be.
Parameters
----------
x_data : list
    A list of lists with the x data for each plot as a list within the list
y_data : list
    A list of lists with the y data for each plot as a list within the list
patch_param : list
    The dimensions of the patch as min and max for the the height and width
Returns
-------
xlim : list
    The lowest and highest values on the x-axis
ylim : list
    The lowest and highest values on the y-axis
'''


def compare_patch_limits(x_data, y_data, patch_params):
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

'''
Description.
Parameters
----------

Returns
-------
hyscore_kde.png : PNG
    A PNG depicting the KDE analysis at 300 dpi.
'''

def get_plot_limits(x_data, y_data, plot_params):
    # size group extremes
    group_curr_max_min = {}
    xlims = []
    ylims = []
    for i in range(len(x_data)):
        # Set the max and min values of the current plot as variables
        height_min = plot_params[i]['height_min']
        height_max = plot_params[i]['height_max']
        width_min = plot_params[i]['width_min']
        width_max = plot_params[i]['width_max']
        size_group = plot_params[i]['size_group']
        patch_params = [height_min, height_max, width_min, width_max]

        # Get the min and max values for the axis
        xlim, ylim = compare_patch_limits(x_data[i], y_data[i], patch_params)

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
            group_curr_max_min[size_group] = [xlim,ylim]
        xlims.append(xlim)
        ylims.append(ylim)
    return xlims, ylims


'''
Description.
Parameters
----------

Returns
-------
hyscore_kde.png : PNG
    A PNG depicting the KDE analysis at 300 dpi.
'''


def graph_datasets(x_data, y_data, z_data, labels, plot_params, show_crosshairs):
    cmap = mpl.cm.Blues(np.linspace(0, 1, 20))
    cmap = mpl.colors.ListedColormap(cmap[5:, :-1])
    
    # Lab styling graph properties
    font = {'family': 'sans-serif', 'weight': 'bold', 'size': 18}
    plt.rc('font', **font)
    plt.rcParams['axes.linewidth'] = 2.5
    plt.rcParams['xtick.major.size'] = 10
    plt.rcParams['xtick.major.width'] = 2.5
    plt.rcParams['ytick.major.size'] = 10
    plt.rcParams['ytick.major.width'] = 2.5
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.rcParams['mathtext.default'] = 'regular'
    
    # Plot subfigures
    fig, ax = plt.subplots(1, len(x_data), sharey=True, figsize=(len(x_data)*4,4))
    fig.subplots_adjust(wspace=0)
    fig.colorbar(cm.ScalarMappable(norm=None, cmap=cmap))
    
    # Titles and axes titles
    fig.text(0.5, -0.03, labels['xlabel'], ha='center')
    plt.ylabel(labels['ylabel'], fontweight='bold')

    # Get x and y limits
    xlims, ylims = get_plot_limits(x_data,y_data,plot_params)

    # Loop through the the data associated with each plot
    for i in range(len(x_data)):

        # Set the max and min values of the current plot as variables
        height_min = plot_params[i]['height_min']
        height_max = plot_params[i]['height_max']
        width_min = plot_params[i]['width_min']
        width_max = plot_params[i]['width_max']

        # Get xlim and ylim
        xlim = xlims[i]
        ylim = ylims[i]

        # Create a scatter plot
        axes = ax[i] if len(x_data) > 1 else ax
        axes.scatter(x_data[i], y_data[i], c=z_data[i], s=40, vmin=0, vmax=0.30, cmap=cmap)
        axes.set_autoscale_on(False)
        axes.set_xlim(xlim)
        axes.set_ylim(ylim)

        if show_crosshairs:
            # Calculate the dimensions for the patch and define patch
            anchor = (width_min, height_min)
            width = width_max - width_min
            height = height_max - height_min
            axes.add_patch(Rectangle(anchor, width, height, fill=False, color="k",
                            linestyle='--', linewidth=2.0, joinstyle='miter'))
            
            # Define where to place the crosshairs of the patch
            width_avg = np.average([width_max, width_min])
            height_avg = np.average([height_max, height_min])
            axes.plot((width_min, width_max),
                       (height_avg, height_avg), color='k', linewidth=2.0)
            axes.plot((width_avg, width_avg),
                       (height_min, height_max), color='k', linewidth=2.0)

        # Set the ticks as the y and x limits
        xlim_min, xlim_max = xlim
        interval = ((xlim_max - xlim_min) / 3.6)
        xticks = np.arange(xlim_min, xlim_max + .1, interval)
        axes.xaxis.set_ticks(xticks)
        axes.xaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
        axes.tick_params(which='both', bottom=True, top=True, left=True,
                          right=False)
        axes.tick_params(which='minor', length=5, color='k', width=2.5)

    plt.savefig('./3_out/hyscore_kde.png', bbox_inches='tight', dpi=300)


############################## HYSCORE PLOTTER #################################
# Introduce user to HyScore Eval functionality
def restraint_plots():
    print('\n--------------------------')
    print('WELCOME TO HYSCORE PLOTTER')
    print('--------------------------\n')
    print('Generates a series of KDE plots for hyscore-guided simulations.')
    print('This the goal of HYSCORE PLOTTER is to:')
    print('+ Vizualize a simulation against two order parameters')
    print('+ Compare the results to the experimentally expected values')
    print('------------------------\n')

    show_crosshairs = input('Would you like crosshairs (y/n)?  ') == 'y'

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
