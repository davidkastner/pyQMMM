"""Takes the PPM image output from VMD and converts them to PNGs."""

import os


def ppm2png_converter():
    """
    Converts a PPM to a PNG.

    When VMD is used to generate molecular movies,
    one common point of annoyance it that the output files are written as PPM.
    This script will convert the files to PNGs so they can be combined.
    Pnmtopng from Netpbm must be installed to perform the conversion.
    """
    directory = "./"
    # Loop through all images in the current directory
    count = 0
    for filename in sorted(os.listdir(directory)):
        file = os.path.join(directory, filename)

        # Checking if it is a file
        if os.path.isfile(file):
            os.system(f"pnmtopng {file} > {count}.png")
            count += 1


if __name__ == "__main__":
    ppm2png_converter()
