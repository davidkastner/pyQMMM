"""
Reverses an xyz trajectory, for example if it was run backwards for better convergence.
"""

from typing import List

def read_xyz(in_file: str) -> List[List[str]]:
    """
    Read an xyz trajectory file and return a list of frames.

    Parameters
    ----------
    in_file : str
        The name of the xyz file to read.

    Returns
    -------
    frames : List[List[str]]
        A list of frames, each frame is a list of lines.

    """
    with open(f"{in_file}.xyz", "r") as f:
        lines = f.readlines()

    # Extract the frames
    frames = []
    frame_lines = []
    for line in lines:
        if line.startswith("Converged"):
            if frame_lines:
                frames.append(frame_lines)
                frame_lines = []
        frame_lines.append(line)
    frames.append(frame_lines)

    return frames


def write_xyz(out_file: str, frames: List[List[str]]) -> None:
    """
    Write frames to an xyz trajectory file.

    Parameters
    ----------
    out_file : str
        The name of the output xyz file.
    frames : List[List[str]]
        A list of frames, each frame is a list of lines.
    """
    with open(f"{out_file}.xyz", "w") as f:
        for frame_lines in frames:
            f.write("".join(frame_lines))


def flip_xyz_trajectory(in_file: str) -> None:
    """
    Takes an xyz file and reverses the order of the frames.

    Parameters
    ----------
    in_file : str
        The name of the input xyz file to reverse.

    Notes
    -----
    The input file should be an xyz trajectory file, usually named scan_optim in TeraChem.
    The output file will be named as "{in_file}_flip.xyz".
    """
    print("\n.-------------.")
    print("| XYZ FLIPPER |")
    print(".-------------.\n")
    print("Reverse an xyz trajectory.")
    print("Useful if a geometry scan was run in reverse.\n")

    frames = read_xyz(in_file)

    # Reverse the order of the frames
    frames_reversed = frames[::-1]

    # Write the reversed frames to a new file
    out_file = f"{in_file}_flip"
    write_xyz(out_file, frames_reversed)

    print(f"   > Reversed trajectory written to {out_file}.xyz")


if __name__ == "__main__":
    flip_xyz_trajectory("scan_optim")