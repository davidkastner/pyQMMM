"""Process and analyze output from AMBER GBSA calculation"""

import glob
import pandas as pd
import matplotlib.pyplot as plt
from pandas.api.types import CategoricalDtype


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
    plt.rcParams["xtick.top"] = False
    plt.rcParams["ytick.right"] = False
    plt.rcParams["svg.fonttype"] = "none"


def get_gbsa_df(raw, ignore_residues) -> pd.DataFrame:
    """
    Turn the GBSA file into a parsable pd.DataFrame.

    Parameters
    ----------
    raw: str
        The name of the GBSA output file.

    Returns
    -------
    df: pd.DataFrame
        The raw GBSA file as a pd.DataFrame

    """

    total_energy_keyword = "D,E,L,T,A,S,:"
    sidechain_keyword = "S,i,d,e,c,h,a,i,n, ,E,n,e,r,g,y, ,D,e,c,o,m,p,o,s,i,t,i,o,n,:"
    columns = [
        "Resname 1",
        "Resid 1",
        "Resname 2",
        "Resid 2",
        "Internal",
        "Internal SD",
        "Internal SDM",
        "VDW",
        "VDW SD",
        "VDW SDM",
        "Electrostatic",
        "Electrostatic SD",
        "Electrostatic SDM",
        "Polar",
        "Polar SD",
        "Polar SDM",
        "Non-polar",
        "Non-polar SD",
        "Non-polar SDM",
        "Total",
        "Total SD",
        "Total SDM",
    ]
    csv_file_name = "deltas.csv"

    delta_section = False
    with open(raw, "r") as raw_data, open(csv_file_name, "w") as csv_file:
        for line in raw_data:
            if delta_section:
                if "T,o,t,a,l" in line or "Std" in line or "Resid" in line:
                    if "Resid" in line:
                        csv_file.write(",".join(columns) + "\n")
                    continue
                if sidechain_keyword in line:
                    break
                else:
                    line = ",".join(line.split()) + "\n"
                    csv_file.write(line)

            if line.startswith(total_energy_keyword):
                delta_section = True

    df = pd.read_csv(csv_file_name)
    df = df[~df["Resname 2"].isin(ignore_residues)]
    df = df[df["Resid 1"] != df["Resid 2"]]

    return df


def update_res_names(df) -> pd.DataFrame:
    """
    Updates odd residue names to more conventional names.

    Parameters
    ----------
    df: pd.DataFrame
        The raw GBSA file read in as a DataFrame.

    Returns
    -------
    df: pd.DataFrame
        The GBSA file as a DataFrame with more intuitive residue names.

    """

    res_names = {
        "AG2": "ARG",
        "AN1": "ASN",
        "HIE": "HIS",
        "TR1": "TYR",
        "HD1": "HIS",
        "HD2": "HIS",
        "AP1": "ASP",
        "CL1": "CL",
        "SC1": "SUC",
    }

    df.reset_index(inplace=True)
    df.replace({"Resname 1": res_names, "Resname 2": res_names}, inplace=True)
    df.insert(4, "Residue", df["Resname 2"] + df["Resid 2"].astype(str))

    return df


def get_top_hits_df(df, sub_num, num_hits, sorted_x_labels) -> pd.DataFrame:
    """
    Gets the residues with the greatest energetic contributions.

    The user can specify how many they would like to see.

    Parameters
    ----------
    df: pd.DataFrame
        GBSA DataFrame with the updated residue names
    sub_num: int
        The index of your substrate
    num_hits: int
        The number of top hits that the user would like
    sorted_x_labels: list
        List of residue names sorted by total energy

    Returns
    -------
    df_hits: pd.DataFrame
        The DataFrame sorted only for the residues of interest.

    """
    # Get the top largest contributors to ligand interaction energies
    df_hits = df[df["Resid 1"] == sub_num].nsmallest(num_hits, "Total", keep="all")

    residue_order = CategoricalDtype(sorted_x_labels, ordered=True)
    df_hits["Residue"] = df_hits["Residue"].astype(residue_order)
    df_hits = df_hits.sort_values("Residue")

    df_hits.to_csv("top_hits.csv", index=False)

    return df_hits


def plot_single_total_gbsa(df, file_name) -> None:
    """
    Plot the total GBSA energy scores for each residue.

    Generates a bar plot representing the by-residue total GBSA energy.
    The bar plot is saved as 'gbsa_total.svg' in the current directory.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the residue information and GBSA energies.
    file_name : str
        Name of the file where the plot will be saved.

    """
    colors = "darkgrey"
    ax = df.plot.bar(x="Residue", y="Total", color=colors, figsize=(4, 4))
    ax.set_ylabel("GBSA energy (kcal/mol)", weight="bold")
    ax.set_xlabel("residue", weight="bold")
    plt.savefig(file_name, bbox_inches="tight", transparent=True)
    plt.close()


def plot_clustered_stacked(df, y_columns, sorted_x_labels):
    """
    Plot the GBSA energy by type for a single dataframe.

    This function generates a stacked bar plot representing the GBSA energies.
    for each energy type. The plot is saved as a file in the working directory.

    Parameters
    ----------
    df_hits : pd.DataFrame
        DataFrame containing the residue information and GBSA energies.
    y_columns : list
        List of column names in `df_hits` that represent different components.
    sorted_x_labels : list
        List of residue names in order that they appear on the x-axis.

    """
    format_plot()
    _, axe = plt.subplots(figsize=(4, 4))
    plt.axhline(y=0, color="k", alpha=0.5, linestyle="-", linewidth=3)
    colors = ["#fb8500", "#ffb703", "#023047", "#219ebc", "#8ecae6"]

    residue_order = CategoricalDtype(sorted_x_labels, ordered=True)
    df = df.copy()
    df.loc[:, "Residue"] = df["Residue"].astype(residue_order)
    axe = df.sort_values("Residue").plot.bar(
        x="Residue",
        y=y_columns,
        color=colors,
        linewidth=0,
        stacked=True,
        ax=axe,
        legend=True,
        grid=False,
        width=0.3,
    )

    axe.set_ylabel("GBSA energy (kcal/mol))", weight="bold")
    axe.set_xlabel("residue", weight="bold")
    axe.set_xticks([tick for tick in axe.get_xticks()])

    return axe


def plot_all_gbsa(df_hits, y_columns, sorted_x_labels) -> None:
    """
    Plot the GBSA energy scores by type for a single dataframe.

    Generates a stacked bar plot representing the GBSA component energies.
    The plot is saved as a file in the working directory.

    Parameters
    ----------
    df_hits : pd.DataFrame
        DataFrame containing the residue information and GBSA energies.
    y_columns : list
        List of column names in `df_hits` that represent component energies.
    sorted_x_labels : list
        List of residue names in the order in which they appear on the x-axis.

    """

    series_columns = y_columns + ["Residue"]
    plot_clustered_stacked(
        df_hits[series_columns],
        y_columns,
        sorted_x_labels,
    )
    plt.savefig("stacked_single.svg", bbox_inches="tight", transparent=True)


def analyze() -> None:
    """
    Main GBSA analysis wrapper function for a single dataset.
    """

    print("\n.---------------.")
    print("| GBSA ANALYZER |")
    print(".---------------.\n")
    print("This script will process a single GBSA output file:")
    print("+ Looks for file24.dat\n")

    # Get user input
    sub_num = int(
        input("What is the index of your substrate in your GBSA calculation?: ")
    )
    num_hits = int(input("Show me the top n residues: "))
    ignore_residues = input("What residues would you like ignored (e.g., LS1,LS2)? ").split(',')

    file_extension = "*24.dat"

    # Collect the GBSA data located in the current directory
    raw_files = glob.glob(file_extension)
    raw_files = sorted(raw_files)

    if len(raw_files) == 0:
        print("No *24.dat files found. Please check your directory.")
        return

    raw = raw_files[0]

    # Format plot
    format_plot()

    # Get and process GBSA dataframe
    df = get_gbsa_df(raw, ignore_residues)
    df = update_res_names(df)

    # Generate plots
    df_hits = df[df["Resid 1"] == sub_num].nsmallest(num_hits, "Total", keep="all")
    sorted_x_labels = df_hits["Residue"].tolist()
    df_hits = get_top_hits_df(df, sub_num, num_hits, sorted_x_labels)

    # Plot GBSA Total
    plot_single_total_gbsa(df_hits, "gbsa_total.svg")

    # Plot All GBSA
    plot_all_gbsa(df_hits, ["VDW", "Electrostatic", "Polar", "Non-polar"], sorted_x_labels)


if __name__ == "__main__":
    analyze()
