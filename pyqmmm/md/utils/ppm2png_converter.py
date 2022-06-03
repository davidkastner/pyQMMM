"""Takes the ppm image output from VMD and converts them to PNGs."""

import os


def ppm2png_converter():
    """
    Converts a PNG to a PNG.
    Pnmtopng from Netpbm must be installed to perform the conversion.
    """
    directory = "./"
    # Loop through all images in the current directory
    count = 0
    for filename in sorted(os.listdir(directory)):
        file = os.path.join(directory, filename)

        # Checking if it is a file
        if os.path.isfile(file):
            os.system("pnmtopng {} > {}.png".format(file, count))
            count += 1


if __name__ == "__main__":
    ppm2png_converter()
