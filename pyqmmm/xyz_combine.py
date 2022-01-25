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

'''
################################ DEPENDENCIES ##################################
import numpy as np

################################## FUNCTIONS ###################################

'''
Get the request frames for each file from the user.
Returns
-------
frames : list
    List of lists containing the frames the user wants from each file in order
'''


def requested_frames():
    request = 'start'
    file_count = 0
    frames_list = []

    while request != '':
        # What frames would you like from the first .xyz file
        request = input('Frames from file #{}? (1_2): '.format(file_count))

        if request != '':
            # Check the request and convert it to a list even if it is hyphenated
            temp = [(lambda sub: range(sub[0], sub[-1] + 1))
                    (list(map(int, ele.split('-')))) for ele in request.split('_')]
            frames = [b for a in temp for b in a]
            frames_list.append(frames)

    return frames_list


'''
Loop through the coordinate files and store each frame as a list element
Parameters
-------
atoms : list
    list of atoms indices
Get the user's reaction coordinate definition.
Returns
-------
atoms : list
    list of atoms indices
'''


def store_frames():

    # General function handler


def combine_xyz_files():
    # Welcome the user to the file and introduce basic functionality
    print('\n.-------------------.')
    print('| COMBINE XYZ FILES |')
    print('.-------------------.\n')
    print('Add both xyz trajectories to the current directory.')
    print('You can combine as many xyz files as you need.')
    print('Leave the prompt blank when you are done.\n')

    # Find out what frames the user wants combined
    frames_list = requested_frames()


if __name__ == "__main__":
    combine_xyz_files()
