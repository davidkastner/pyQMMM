"""Breaks up TeraChem optimization XYZ file into individual frames."""

import os
import shutil


def check_exists():
    """
    Check to see if user's xyz file is in the current directory
    """
    name = input("What is the name of your .xyz ensemble (ignore extenstion)? ")
    file_name = "{}.xyz".format(name)
    if os.path.exists(file_name):
        print("Found {}".format(file_name))
    else:
        print("No {}".format(dat))
        exit()
    return file_name


def create_dir():
    """
    Create a new directory to store the frames
    """
    dir = "movie"
    if os.path.exists(dir):
        shutil.rmtree(dir)
        os.makedirs(dir)
    else:
        os.makedirs(dir)


def get_frames(file_name):
    """
    Break up the original xyz file.
    """
    current_frame = 0
    with open(file_name, "r") as ensemble:
        for line in ensemble:
            if len("".join(line.split())) == 2:
                current_frame += 1
                if current_frame > 1:
                    f.close()
                f = open("./movie/{}.xyz".format(current_frame), "w")
            f.write(line)


def xyz_movie_generator():
    # Welcome user and print some instructions
    print("\n.---------------------.")
    print("| XYZ MOVIE GENERATOR |")
    print(".---------------------.\n")
    print("This script takes the TeraChem xyz file and breaks it up.")
    print("This allows Chimera to make a movie from the optimization.")
    print("It will search your directory for optim.xyz")
    print("------------------------\n")

    # Run the functions to generate individual movie frames
    file_name = check_exists()
    create_dir()
    get_frames(file_name)


if __name__ == "__main__":
    xyz_movie_generator()
