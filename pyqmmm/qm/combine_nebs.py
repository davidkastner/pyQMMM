import glob
import re

def get_sorted_xyz_files():
    """
    Gets a sorted list of .xyz files in the current directory whose names are only numbers.
    Ignores any files that do not match this naming pattern or are explicitly set to be ignored.
    
    Returns
    -------
    list
        Sorted list of .xyz filenames that match the numeric pattern.
    """
    xyz_files = glob.glob("*.xyz")
    # Filter for files that are only numeric (e.g., "1.xyz") and exclude specific files
    numeric_xyz_files = [
        f for f in xyz_files if re.fullmatch(r"\d+\.xyz", f) and f != "bad_neb_ignore.xyz"
    ]
    # Sort the files numerically based on the integer in the filename
    numeric_xyz_files.sort(key=lambda x: int(x.split(".")[0]))
    return numeric_xyz_files

def extract_frames(xyz_filename):
    """
    Reads all frames from an xyz file and returns them as a list of strings.
    
    Parameters
    ----------
    xyz_filename : str
        The filename of the xyz file.
    
    Returns
    -------
    list
        A list of strings, each string representing a frame in the xyz file.
    """
    frames = []
    with open(xyz_filename, 'r') as file:
        lines = file.readlines()
        atom_count = lines[0].strip()
        frame_length = int(atom_count) + 2
        for i in range(0, len(lines), frame_length):
            frames.append("".join(lines[i:i + frame_length]))
    return frames

def combine_trajectories():
    """
    Combines xyz files into a single xyz trajectory file while removing duplicate frames.
    Only processes files named with numbers, skipping any specified files to ignore.
    """
    output_filename = "combined_nebs.xyz"
    xyz_files = get_sorted_xyz_files()
    combined_frames = []
    
    for idx, xyz_file in enumerate(xyz_files):
        frames = extract_frames(xyz_file)
        
        # If not the first file, check for duplicate with the last frame of previous file
        if idx > 0 and frames[0] == combined_frames[-1]:
            frames = frames[1:]  # Remove the first frame if it's a duplicate

        combined_frames.extend(frames)

    # Write the combined frames to a new file
    with open(output_filename, "w") as outfile:
        for frame in combined_frames:
            outfile.write(frame)
    
    print(f"Combined trajectory written to {output_filename}")

if __name__ == "__main__":
    combine_trajectories()
