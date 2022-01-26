'''
Docs: https://github.com/davidkastner/pyQMMM/blob/main/pyqmmm/README.md
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
Search the current directory for all xyz files and remove any non-trajectories
Parameters
-------
atoms : list
    list of atoms indices
Get the user's reaction coordinate definition.
Returns
-------
trajectory_list : list
    list string names of all the trajectory xyz files in the directory
'''


def get_xyz_trajectories():
    # Get all xyz files and sort them
    file_list = glob.glob('./*.xyz')
    sorted(file_list)
    xyz_filename_list = []

    # Loop through files and check to see if they are trajectories
    for file in file_list:
        with open(file, 'r') as current_file:
            trajectory = False
            first_line = True
            header_count = 0
            # If the atom count appears more than once than it is a trajectory
            for line in current_file:
                if first_line == True:
                    atom_count = line.strip()
                    header_count += 1
                    first_line = False
                if line.strip() == atom_count:
                    header_count += 1
                if header_count > 1:
                    trajectory = True
                    break
        # Combine all the trajectory files into a single list
        if trajectory == True:
            xyz_filename_list.append(file)

    return xyz_filename_list


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

    # Search through all xyz's in the current directory and get the trajectories
    xyz_filename_list = get_xyz_trajectories()

    # Find out what frames the user wants combined
    file_request_dict = request_frames(xyz_filename_list)

    # Save each frame of the trajectory to an list


if __name__ == "__main__":
    combine_xyz_files()
