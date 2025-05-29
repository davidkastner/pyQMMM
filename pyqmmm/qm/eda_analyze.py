import os
import re
import csv
import matplotlib.pyplot as plt

# Conversion factor
kj_to_kcal = 0.239006


def extract_energies(file_path):
    energies = {}
    with open(file_path, "r") as f:
        lines = f.readlines()

        # Extract energies from the "Decomposition of frozen interaction energy" section
        for idx, line in enumerate(lines):
            if "Decomposition of frozen interaction energy" in line:
                try:
                    energies["Electrostatics"] = (
                        float(
                            re.search(
                                r"E_cls_elec\(solv\)\s+\(kJ/mol\) = ([-+]?[\d.]+)",
                                lines[idx + 11],
                            ).group(1)
                        )
                        * kj_to_kcal
                    )
                except AttributeError:
                    print(
                        f"Couldn't find Electrostatics energy in {file_path}. Line content: {lines[idx+11]}"
                    )
                    energies["Electrostatics"] = 0

                try:
                    energies["Repulsion"] = (
                        float(
                            re.search(
                                r"E_mod_pauli\s+\(MOD PAULI\) \(kJ/mol\) = ([-+]?[\d.]+)",
                                lines[idx + 6],
                            ).group(1)
                        )
                        * kj_to_kcal
                    )
                except AttributeError:
                    print(
                        f"Couldn't find Repulsion energy in {file_path}. Line content: {lines[idx+6]}"
                    )
                    energies["Repulsion"] = 0

                try:
                    energies["Dispersion"] = (
                        float(
                            re.search(
                                r"E_cls_disp\s+\(CLS DISP\)\s+\(kJ/mol\) = ([-+]?[\d.]+)",
                                lines[idx + 7],
                            ).group(1)
                        )
                        * kj_to_kcal
                    )
                except AttributeError:
                    print(
                        f"Couldn't find Dispersion energy in {file_path}. Line content: {lines[idx+7]}"
                    )
                    energies["Dispersion"] = 0

            if "Simplified EDA Summary (kJ/mol)" in line:
                try:
                    energies["SOLVATION"] = (
                        float(
                            re.search(
                                r"SOLVATION\s+([-+]?[\d.]+)", lines[idx + 3]
                            ).group(1)
                        )
                        * kj_to_kcal
                    )
                except AttributeError:
                    print(
                        f"Couldn't find SOLVATION energy in {file_path}. Line content: {lines[idx+3]}"
                    )
                    energies["SOLVATION"] = 0

                try:
                    energies["POLARIZATION"] = (
                        float(
                            re.search(
                                r"POLARIZATION\s+([-+]?[\d.]+)", lines[idx + 6]
                            ).group(1)
                        )
                        * kj_to_kcal
                    )
                except AttributeError:
                    print(
                        f"Couldn't find POLARIZATION energy in {file_path}. Line content: {lines[idx+6]}"
                    )
                    energies["POLARIZATION"] = 0

                try:
                    energies["CHARGE TRANSFER"] = (
                        float(
                            re.search(
                                r"CHARGE TRANSFER\s+([-+]?[\d.]+)", lines[idx + 7]
                            ).group(1)
                        )
                        * kj_to_kcal
                    )
                except AttributeError:
                    print(
                        f"Couldn't find CHARGE TRANSFER energy in {file_path}. Line content: {lines[idx+7]}"
                    )
                    energies["CHARGE TRANSFER"] = 0

    return energies


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


def main():
    # Ask for residue name from user
    residue_name = input("What residue is this for (e.g., His12)? ")

    # Collecting all folder names in the current directory and sorting based on the prefix number
    folder_names = sorted(
        [folder for folder in os.listdir() if os.path.isdir(folder)],
        key=lambda x: int(x.split("_")[0]),
    )

    # Lists to store results
    intermediates = []
    solvation_energies = []
    electrostatics_energies = []
    repulsion_energies = []
    dispersion_energies = []
    polarization_energies = []
    charge_transfer_energies = []

    for folder in folder_names:
        intermediate_name = folder.split("_")[1]
        intermediates.append(intermediate_name)

        # Find the desired .out file in the folder
        file_name = [
            file
            for file in os.listdir(folder)
            if "qmscript" in file and file.endswith(".out")
        ]
        if not file_name:
            print(f"No matching .out file found in folder {folder}. Skipping...")
            continue

        file_path = os.path.join(folder, file_name[0])

        # Extract energies
        energies = extract_energies(file_path)

        solvation_energies.append(energies.get("SOLVATION", 0))
        electrostatics_energies.append(energies.get("Electrostatics", 0))
        repulsion_energies.append(energies.get("Repulsion", 0))
        dispersion_energies.append(energies.get("Dispersion", 0))
        polarization_energies.append(energies.get("POLARIZATION", 0))
        charge_transfer_energies.append(energies.get("CHARGE TRANSFER", 0))

    # Plotting
    format_plot()
    plt.figure(figsize=(6, 5))
    # plt.plot(
    #     intermediates, solvation_energies, marker="o", label="solvation", color="b"
    # )
    plt.plot(
        intermediates,
        electrostatics_energies,
        marker="o",
        label="electrostatics",
        color="orange",
    )
    plt.plot(
        intermediates, repulsion_energies, marker="o", label="repulsion", color="r"
    )
    plt.plot(
        intermediates, dispersion_energies, marker="o", label="dispersion", color="b"
    )
    plt.plot(
        intermediates,
        polarization_energies,
        marker="o",
        label="polarization",
        color="g",
    )
    plt.plot(
        intermediates,
        charge_transfer_energies,
        marker="o",
        label="charge transfer",
        color="purple",
    )
    plt.xlabel("intermediates", weight="bold")
    plt.ylabel(f"{residue_name} energy (kcal/mol)", weight="bold")
    plt.legend(
        bbox_to_anchor=(1.04, 0.8), loc="center left", borderaxespad=0, frameon=False
    )
    plt.xticks(rotation=90)

    # Save figures
    plt.savefig(f"ALMO-EDA_{residue_name}.png", bbox_inches="tight", dpi=300)
    plt.savefig(f"ALMO-EDA_{residue_name}.svg", bbox_inches="tight")

    # Writing to CSV
    with open("EDA_results.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "intermediate",
                "solvation",
                "electrostatics",
                "repulsion",
                "dispersion",
                "polarization",
                "charge transfer",
            ]
        )
        for i in range(len(intermediates)):
            writer.writerow(
                [
                    intermediates[i],
                    solvation_energies[i],
                    electrostatics_energies[i],
                    repulsion_energies[i],
                    dispersion_energies[i],
                    polarization_energies[i],
                    charge_transfer_energies[i],
                ]
            )


if __name__ == "__main__":
    main()
