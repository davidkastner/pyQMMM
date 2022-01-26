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
import glob

################################## FUNCTIONS ###################################

'''
Search the current directory and located 
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


def get_xyz_trajectories():
    file_list = glob.glob('./*.xyz')
    file_list_sorted = sorted(file_list)


'''
Get the request frames for each file from the user.
Parameters
----------
xyz_filename_list : list
    A list of all xyz trajectory files names as strings

Returns
-------
frames : list
    List of lists containing the frames the user wants from each file in order
'''


def request_frames(xyz_filename_list):
    # Save the requests with its associated file as some may be empty requests
    file_request_dict = {}

    # What frames would you like from the first .xyz file?
    for file in xyz_filename_list:
        request = input('Frames from {}? (e.g., 1,3-5): '.format(file))

        if request != '':
         # Check the request and convert it to a list even if it is hyphenated
            temp = [(lambda sub: range(sub[0], sub[-1] + 1))
                    (list(map(int, ele.split('-')))) for ele in request.split('-')]
            frames = [b for a in temp for b in a]
            file_request_dict[file] = frames

    return file_request_dict


def combine_xyz_files():
    # Welcome the user to the file and introduce basic functionality
    print('\n.-------------------.')
    print('| COMBINE XYZ FILES |')
    print('.-------------------.\n')
    print('Searches current directory for xyz trajectory files.')
    print('You can combine as many xyz files as you need.')
    print('Name your xyz file as 1.xyz, 2.xyz, etc.')
    print('Leave the prompt blank when you are done.\n')

    # Find out what frames the user wants combined
    frames_list = request_frames()


if __name__ == "__main__":
    combine_xyz_files()
