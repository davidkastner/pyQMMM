"""Takes an xyz file and reverses the order of the frames."""


def xyz_flipper(in_file: str) -> None:
    """
    Takes an xyz file and reverses the order of the frames.

    Parameters
    ----------
    in_file : str
        The name of the input filexyz trajectory to reverse.
    
    Notes
    -----
    For example, this is usually scan_optim in TeraChem.

    """
    # The name of the input filexyz trajectory to reverse
    in_file = "scan_optim"

    # Open the input file for reading
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

    # Reverse the order of the frames
    frames = frames[::-1]

    # Write the reversed frames to a new file
    with open(f"{in_file}_flip.xyz", "w") as f:
        for frame_lines in frames:
            f.write("".join(frame_lines))

if __name__ == "__main__":
    xyz_flipper("scan_optim")
