"""Process and analyze output from AMBER GBSA calculation"""

import glob
import pandas as pd
import matplotlib.pyplot as plt
from pandas.api.types import CategoricalDtype


def get_gbsa_df(raw) -> pd.DataFrame:
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


def get_top_hits_df(df, sub_num, num_hits) -> pd.DataFrame:
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
    
    Returns
    -------
    df_hits: pd.DataFrame
        The DataFrame sorted only for the residues of interest.

    """
    # Get the top largest contributors to ligand interaction energies
    df_hits = df[df["Resid 1"] == sub_num].nsmallest(num_hits, "Total", keep="all")
    df_hits.to_csv("top_hits.csv", index=False)

    return df_hits


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


def plot_single_total_gbsa(df, file_name) -> None:
    """
    Plot the total GBSA energy scores.

    """
    plt.figure()  # Add this line
    colors = "#8ecae6"
    ax = df.plot.bar(x="Residue", y="Total", color=colors)
    format_plot()
    ax.set_ylabel("GBSA energy score", weight="bold")
    ax.set_xlabel("Residue", weight="bold")
    plt.savefig(file_name, bbox_inches="tight", transparent=True)
    plt.close()


def plot_clustered_stacked(dataframes, labels, y_columns, sorted_x_labels):
    """
    Format the stacked bar plots.

    """

    H = "//"
    plt.axhline(y=0, color="k", alpha=0.5, linestyle="-", linewidth=3)
    colors = ["#fb8500", "#ffb703", "#023047", "#219ebc", "#8ecae6"]
    number_of_df = len(dataframes)
    number_of_col = len(dataframes[0].columns)
    axe = plt.subplot(111)
    position = -1.15

    for df in dataframes:  # for each data frame
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
            legend=False,
            grid=False,
            width=0.3,
            position=position,
        )
        position -= 1
        format_plot()

    (
        handles,
        axe_labels,
    ) = axe.get_legend_handles_labels()  # get the handles we want to modify
    for i in range(
        0, number_of_df * number_of_col, number_of_col
    ):  # len(h) = n_col * n_df
        sliced_handles = (
            handles[i : i + number_of_col]
            if i == 0
            else handles[i - 1 : i + number_of_col]
        )
        for j, pa in enumerate(sliced_handles):
            for rect in pa.patches:  # for each index
                rect.set_hatch(H * int(i / number_of_col))  # edited part

    # Add invisible data to add another legend
    n = []
    for i in range(number_of_df):
        n.append(axe.bar(0, 0, color="gray", hatch=H * i))

    l1 = axe.legend(
        handles[:number_of_col], list(axe_labels[: number_of_col - 1]), loc=[1.01, 0.5]
    )

    axe.add_artist(l1)
    axe.set_ylabel("GBSA energy score", weight="bold")
    axe.set_xlabel("Residue", weight="bold")
    axe.set_xticks([tick + 0.65 for tick in axe.get_xticks()])

    return axe


def plot_multi_all_gbsa(df_hits_list, df_list, y_columns, sorted_x_labels) -> None:
    """
    Plot the GBSA energy scores by type for multiple dataframes.

    """

    gbsa1_df_hits, gbsa2_df_hits, series_columns = prep_multi_gbsa_data(
        df_hits_list, df_list, y_columns
    )
    plot_clustered_stacked(
        [gbsa1_df_hits[series_columns], gbsa2_df_hits[series_columns]],
        ["gbsa1", "gbsa2"],
        y_columns,
        sorted_x_labels
    )
    plt.savefig("stacked_multi_1.pdf", bbox_inches="tight", transparent=True)


def prep_multi_gbsa_data(df_hits_list, df_list, y_columns):
    """
    Prepare the data for plotting the GBSA energy scores by type for multiple dataframes.
    
    """
    gbsa1_df_hits = df_hits_list[0]
    gbsa2_df_hits = df_hits_list[1]
    gbsa1_df = df_list[0]
    gbsa2_df = df_list[1]
    gbsa1_residues = gbsa1_df_hits["Residue"].tolist()
    gbsa2_residues = gbsa2_df_hits["Residue"].tolist()
    residues = list(set(gbsa1_residues + gbsa2_residues))

    for residue in residues:
        if residue not in gbsa1_residues and residue in gbsa2_residues:
            residue_index = gbsa2_df_hits.loc[gbsa2_df_hits["Residue"] == residue][
                "index"
            ].tolist()[0]
            missing_residue = gbsa1_df.loc[gbsa1_df["index"] == residue_index]
            gbsa1_df_hits = pd.concat([gbsa1_df_hits, missing_residue], ignore_index=True)
        elif residue not in gbsa2_residues and residue in gbsa1_residues:
            residue_index = gbsa1_df_hits.loc[gbsa1_df_hits["Residue"] == residue][
                "index"
            ].tolist()[0]
            missing_residue = gbsa2_df.loc[gbsa2_df["index"] == residue_index]
            gbsa2_df_hits = pd.concat([gbsa2_df_hits, missing_residue], ignore_index=True)

    format_plot()
    series_columns = y_columns + ["Residue"]

    return gbsa1_df_hits, gbsa2_df_hits, series_columns


def plot_multi_total_gbsa(df_hits_list, df_list, y_columns) -> list:
    """
    Create the GBSA plot.

    Parameters
    ----------
    df_hits_list: pd.DataFrame

    df_list: pd.DataFrame

    y_columns:


    Returns
    -------
    sorted_x_labels: list

    """

    gbsa1_df_hits, gbsa2_df_hits, series_columns = prep_multi_gbsa_data(
        df_hits_list, df_list, y_columns
    )
    gbsa1_series = gbsa1_df_hits[series_columns].set_index("Residue").squeeze()
    gbsa2_series = gbsa2_df_hits[series_columns].set_index("Residue").squeeze()
    format_plot()
    new_df = pd.DataFrame({"gbsa1": gbsa1_series, "gbsa2": gbsa2_series})
    new_df = new_df.sort_values(by=["gbsa1"])
    sorted_x_labels = list(new_df.index)
    plt.figure()  # Add this line
    ax = new_df.plot.bar(color=["SkyBlue", "IndianRed"])
    ax.set_ylabel("GBSA energy score", weight="bold")
    ax.set_xlabel("Residue", weight="bold")

    plt.savefig("stacked_multi_2.pdf", bbox_inches="tight", transparent=True)
    plt.close()

    return sorted_x_labels


def analyze() -> None:
    '''
    Main GBSA analysis wrapper function.
    '''

    # Welcome user and print some instructions
    print("\n.---------------.")
    print("| GBSA ANALYZER |")
    print(".---------------.\n")
    print("This script will process GBSA output files:")
    print("+ Looks for file24.dat")
    print("+ Will look for more than one GBSA output to compare\n")

    # Get user input
    sub_num = int(input("What is the index of your substrate in your GBSA calculation?: "))
    num_hits = int(input('Show me the top n residues: '))

    file_extension = "*24.dat"
    plot_file_names = [["gbsa1_total.pdf", "gbsa1_all.pdf"], ["gbsa2_total.pdf", "gbsa2_all.pdf"]]

    # Collect all the GBSA data located in the current directory
    raw_files = glob.glob(file_extension)
    raw_files = sorted(raw_files)

    df_list = []
    df_hits_list = []

    # Loop through each GBSA file and analyze the results
    for raw, file_name_list in zip(raw_files, plot_file_names):
        df = get_gbsa_df(raw)

        df = update_res_names(df)
        df_hits = get_top_hits_df(df, sub_num, num_hits)

        df_list.append(df)
        df_hits_list.append(df_hits)

        # Generate a plots
        plot_single_total_gbsa(df_hits, file_name_list[0])

        # If there is only one file matching "*24.dat", do not generate the other plots
        if len(raw_files) == 1:
            break

    # Generate multi GBSA plots if there are more than one file
    if len(raw_files) > 1:
        sorted_x_labels = plot_multi_total_gbsa(df_hits_list, df_list, ["Total"])
        plot_multi_all_gbsa(df_hits_list, df_list, ["VDW", "Electrostatic", "Polar", "Non-polar"], sorted_x_labels)

if __name__ == "__main__":
    analyze()

if __name__ == "__main__":
    analyze()