'''
See more here: https://github.com/davidkastner/quick-csa/blob/main/README.md
DESCRIPTION
    Reaction path calculations often need to be restarted from a later point.
    For example, when rerunning a scan of the peak to get higher resolution TS.
    Afterwards, the .xyz files of the two scans need to be stitched together.
    Here, users can specify the frames from each file that need to be combined.
    The script will generate a new combined file.

    Author: David Kastner
    Massachusetts Institute of Technology
    kastner (at) mit . edu

SEE ALSO
    energy_collector.py
    collect_reaction_coordinate.py
'''
################################ DEPENDENCIES ##################################
import numpy as np

################################## FUNCTIONS ###################################
'''
Get the request frames for each file from the user.
Returns
-------
frames : list
    List of lists containing the frames the user wants from each file
'''
def requested_frames():
    # What frames would you like from the first .xyz file
    request = input('Frames from first file? (e.g., 1_2): ')

    # Check the request and convert it to a list even if it is hyphenated
    temp = [(lambda sub: range(sub[0], sub[-1] + 1))(list(map(int, ele.split('-')))) for ele in request.split('_')] 
    frames = [b for a in temp for b in a] 

    return frames

# General function handler
def xyz_combine():
    print('\n.------------------------.')
    print('| WELCOME TO XYZ COMBINE |')
    print('.------------------------.\n')
    print('Add both xyz trajectories to the current directory.')
    print('You can combine as many xyz files as you need.')
    print('Leave the prompt blank when you are done.\n')

    # Find out what frames the user wants combined
    frames = requested_frames()


if __name__ == "__main__":
    xyz_combine()
