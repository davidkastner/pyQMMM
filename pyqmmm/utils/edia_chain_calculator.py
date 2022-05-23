# Docs: https://pyqmmm.readthedocs.io/en/latest/
# DESCRIPTION
#     The output for EDIA is only for individual residues or atoms
#     This script takes EDIA output and cacluates the average chain EDIA scores

#     Author: David Kastner
#     Massachusetts Institute of Technology
#     kastner (at) mit . edu


# Import packages and dependencies
import numpy as numpy
import matplotlib.pyplot as plt
import pandas as pd

# Get user input
csv = input("Name of your EDIA CSV file without extension?: ")
chains = input('Chains to compare (e.g., "ABCD")? ')
residues = input('Key residues of interest (e.g., "9,23,134" or "none"): ')

# Open CSV file into pandas dataframe
df = pd.read_csv("{}.csv".format(csv))
df_all = df[["Chain", "EDIAm", "Median EDIA"]]

# Examine user chains input and return errors
chains = chains.upper()
chain_list = []
for chain in chains:
    if chain in df_all.Chain.values:
        print("Chain {} found.".format(chain))
        chain_list.append(chain)
    else:
        print("Chain {} not found.".format(chain))
print("-------------------")
print()

# Create empty dataframe to store means
df_means = pd.DataFrame(
    index=[chain for chain in chain_list], columns=["EDIAm", "EDIA"]
)
# Create empty dataframe to store standard error
df_se = pd.DataFrame(index=[chain for chain in chain_list], columns=["EDIAm", "EDIA"])

# Calculate the Avg. EDIAm, Avg. EDIA, and Std. Error
for chain in chain_list:
    # Isolate a specific chain
    isolated_chain = df_all.loc[df["Chain"] == chain]

    # Get the mean for EDIAm and EDIA
    avg_ediam = isolated_chain["EDIAm"].mean()
    avg_edia = isolated_chain["Median EDIA"].mean()
    # Store it in the df_means dataframe
    df_means.loc[chain] = [avg_ediam, avg_edia]

    # Get the standard error for EDIAm and EDIA
    std_err_ediam = isolated_chain["EDIAm"].sem()
    std_err_edia = isolated_chain["Median EDIA"].sem()
    # Store it in the df_means dataframe
    df_se.loc[chain] = [std_err_ediam, std_err_edia]

# Rank order the chains by EDIA score
sorted_df = df_means.sort_values(by="EDIA", ascending=False)
print("Your sorted results for all residues:")
print(sorted_df)
print("-------------------")
print()

# Plot the findings
# Plot constants
colors = ["#ff16ea", "#020cfa"]
label = chain_list

# Plot parameters
plt.rc("axes", linewidth=2.5)
fig, ax = plt.subplots()
df_means.plot.bar(yerr=df_se, ax=ax, capsize=4, rot=0, color=colors)
plt.title("Chain Comparison", fontsize=18)
plt.ylabel("EDIA Score", fontsize=16)
plt.xlabel("Chains", fontsize=16)
plt.xticks(rotation=0)
plt.tick_params(labelsize=14)
plt.legend(fontsize=12, loc="lower right")
plt.savefig("chain_comparison.pdf", bbox_inches="tight")
print("Figure has been created.")
print("-------------------")
print()

# Select out key columns
df_res = df[["ID", "Chain", "EDIAm", "Median EDIA"]]

# Examine user residue input and return errors
if residues != "none":
    residue_split = residues.split(",")
    residue_split = [int(i) for i in residue_split]
    residue_list = []
    for residue in residue_split:
        if residue in df_res.ID.values:
            print("Residue {} found.".format(residue))
            residue_list.append(residue)
        else:
            print("Residue {} not found.".format(residue))
print("-------------------")

# Select only residues the user asked for
df_sel_res = df_res[df_res.ID.isin(residue_list)]
for residue in residue_list:
    isolated_residue = df_sel_res.loc[df_sel_res["ID"] == residue]
    chains_present = isolated_residue["Chain"].values
    for chain in chain_list:
        if chain not in chains_present:
            df_row = {"ID": residue, "Chain": chain, "EDIAm": 0, "Median EDIA": 0}
            df_sel_res = df_sel_res.append(df_row, ignore_index=True)

# Create empty dataframe to store means
df_res_means = pd.DataFrame(index=chain_list, columns=["EDIAm", "EDIA"])

# Create empty dataframe to store standard error
df_res_se = pd.DataFrame(index=chain_list, columns=["EDIAm", "EDIA"])

# Calculate the Avg. EDIAm, Avg. EDIA, and Std. Error
for chain in chain_list:
    # Isolate a specific chain
    isolated_residue = df_sel_res.loc[df_sel_res["Chain"] == chain]

    # Get the mean for EDIAm and EDIA
    avg_res_ediam = isolated_residue["EDIAm"].mean()
    avg_res_edia = isolated_residue["Median EDIA"].mean()
    # Store it in the df_means dataframe
    df_res_means.loc[chain] = [avg_res_ediam, avg_res_edia]

    # Get the standard error for EDIAm and EDIA
    std_err_res_ediam = isolated_residue["EDIAm"].sem()
    std_err_res_edia = isolated_residue["Median EDIA"].sem()
    # Store it in the df_means dataframe
    df_res_se.loc[chain] = [std_err_res_ediam, std_err_res_edia]


def edia_chain_calculator():
    # Rank order the chains by EDIA score
    sorted_res_df = df_res_means.sort_values(by="EDIA", ascending=False)
    print("Your sorted results for specific residues:")
    print(sorted_res_df)
    print("-------------------")
    print()

    # Plot the findings
    plt.rc("axes", linewidth=2.5)
    fig, ax = plt.subplots()
    df_res_means.plot.bar(yerr=df_res_se, ax=ax, capsize=4, rot=0, color=colors)
    plt.title("Chain Comparison for Select Residues", fontsize=18)
    plt.ylabel("EDIA Score", fontsize=16)
    plt.xlabel("Chains", fontsize=16)
    plt.xticks(rotation=0)
    plt.tick_params(labelsize=14)
    plt.legend(fontsize=12, loc="lower right")
    plt.savefig("chain_res_comp.pdf", bbox_inches="tight")
    print("Figure has been created.")
    print("-------------------")


if __name__ == "__main__":
    edia_chain_calculator()
