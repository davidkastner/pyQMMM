import re

def create_neb_mep_trj_from_out():
    # Define the file paths
    orca_output_file = 'orca.out'
    output_xyz_file = 'qmscript_MEP_trj.xyz'

    # Define regex patterns for extracting data
    # Adjusted to handle one-letter and two-letter element symbols
    coordinate_pattern = re.compile(r'(REACTANT|PRODUCT|IMAGE \d+ \((ANGSTROEM|BOHR)\))\n-+\n((?:[A-Z][a-z]?\s+-?\d+\.\d+\s+-?\d+\.\d+\s+-?\d+\.\d+\s*\n)+)')
    energy_pattern = re.compile(r'\s+\d+\s+\S+\s+(-?\d+\.\d+)')

    # Read the ORCA output file
    with open(orca_output_file, 'r') as file:
        orca_output = file.read()

    # Extract coordinates and energies
    coordinates = coordinate_pattern.findall(orca_output)
    path_summary_snippet = orca_output.split('PATH SUMMARY')[1].split('---------------------------------------------------------------')[1].strip()
    energies = energy_pattern.findall(path_summary_snippet)

    # Adjust coordinates list to include REACTANT and PRODUCT properly
    coordinates = [('REACTANT', coordinates[0][1], coordinates[0][2])] + coordinates + [('PRODUCT', coordinates[-1][1], coordinates[-1][2])]

    # Ensure the number of coordinates and energies match
    assert len(coordinates) == len(energies), "Mismatch between number of coordinates and energies."

    # Write the extracted data to the new XYZ file
    with open(output_xyz_file, 'w') as file:
        for i, (coord_type, unit, coord_data) in enumerate(coordinates):
            lines = coord_data.strip().split('\n')
            num_atoms = len(lines)
            energy = energies[i]
            title_line = f"Coordinates from ORCA-job qmscript_MEP E {energy}"
            
            file.write(f"{num_atoms}\n")
            file.write(f"{title_line}\n")
            for line in lines:
                file.write(line + '\n')

    output_xyz_file
