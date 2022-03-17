'''
Docs: https://github.com/davidkastner/pyQMMM/blob/main/pyqmmm/README.md
DESCRIPTION
   After clustering with CPPTraj, you will be returned with a summary.dat file.
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

def get_iteration_pairs():
    return

def cluster_frame_indexer():
    print('\n.-----------------------.')
    print('| CLUSTER FRAME INDEXER |')
    print('.-----------------------.\n')
    print('Run this script in the same directory as cnumvtime.dat.')
    print('The script prints the frame indices.\n')
    print('It will also provide an interval if you want only a subset.\n')


if __name__ == "__main__":
    cluster_frame_indexer()
