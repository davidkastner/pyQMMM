"""Calculates the bond valence for coordinating atoms across a reaction"""

import glob
import time
import subprocess
import pandas as pd

def calculate_bond_valence(atom_pairs, threads):
    start_time = time.time()

    # Get all wave function files
    wfn_files = glob.glob("*.gbw")
    if len(wfn_files) == 0:
        raise Exception("   > No wavefunction file found.")

    # Sort the files by the starting number
    wfn_files.sort(key=lambda x: int(x.split('_')[0]))

    # Dictionary to store the bond order information
    bond_order_data = {f"Pair_{pair}": [] for pair in atom_pairs}
    steps = []

    for wfn in wfn_files:
        step_name = wfn.split('.')[0]
        steps.append(step_name)

        command = f"Multiwfn {wfn} -nt {threads}"

        print(f"   > Processing {step_name}")
        print(f"      > Executing the command: {command}")

        proc = subprocess.Popen(
            command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True
        )

        commands = ["9", "1", "n", "0", "q"]
        output = proc.communicate("\n".join(commands).encode())

        lines = str(output[0]).split("\\n")
        step_data = {}

        start_processing = False
        for line in lines:
            if "Bond orders with absolute value" in line:
                start_processing = True
                continue

            if "Note: The \"Total\" bond orders shown above" in line:
                break

            if start_processing and "Alpha:" in line and "Total:" in line:
                parts = line.split("(")
                atom1 = int(parts[0].split()[-1])
                atom2 = int(parts[1].split()[-1])
                bond_order = float(parts[2].split()[-1])
                pair_key = f"Pair_{(atom1, atom2)}" if (atom1, atom2) in atom_pairs else f"Pair_{(atom2, atom1)}"
                step_data[pair_key] = bond_order

        # Append bond order data for this step
        for key in bond_order_data:
            bond_order_data[key].append(step_data.get(key, None))

    # Create DataFrame from the bond order data
    bond_order_df = pd.DataFrame(bond_order_data, index=steps)

    # Save the results as a CSV file
    bond_order_df.to_csv("bond_valence.csv")

    total_time = round(time.time() - start_time, 3)
    print(f"\tRESULT: Calculated bond orders for {len(wfn_files)} steps.")
    print(f"\tOUTPUT: Generated bond valences in the current directory.")
    print(f"\tTIME: Total execution time: {total_time} seconds.\n")

if __name__ == "__main__":
    atom_pairs = [(145, 146), (65, 145), (66, 145), (12, 145), (32, 145), (145, 149)]
    calculate_bond_valence(atom_pairs, 4)