"""Prepares a killed ORCA NEB job for a restart by moving and renaming files."""

import os
import shutil

def create_delete_folder(folder_name='delete'):
    """
    Create a directory for files to be deleted if it doesn't already exist.

    Parameters
    ----------
    folder_name : str, optional
        The name of the folder where files will be moved to before deletion.

    Returns
    -------
    None
    """
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

def keep_file(filename):
    """
    Check if a file is to be kept based on its extension or name.

    Parameters
    ----------
    filename : str
        The name of the file to be checked.

    Returns
    -------
    bool
        True if the file should be kept, False otherwise.
    """
    # Extensions to keep
    keep_extensions = ['.in', '.allxyz', '.xyz', '.sh']
    # Keep files with specific extensions or names
    return filename.endswith(tuple(keep_extensions)) or filename.endswith(".gbw") or filename == 'delete' or filename.endswith(".py")

def rename_gbw(filename):
    """
    Rename .gbw files if they start with "qmscript".

    Parameters
    ----------
    filename : str
        The name of the file to potentially rename.

    Returns
    -------
    str
        The new name of the file, if renamed, or the original name.
    """
    if filename.startswith("qmscript") and filename.endswith(".gbw"):
        return "restart" + filename[len("qmscript"):]
    return filename

def move_files(files, delete_folder='delete'):
    """
    Move files to a specified folder, excluding those that are to be kept.

    Parameters
    ----------
    files : list of str
        The list of files in the current directory.
    delete_folder : str, optional
        The name of the folder to move files to.

    Returns
    -------
    None
    """
    files_to_move = [f for f in files if not keep_file(f)]
    num_files_to_move = len(files_to_move)

    # Ask for user confirmation before moving files
    response = input(f"{num_files_to_move} files will be moved to the '{delete_folder}' folder. Continue? (y/n): ")
    if response.lower() != 'y':
        print("Operation cancelled by user.")
        return

    for file in files_to_move:
        shutil.move(file, os.path.join(delete_folder, file))
        print(f"Moved: {file}")

    for file in files:
        if file.endswith(".gbw"):
            new_name = rename_gbw(file)
            os.rename(file, new_name)
            print(f"Renamed: {file} to {new_name}")

    print("Files have been moved or renamed as necessary, excluding specified files.")

if __name__ == "__main__":
    create_delete_folder()
    files_in_directory = [f for f in os.listdir() if f != 'delete']
    move_files(files_in_directory)
