'''
Docs: https://github.com/davidkastner/pyQMMM/blob/main/pyqmmm/README.md
DESCRIPTION
   After clustering with CPPTraj, you will be returned with a cnuvtime.dat file.
   This contains the frames numbers and their corresponding clusters.
   This script will find all frames in the main cluster and condense it into
   the smallest string of numbers. This can then be used with CPPTraj to convert
   to a new mdcrd.
   parm welo5_solv.prmtop
   trajin constP_prod.mdcrd
   trajout output.mdcrd onlyframes 2,5-200,202-400
   Author: David Kastner
   Massachusetts Institute of Technology
   kastner (at) mit . edu
   
'''

################################## FUNCTIONS ###################################

'''
Reads 
Parameters
----------
    
Returns
-------
'''

def get_clusters(file):
    cluster_list = []
    with open(file, 'r') as cluster_file:
        for line in cluster_file:
            frame_num = int(line.split('')[0])
            cluster_num = int(line.split('')[1])
            if cluster_num = 0:
                cluster_list.append(cluster_num)
    return cluster_list

def condense_numbering(cluster_list):
    return final_selection

def calculate_interval(cluster_list):
    return

def cluster_frame_indexer():
    print('\n.-----------------------.')
    print('| CLUSTER FRAME INDEXER |')
    print('.-----------------------.\n')
    print('Run this script in the same directory as cnumvtime.dat.')
    print('The script prints the frame indices.\n')
    print('It will also provide an interval if you want only a subset.\n')

    # This is the standard name but feel free to change it if yours is different
    cluster_definitions_file = 'cnumvtime.dat'
    cluster_list = get_clusters(cluster_definitions_file)
    final_selection = condense_numbering(cluster_list)
    
    # Important output for the user
    print(f"Total frames counted: {}")
    print(f"Final selection: {}")
    print(f"Interval: {}")

if __name__ == "__main__":
    cluster_frame_indexer()
