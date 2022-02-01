'''
Docs: https://github.com/davidkastner/pyQMMM/blob/main/pyqmmm/README.md
DESCRIPTION
    Takes the ppm image output from VMD and converts them to PNGs.
    These can then be merged in blender to create a movie of the trajectory.
    Uses the pnmtopng utility so make sure it is installed.
   
    Author: David Kastner
    Massachusetts Institute of Technology
    kastner (at) mit . edu
   
'''

################################ DEPENDENCIES ##################################
import os

################################# FUNCTIONS ####################################


def convert_ppm_png():
    directory = './'
    # Loop through all images in the current directory
    count = 0
    for filename in sorted(os.listdir(directory)):
        file = os.path.join(directory, filename)

        # Checking if it is a file
        if os.path.isfile(file):
            os.system('pnmtopng {} > {}.png'.format(file, count))
            count += 1


if __name__ == "__main__":
    convert_ppm_png()
