"""Calculates the bond valence for coordinating atoms across a reaction"""

import glob
import time
import subprocess
import pandas as pd
import matplotlib.pyplot as plt

def format_plot() -> None:
    """
    General plotting parameters for the Kulik Lab.

    """
    font = {"family": "sans-serif", "weight": "bold", "size": 10}
    plt.rc("font", **font)
    plt.rcParams["xtick.major.pad"] = 5
    plt.rcParams["ytick.major.pad"] = 5
    plt.rcParams["axes.linewidth"] = 2
    plt.rcParams["xtick.major.size"] = 7
    plt.rcParams["xtick.major.width"] = 2
    plt.rcParams["ytick.major.size"] = 7
    plt.rcParams["ytick.major.width"] = 2
    plt.rcParams["xtick.direction"] = "in"
    plt.rcParams["ytick.direction"] = "in"
    plt.rcParams["xtick.top"] = True
    plt.rcParams["ytick.right"] = True
    plt.rcParams["svg.fonttype"] = "none"

def calculate_bond_valence(atom_pairs, threads):
    start_time = time.time()

    # Get all wave function files
    wfn_files = glob.glob("*.gbw")
    if len(wfn_files) == 0:
        raise Exception("   > No wavefunction file found.")

    # Sort the files by the starting number
    wfn_files.sort(key=lambda x: int(x.split('_')[0]))

    # Define the columns based on atom pairs
    columns = ['Step'] + [f'{pair[0]}-{pair[1]}' for pair in atom_pairs]

    # Open the CSV file
    with open("bond_valence.csv", "w") as csv_file:
        # Write the header
        csv_file.write(','.join(columns) + '\n')

        for wfn in wfn_files:
            step_name = wfn.split('.')[0]
            command = f"Multiwfn {wfn} -nt {threads}"

            print(f"   > Processing {step_name}")
            print(f"      > Executing command: {command}")

            proc = subprocess.Popen(
                command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True
            )

            commands = ["9", "1", "n", "0", "q"]
            output = proc.communicate("\n".join(commands).encode())

            lines = str(output[0]).split("\\n")
            step_data = {'Step': step_name}
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
                    if (atom1, atom2) in atom_pairs or (atom2, atom1) in atom_pairs:
                        step_data[f"{atom1}-{atom2}"] = bond_order
            
            # Create step_data as a list with the same order as columns
            step_data_list = [step_data.get(col, '') for col in columns]

            # Write the row to the CSV file
            csv_file.write(','.join(map(str, step_data_list)) + '\n')

    total_time = round(time.time() - start_time, 3)
    print(f"\tRESULT: Calculated bond orders for {len(wfn_files)} steps.")
    print(f"\tOUTPUT: Generated bond valences in the current directory.")
    print(f"\tTIME: Total execution time: {total_time} seconds.\n")

def plot_bond_valence():
    # Read the bond valence data from CSV, including the row names
    format_plot()
    bond_order_df = pd.read_csv("bond_valence.csv")

    # Replace NaN with 0
    bond_order_df = bond_order_df.fillna(0)

    # Define the colors for the lines
    colors = ['blue', 'green', 'red', 'orange', 'gray', 'purple']

    # Plotting each column (i.e., each atom pair)
    for idx, column in enumerate(bond_order_df.columns[1:]): # Skip the 'Step' column
        plt.plot(bond_order_df['Step'], bond_order_df[column], label=column, linewidth=2, color=colors[idx % len(colors)])

    plt.xlabel('mechanism step', weight="bold")
    plt.ylabel('Meyer bond order', weight="bold")
    plt.xticks(rotation=90) # Rotate x-axis labels by 90 degrees
    
    # Place the legend outside the plot on the top right corner
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    
    plt.tight_layout() # Adjust layout to make sure everything fits
    plt.savefig(f"bond_valence.png", bbox_inches="tight", format="png", dpi=300)

if __name__ == "__main__":
    try:
        # Check if the CSV file exists
        with open("bond_valence.csv"):
            print("   > CSV file found. Plotting the data.")
            plot_bond_valence()
    except FileNotFoundError:
        print("   > CSV file not found. Running Multiwfn analysis.")
        atom_pairs = [(145, 146), (65, 145), (66, 145), (12, 145), (32, 145), (145, 149)]
        calculate_bond_valence(atom_pairs, 4)
        plot_bond_valence()