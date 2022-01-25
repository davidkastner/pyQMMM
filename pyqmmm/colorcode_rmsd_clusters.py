'''
See more here: https://github.com/davidkastner/pdb-utilities/blob/main/README.md
DESCRIPTION
    Plots RMSD and colors points based on their corresponding clusters.

    Author: David Kastner
    Massachusetts Institute of Technology
    kastner (at) mit . edu
   
'''

# Imports packages and dependencies
import pandas as pd
import matplotlib.pyplot as plt
import os.path
from pathlib import Path

# Converts a dat file to csv


def dat2df(dat_file):
    df = pd.read_csv(dat_file, sep='\s+', header=None, skiprows=1, index_col=0)
    df.index = [x/500 for x in range(df.shape[0])]
    df = df.iloc[1:, :]
    return df


def get_plot(final_df):
    # General plotting parameters for the Kulik lab
    font = {'family': 'sans-serif', 'weight': 'bold', 'size': 10}
    plt.rc('font', **font)
    plt.rcParams['axes.linewidth'] = 2.5
    plt.rcParams['xtick.major.size'] = 10
    plt.rcParams['xtick.major.width'] = 2.5
    plt.rcParams['ytick.major.size'] = 10
    plt.rcParams['ytick.major.width'] = 2.5
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.rcParams['mathtext.default'] = 'regular'

    clusters = [0, 1, 2, 3, 4]
    colors = ['#e63946', '#a8dadc', '#457b9d', '#1d3557', '#800000']
    label = ['Cluster 1', 'Cluster 2', 'Cluster 3', 'Cluster 4', 'Other']

    for cluster, color in zip(clusters[:4], colors[:4]):
        indicesToKeep = final_df['Cluster'] == cluster if cluster != 4 else final_df['Cluster'] >= cluster
        plt.scatter(final_df.loc[indicesToKeep, 'Frame'], final_df.loc[indicesToKeep, 'RMSD'],
                    edgecolors=color, s=9, facecolors='none', label=label[cluster if cluster < 4 else 4])

    plt.rc('axes', linewidth=2.5)
    plt.ylabel('Active site RMSD (Å)', fontsize=16, weight='bold')
    plt.xlabel('Time (ns)', fontsize=16, weight='bold')
    plt.tick_params(labelsize=14)
    plt.tick_params(which='both', bottom=True, top=True, left=True, right=True)
    plt.tick_params(which='minor', length=5, color='k', width=2.5)
    plt.savefig('clus_rmsd.png', bbox_inches='tight', dpi=600)
    plt.show()


def color_code_rmsd_clusters():
    # Welcome user and print some instructions
    print('\n.--------------------------.')
    print('| COLOR CODE RMSD CLUSTERS |')
    print('.--------------------------.\n')
    print('This script will search your directory for the following output:')
    print('+ CCPTraj RMSD file > rmsd.dat')
    print('+ List of frames assigned clusters > cnumvtime.dat')
    print('+ Root mean square deviation > rmsd.dat\n')

    # Check for required files
    expected_dat = ['rmsd.dat', 'cnumvtime.dat']

    # Check the users directory for analyzeable files
    for dat in expected_dat:
        data_file = Path(dat)
        if data_file.exists():
            print('Found {}'.format(dat))
        else:
            print('No {}'.format(dat))
            print('Please add {} to your directory'.format(dat))
            exit()

    rmsd_df = dat2df(expected_dat[0])
    clus_df = dat2df(expected_dat[1])

    final_df = pd.concat([rmsd_df, clus_df], axis=1)
    final_df.columns = ['RMSD', 'Cluster']
    final_df['Frame'] = final_df.index


# Execute the function when run as a script but not if used as a pyQM/MM module
if __name__ == "__main__":
    color_code_rmsd_clusters()
