'''
Docs: https://github.com/davidkastner/hyscore-plotter/blob/main/README.md
DESCRIPTION
   Creates a series of KDE plots based on HYSCORE-guided simulations.
   Author: David Kastner and Rimsha Mehmood
   Massachusetts Institute of Technology
   kastner (at) mit . edu
SEE ALSO
    N/A
'''
################################ DEPENDENCIES ################################## 
import numpy as np
import glob
import sys
import configparser
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from matplotlib.patches import Rectangle
import matplotlib.colors as mplc
import matplotlib.cm as cm
import matplotlib.ticker as ticker
from matplotlib.ticker import AutoMinorLocator
################################## FUNCTIONS ################################### 
'''
Combines a CPP Traj output file with angles and another with distances.
The first column is the distance and the second is the angle.
They are separated by a space.
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
    #Determine the number of plots the user wants based on angle and dist files
    num_ang = glob.glob('./1_input/angle*')
    num_dist = glob.glob('./1_input/angle*')
    num_plots = len(num_ang)
    #Check if there is a distance file for every angle file
    if num_plots != len(num_dist)
        print('The number of distance and angle files is not the same.')
        sys.exit()
    #Combine the dist and angle files into a single file
    file_array = []
    for num in num_plots:
        file_array.append('./2_interm/combined_{}.dat'.format(num))
        with open('./2_interm/combined_{}.dat'.format(num),'w') as combined:
            with open('./1_input/angle_{}.dat'.format(num),'r') as ang_file:
                with open('./1_input/dist_{}.dat'.format(num),'r') as dist_file:
                    for ang_line, dist_line in zip(ang_file, dist_file):
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
    #Open a file and loop through it splitting by white space
    with open(filename, 'r') as file:
        x = []
        y = []
        for line in file:
            dist, ang = line.split(' ')	
            x.append(dist)
            y.append(ang)
        #Convert the compiled lists into a numpy array
        x = np.asarray(x, dtype = float)
        y = np.asarray(y, dtype = float)
        
        return x, y

'''
Description.
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
    #Collect data
    x_data = []
    y_data = []
    z_data = []
    for filename in filenames:
        #Unpack the x and y values from the combined file
        x, y = get_xy_data(filename)
        #Makes a color 2D scatter and class calculate the point density
        xy_matrix = np.vstack([x, y])
        #Evaluate the estimated pdf for xy_matrix
        z = gaussian_kde(xy_matrix)(xy_matrix)
        index = z.argsort()
        x_data.append(x[index])
        y_data.append(y[index])
        z_data.append(z[index])
        
    return x_data, y_data, z_data
            
'''
Description.
Parameters
----------
    
Returns
-------
hyscore_kde.png : PNG
    A PNG depicting the KDE analysis at 300 dpi.
'''
def graph_datasets(x_data, y_data, z_data):
    cmap = mpl.cm.Oranges(np.linspace(0,1,20))
    cmap = mpl.colors.ListedColormap(cmap[5:,:-1])
    # Graph properties
    font = {'family':'sans-serif', 'weight':'bold', 'size' : 18}
    plt.rc('font', **font)
    plt.rcParams['axes.linewidth'] = 2.5
    plt.rcParams['xtick.major.size'] = 10
    plt.rcParams['xtick.major.width'] = 2.5
    plt.rcParams['ytick.major.size'] = 10
    plt.rcParams['ytick.major.width'] = 2.5
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.rcParams['mathtext.default'] = 'regular'

    #Plot
    fig, ax = plt.subplots(1, 3, sharey=True, figsize=(12, 4))
    fig.subplots_adjust(wspace=0)
    fig.colorbar(cm.ScalarMappable(norm=None, cmap=cmap))
    
    #Titles and axes titles
    ax[1].set_xlabel("Fe-H distance ($\AA$)", fontweight='bold')
    ax[0].set_ylabel("H-Fe-O angle ($^{o}$)", fontweight='bold')

    for i in range(len(x_data)):
        ax[i].scatter(x_data[i], y_data[i], c=z_data[i], s=40, vmin=0, vmax=0.30, 
                      cmap=cmap)
        ax[i].set_autoscale_on(False)
        end_xlim = 7.5 if i == 1 else 4.0
        ax[i].set_xlim([2.8, end_xlim])
        ax[i].set_ylim([-5, 65])
        ax[i].add_patch(Rectangle((3.2,25), 0.4, 20, fill=False, color="k", 
                        linestyle='--', linewidth=2.0, joinstyle='miter'))
        ax[i].plot((3.2,3.6), (35,35), color='k', linewidth=2.0)
        ax[i].plot((3.4,3.4), (25,45), color='k', linewidth=2.0)
        xticks = np.arange(2.8, 7.6, 1) if i == 1 else np.arange(2.8, 4.1, 0.33)
        ax[i].xaxis.set_ticks(xticks)
        ax[i].xaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
        ax[i].tick_params(which='both', bottom=True, top=True, left=True, 
                          right=False)
        ax[i].tick_params(which='minor', length=5, color='k', width=2.5)

    plt.savefig('hyscore_kde.png', bbox_inches='tight', dpi=300)

############################## HYSCORE PLOTTER #################################   
#Introduce user to HyScore Eval functionality
print('WELCOME TO HYSCORE PLOTTER')
print('--------------------------\n')
print('Generates a series of KDE plots for hyscore-guided simulations.')
print('This script will search the 1_input directory for the following input:')
print('+ Angle of interest as angle_$N.dat')
print('+ Distance of interest as dist_$N.dat')
print('------------------------\n')

#Get filenames from output directory
filenames = combine_inp()

#Get coordinates from config file

#TODO construct dictionary {filename:{xa:[], ya:[]}}
x_data, y_data, z_data = collect_xyz_data(filenames)
graph_datasets(x_data, y_data, z_data)
