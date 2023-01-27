"""Methods for batch submitting analyses."""

import os
import shutil

def submit_replicate_cpptraj():
    """
    Submits analyses across all replicates.

    Notes
    -----
    The user will need to set the variables script and job_path.
    - script is the name the your specific cpptraj script
    - job_path is the path within each replicate folder to get to your jobs
    - There is also an option to ignore directories if some are not associated with a replicate

    """
    # Load modules
    os.system("module load sge")
    os.system("module load amber/18")

    # Job specific variables for user to set
    script = "cluster.q" # The name of the job script to submit
    job_path = "2_analysis" # The path within each
    files_to_copy = "cluster" # The directory containing the job files
    ignore_dirs = ["cluster", "hbond"] # Don't enter into these directories

    # Get path elements
    root = os.getcwd()
    all_files = sorted(os.listdir(root))

    # Loop over all replicate directories
    replicate_dirs = sorted([file for file in all_files if os.path.isdir(file) and file not in ignore_dirs])
    for replicate_dir in replicate_dirs:
        # Only directories, not files
        path_to_jobs = f"{root}/{replicate_dir}/{job_path}"
        os.chdir(path_to_jobs)
        shutil.copytree(f"{root}/{files_to_copy}", f"{os.getcwd()}/{files_to_copy}")
        os.chdir(files_to_copy)
        
        # Loop over all job directories
        job_dirs = sorted([file for file in os.listdir() if os.path.isdir(file)])
        for job_dir in job_dirs:
            path_to_job = f"{path_to_jobs}/{files_to_copy}/{job_dir}"
            os.chdir(path_to_job)
            os.system(f"qsub {script}")
            print(f"Submitted: {path_to_job}")

if __name__ == "__main__":
    submit_replicate_cpptraj()