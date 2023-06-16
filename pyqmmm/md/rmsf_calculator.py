"""Calculate the RMSF across replicates using MDAnalysis"""

import MDAnalysis as mda
from MDAnalysis.analysis import align, rms
import numpy as np
import pandas as pd
import time
import os
from pathlib import Path
import warnings

# Ignore MDAnalysis UserWarnings
warnings.filterwarnings('ignore', category=UserWarning, module='MDAnalysis')

def calculate_rmsf_per_trajectory(topology, trajectory, reference, count):
    """
    Calculate the RMSF per trajectory.

    Calculates the RMSF for each residue in a given trajectory.
    Aligns the trajectory to a reference, calculates the RMSF,
    and returns a DataFrame with the residue IDs, names, and RMSF values.

    Parameters
    ----------
    topology : str
        Path to the topology file.
    trajectory : str
        Path to the trajectory file.
    reference : MDAnalysis.core.universe.Universe
        The reference structure to which the trajectory is aligned.
    count : int
        The index of the trajectory, used for naming in the resulting DataFrame.

    Returns
    -------
    df : pandas.DataFrame
        DataFrame containing resIDs, residue names, and RMSFs for a trajectory.

    """
    print(f"   > Reading: {trajectory}")
    u = mda.Universe(topology, trajectory, dt=0.2, format="TRJ")

    # Use 'all' to select all atoms
    aligner = align.AlignTraj(u, reference, select="all", in_memory=True)
    # Perform trajectory alignment
    aligner.run()

    print(f"   > Computing the RMSF: {trajectory}")
    R = rms.RMSF(u.select_atoms("all")).run()
    rmsf_values = R.results.rmsf

    # Calculate average RMSF per residue and store residue info
    rmsf_residues = []
    resnames = []
    resids = []
    min_index = min(u.atoms.indices)
    for residue in u.atoms.residues:
        # Adjust indices
        atoms_in_residue = [index - min_index for index in residue.atoms.indices]
        # Check if the index is within the rmsf_values range
        if max(atoms_in_residue) >= len(rmsf_values):
            print(f"Skipping residue {residue.resname}{residue.resid}")
            continue
        avg_rmsf = np.mean(rmsf_values[atoms_in_residue])
        rmsf_residues.append(avg_rmsf)
        resnames.append(residue.resname)
        # Start index at 1 instead of 0
        resids.append(residue.resid+1)

    # Create a DataFrame for each trajectory with the residue and RMSF
    trajectory_name = "Traj_" + str(count + 1)  # Count as trajectory name
    df = pd.DataFrame({
        'ResID': resids,
        'ResName': resnames,
        trajectory_name: rmsf_residues
    })

    return df

def calculate_rmsf(topology, trajectories, reference_file=None):
    """
    Calculate the RMSF with MDAnalysis.

    The script works with analyzing the RMSF across multiple replicates.
    It expects the .crd extension from CCPTraj,
    which needs to be labeled as TRJ for MDAnalysis.

    Parameters
    ----------
    reference_file : str
        The path to a PDB file that you would like to use as a reference.

    """
    # Greet the user
    print("\n.-----------------.")
    print("| RMSF Calculator |")
    print(".-----------------.\n")
    print("Calculates the RMSF by residue.\n")
    start_time = time.time()  # Used to report the executation speed

    rmsf_df = pd.DataFrame()
    # Separate DataFrame for per-residue RMSF
    rmsf_residue_df = pd.DataFrame()

    # Use the provided reference structure if available
    if reference_file:
        reference = mda.Universe(reference_file)
    # Otherwise use the first frame of the first trajectory as reference
    else:
        mda.Universe(topology, trajectories[0], dt=0.2, format="TRJ")
    
    # Iterate over trajectories
    rmsf_residue_df = pd.DataFrame()
    for count, trajectory in enumerate(trajectories):
        df = calculate_rmsf_per_trajectory(topology, trajectory, reference, count)

        # Concatenate current trajectory DataFrame with the total DataFrame
        if rmsf_residue_df.empty:
            rmsf_residue_df = df
        else:
            rmsf_residue_df = pd.merge(rmsf_residue_df, df, on=['ResID', 'ResName'])

    # Calculate average RMSF across trajectories
    rmsf_residue_df['Avg. RMSF'] = rmsf_residue_df.iloc[:, 2:].mean(axis=1)

    # Save to file per-residue RMSF values to a CSV
    out_file = "rmsf.csv"
    rmsf_residue_df.to_csv(out_file, index=False)

    total_time = round(time.time() - start_time, 3)
    print(
        f"""
        \t-------------------------CHARGE MATRICES END--------------------------
        \tRESULT: Computed the RMSF for {count+1} trajectories.
        \tOUTPUT: Saved results in {out_file}.
        \tTIME: Total execution time: {total_time} seconds.
        \t--------------------------------------------------------------------\n
        """
    )

if __name__ == "__main__":
    # Run the command-line interface when this script is executed
    calculate_rmsf("xtal.pdb")
