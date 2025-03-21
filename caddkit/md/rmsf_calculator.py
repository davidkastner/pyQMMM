"""Calculate the RMSF across replicates using MDAnalysis"""

import MDAnalysis as mda
from MDAnalysis.analysis import align, rms
import numpy as np
import pandas as pd
import time
import multiprocessing as mp
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

    # Use 'all' to select all atoms or 'backbone' for backbone atoms
    aligner = align.AlignTraj(u, reference, select="backbone and resid 3-14 19-26 29 30", in_memory=True)
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
        resids.append(residue.resid)

    # Create a DataFrame for each trajectory with the residue and RMSF
    trajectory_name = Path(trajectory).parts[0]  # Count as trajectory name
    df = pd.DataFrame({
        'ResID': resids,
        'ResName': resnames,
        trajectory_name: rmsf_residues
    })

    return df

def main(topology, trajectories, reference_file):
    """
    Calculate the RMSF with MDAnalysis in parallel.
    """
    print("\n.-----------------.")
    print("| RMSF Calculator |")
    print(".-----------------.\n")
    print("Calculates the RMSF by residue.\n")
    start_time = time.time()  # Track execution time

    # Load the reference structure once (shared across processes)
    reference = mda.Universe(reference_file) if reference_file else mda.Universe(topology, trajectories[0], dt=0.2, format="TRJ")

    # Use multiprocessing to calculate RMSF for each trajectory
    with mp.Pool(processes=mp.cpu_count()) as pool:
        results = pool.starmap(calculate_rmsf_per_trajectory, [(topology, traj, reference, count) for count, traj in enumerate(trajectories)])

    # Combine results
    rmsf_residue_df = pd.concat(results, axis=1).T.drop_duplicates().T  # Merge all results

    # Calculate average RMSF across trajectories
    rmsf_residue_df['Avg. RMSF'] = rmsf_residue_df.iloc[:, 2:].mean(axis=1)
    rmsf_residue_df['Avg. Std. Dev'] = rmsf_residue_df.iloc[:, 2:-1].std(axis=1)

    # Save to CSV
    out_file = "rmsf.csv"
    rmsf_residue_df.to_csv(out_file, index=False)

    total_time = round(time.time() - start_time, 3)
    print(
        f"""
        \t-------------------------CHARGE MATRICES END--------------------------
        \tRESULT: Computed the RMSF for {len(trajectories)} trajectories in parallel.
        \tOUTPUT: Saved results in {out_file}.
        \tTIME: Total execution time: {total_time} seconds.
        \t--------------------------------------------------------------------\n
        """
    )

if __name__ == "__main__":
    # Run the command-line interface when this script is executed
    protein = input("What is the name of your protein? ")
    topology = f"1/{protein}_dry.prmtop"
    reference_file = f"1/{protein}_dry.pdb"
    trajectories = ["1/1_output/constP_prod.crd",
                    "1u/1_output/constP_prod.crd",
                    "2/1_output/constP_prod.crd",
                    "3/1_output/constP_prod.crd",
                    "7/1_output/constP_prod.crd",
                    "8u/1_output/constP_prod.crd",
                    "13/1_output/constP_prod.crd",
                    "15/1_output/constP_prod.crd",
                    ]
    main(topology, trajectories, reference_file)
