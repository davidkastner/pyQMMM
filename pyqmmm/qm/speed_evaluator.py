'''Find how fast on average the AIMD timesteps are happening for benchmarking'''

import os
import sys
import re

def check_if_aimd() -> str:
    """
    Check if the TeraChem .out file contains AIMD calculation results.

    Returns
    -------
    out_file : str
        The name of the TeraChem out file.

    """

    # Loop through the current directory to collect all TeraChem .out files
    files = []
    for file in os.listdir("."):
        if file == "qmscript.out":
            files.append(file)
    # A single outfile was found we will save the filename
    if len(files) == 1:
        outfile = files[0]
    # End if there are multiple .out files
    if len(files) > 1:
        sys.exit("This directory contains multiple TeraChem AIMD jobs.")
    # End if there are no .out files
    elif len(files) == 0:
        sys.exit("This directory does not contain a TeraChem AIMD job.")

    # Check if the .out file is a successful AIMD job
    aimd = False # We assume it is not an aimd file
    with open(outfile, "r") as outfile_contents:
        for line in outfile_contents:
            if "=MD= Time per MD step:" in line:
                aimd = True
                print("A TeraChem AIMD job was found.")
                break
    if aimd == False:
        sys.exit("This directory does not contain a TeraChem AIMD job.")

    return outfile

def get_avg_mdstep_time(outfile: str) -> tuple[int,int,int]:
    """
    Calculate the avg, max, and min MD time step compute time.

    Parameters
    ----------
    out_file : str
        The name of the TeraChem out file.

    Returns
    -------
    avg_time : int
        The average time of all MD steps in the simulation.
    max_time : int
        The max time from all MD steps in the simulation.
    min_time : int
        The min time from all MD steps in the simulation.
    """
    # Open the TeraChem AIMD output file
    with open(outfile, "r") as outfile_contents:
        time = [] 
        # Loop through the AIMD output and collect the timestep compute times
        for line in outfile_contents:
            if "=MD= Time per MD step:" in line: # AIMD will have this text
                time.append(float(re.findall("\d+\.\d+", line)[0]))
    print(time)
    avg_time = sum(time)/len(time)
    max_time = max(time)
    min_time = min(time)
    return avg_time, max_time, min_time

def speed_evalutor():
    """
    Driver function for calculating the speed of AIMD from the output.
    """

    print("\n.-----------------.")
    print("| SPEED EVALUATOR |")
    print(".-----------------.\n")
    print("First run organize_energy_scan_data.py for each job.")
    print("Move the scan_charge and scan_spin to the same directory.")
    print("Give them unique names.")
    print("Extract summed charge and spin for user specified atoms.\n")

    # Check if there is aimd data in the current directory to analyze
    outfile = check_if_aimd()
    # Calculate the average, maximum, and minimum times for each step
    avg_time,max_time,min_time = get_avg_mdstep_time(outfile)

    # Report the findings to the user
    print(f"Avg. time: {avg_time}")
    print(f"Max. time: {max_time}")
    print(f"Min. time: {min_time}")

if __name__ == "__main__":
    speed_evalutor()