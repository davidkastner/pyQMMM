import os
import csv

def get_directories():
    """Get a sorted list of directories in the current working directory."""
    return sorted([d for d in os.listdir() if os.path.isdir(d)])

def parse_orca_out(file_path):
    """Extract the last instances of 'Final Gibbs free energy' and 'G-E(el)' from a file."""
    gibbs_energy = None
    gibbs_correction = None
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith("Final Gibbs free energy"):
                    gibbs_energy = line.split()[5]
                elif line.startswith("G-E(el)"):
                    gibbs_correction = line.split()[2]
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except IndexError:
        print(f"Malformed line in file: {file_path}")

    return gibbs_energy, gibbs_correction

def extract():
    """Main function to extract Gibbs free energies and corrections from ORCA output files."""
    output_csv = "gibbs_energies.csv"
    directories = get_directories()
    energy_data = []

    for directory in directories:
        orca_out_path = os.path.join(directory, "orca.out")
        gibbs_energy, gibbs_correction = parse_orca_out(orca_out_path)

        if gibbs_energy and gibbs_correction:
            energy_data.append({
                "Directory": directory,
                "Gibbs Free Energy": gibbs_energy,
                "Gibbs Free Energy Correction": gibbs_correction
            })
        else:
            print(f"Missing data in {orca_out_path}, skipping.")

    write_to_csv(output_csv, energy_data)
    print(f"Gibbs free energies and corrections have been extracted and saved to '{output_csv}'.")

def write_to_csv(output_file, data):
    """Write energy data to a CSV file."""
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ["Directory", "Gibbs Free Energy", "Gibbs Free Energy Correction"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    extract()
