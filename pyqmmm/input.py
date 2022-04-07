'''
Docs: https://github.com/davidkastner/pyQMMM/blob/main/pyqmmm/README.md
DESCRIPTION
    A compilation of essential standalone functions to get user input.

    Author: David Kastner
    Massachusetts Institute of Technology
    kastner (at) mit . edu

'''
################################ DEPENDENCIES ##################################

################################## FUNCTIONS ###################################


'''
Request frames for each file from the user.
Parameters
----------
xyz_filename : str
    The filename of the current xyz trajectory of interest

Returns
-------
frames : list
    The frames the user requested to be extracted from the xyz trajectory
'''


def request_frames(xyz_filename):
    # What frames would you like from the first .xyz file?
    if xyz_filename == 'combined.xyz':
        return
    request = input('Which frames do you want from {}?: '.format(xyz_filename))
    # Continue if the user did not want that file processed and pressed enter
    if request == '':
        return request
    # Check the request and convert it to a list even if it is hyphenated
    temp = [(lambda sub: range(sub[0], sub[-1] + 1))
            (list(map(int, ele.split('-')))) for ele in request.split(',')]
    frames = [b for a in temp for b in a]

    print('For {} you requested frames {}.'.format(xyz_filename, frames))

    return frames
