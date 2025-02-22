import os
import csv

def get_directories():
    """Get a sorted list of directories in the current working directory."""
    return sorted([d for d in os.listdir() if os.path.isdir(d)])

def parse_final_energy(file_path):
    """Extract the last 'FINAL SINGLE POINT ENERGY' from the specified file."""
    last_energy = None
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith("FINAL SINGLE POINT ENERGY"):
                    last_energy = line.split()[4]  # Update to the last occurrence
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except IndexError:
        print(f"Malformed line in file: {file_path}")

    return last_energy

def extract():
    """Main function to extract electronic energies from ORCA output files."""
    output_csv = "energies.csv"
    directories = get_directories()
    energy_data = []

    for directory in directories:
        orca_out_path = os.path.join(directory, "orca.out")
        last_energy = parse_final_energy(orca_out_path)

        if last_energy is not None:
            energy_data.append({
                "Directory": directory,
                "Energy": last_energy
            })
        else:
            print(f"No valid energy data in {orca_out_path}, skipping.")

    write_to_csv(output_csv, energy_data)
    print(f"Electronic energies have been extracted and saved to '{output_csv}'.")

def write_to_csv(output_file, data):
    """Write energy data to a CSV file."""
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ["Directory", "Energy"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    extract()
