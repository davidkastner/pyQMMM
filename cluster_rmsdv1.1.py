'''
See more here: https://github.com/davidkastner/pdb-utilities/blob/main/README.md
DESCRIPTION
   Plots RMSD and colors points based on their corresponding clusters
   Author: David Kastner
   Massachusetts Institute of Technology
   kastner (at) mit . edu
'''

#Imports packages and dependencies
import pandas as pd
import matplotlib.pyplot as plt
import os.path
from pathlib import Path

#Converts a dat file to csv
def dat2df(dat_file):
  df = pd.read_csv(dat_file, sep='\s+', header=None, skiprows=1, index_col=0)
  return df

#Generate the plot
def get_plot(final_df):
  clusters = [0,1,2,3,4]
  colors = ['#e63946','#a8dadc','#457b9d','#1d3557','#f1faee']
  label = ['Cluster 1', 'Cluster 2', 'Cluster 3', 'Cluster 4', 'Other']

#Associate each point with the color of its cluster
  for cluster, color in zip(clusters,colors):
    indicesToKeep = final_df['Cluster'] == cluster if cluster != 4 else final_df['Cluster'] >= cluster
    plt.scatter(final_df.loc[indicesToKeep, 'Frame']
              , final_df.loc[indicesToKeep, 'RMSD']
              , edgecolors = color
              , s = 15
              , facecolors='none'
              , label = label[cluster if cluster < 4 else 4]
              , alpha = .15)

  plt.rc('axes', linewidth=2.5)
  plt.title('Clustered Poses by RMSD', fontsize=18)
  plt.ylabel('RMSD (Å)', fontsize=16)
  plt.xlabel('Frames', fontsize=16)
  plt.xticks(rotation=45)
  plt.tick_params(labelsize=14)
  plt.legend()
  plt.savefig('clus_rmsd.pdf', bbox_inches='tight')
  plt.show()

#Welcome user and print some instructions
print('Welcome to ClusterRMSD')
print('-----------------------\n')
print('This script will search your directory for the following output:')
print('+ CCPTraj RMSD file > rmsd.dat')
print('+ List of frames assigned clusters > cnumvtime.dat')
print('+ Root mean square deviation > rmsd.dat')
print('------------------------\n')


#Check for required files
expected_dat = ['rmsd.dat','cnumvtime.dat']

#Check the users directory for analyzeable files
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

final_df = pd.concat([rmsd_df,clus_df], axis=1)
final_df.columns = ['RMSD', 'Cluster']
final_df['Frame'] = final_df.index

get_plot(final_df)
