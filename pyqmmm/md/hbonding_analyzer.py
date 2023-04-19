"""Analyze data from hydrogen bonding analysis based on hbond.gnu file."""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys

def bond_labels(file_path, ignore_backbone=True, include_backbone=tuple("DHK")):
    """
    Extracts bond labels from gnu file.

    Parameters
    ----------
    file_path: str
        Path to hbond.gnu file
    ignore_backbone: bool
        Whether to ignore backbone hydrogen bonds (donor/acceptor named N or O)
    include_backbone: tuple(str)
        If ignore_backbone, these residues are the exception

    Returns
    -------
    grouped: pd.DataFrame
        DataFrame containing residue pair and interaction index
    """

    dict = {}
    with open(file_path, 'r') as f:
        for line in f:
            if line[:10] == 'set ytics(':
                bonds = line.split('(')[1].split(')')[0]
                for b in bonds.split(','):
                    key_val = b.split(' ')
                    dict[int(float(key_val[-1]))] = key_val[0].strip('"')
    labels = pd.Series(dict.values(), index=dict.keys(), name='labels')
    labels = labels.str.split('-', expand=True)
    labels.columns = ['acceptor', 'donor', 'hydrogen']
    labels[['acceptor', 'acceptor_atom']] = labels['acceptor'].str.split('@', expand=True)
    labels[['donor', 'donor_atom']] = labels['donor'].str.split('@', expand=True)
    # Ignore backbone hydrogen atom donors/acceptors if the acceptor or donor is not in include_backbone
    if ignore_backbone:
        include_regex = '|'.join(include_backbone)
        labels = labels[~(
            (labels['acceptor_atom'].isin(['N', 'O']) & ~labels['acceptor'].str.contains(include_regex, regex=True)) |
            (labels['donor_atom'].isin(['N', 'O']) & ~labels['donor'].str.contains(include_regex, regex=True))
        )]
    labels = labels.reset_index()
    grouped = labels.groupby(['acceptor', 'donor'])['index'].apply(set).reset_index()

    return grouped


def count_occurrences(file_path, labels):
    """
    Counts percent occurrences of each hydrogen bond.

    Parameters
    ----------
    file_path: str
        Path to hbond.gnu file
    labels: str
        Hbond labels as outputted by CPPTRAJ in gnu format

    Returns
    -------
    labels: DataFrame containing residue pair and interaction index
    frame_count: total number of frames in trajectory
    """

    labels['count'] = 0
    frame_count = 0
    with open(file_path, 'r') as f:
        for _ in range(8):
            next(f)
        for frame in f.read().split('\n\n'):
            frame_count += 1
            bonds = set()
            for line in frame.split('\n'):
                if line == 'end':
                    break
                arr = [int(float(x)) for x in line.split(' ') if x]
                if arr[-1] == 1:
                    bonds.add(arr[1])
            contains_bond = [len(i & bonds) != 0 for i in labels['index']]
            labels.loc[contains_bond, 'count'] += 1
    return labels, frame_count


def process_data(count_df, frame_count, name, substrate):
    """
    Cleans up hbonding data (formats residue names, dataframe index, etc.)

    Parameters
    ----------
    count_df: pd.DataFrame
        DataFrame containing the hydrogen bonding counts
    frame_count: int
        Number of frames in trajectory
    name: str
        System name

    Returns
    -------
    count_df: pd.DataFrame
        Cleaned DataFrame containing the hydrogen bonding counts


    """
    increment = 0 # Is there an offset between the res number and the real res number
    res_ser = pd.concat([count_df['acceptor'], count_df['donor']], axis=0)
    count_df['residue'] = res_ser[~res_ser.str.contains(substrate)].sort_index()
    count_df['percent_occurrence'] = count_df['count'] / frame_count
    count_df[['residue', 'position']] = count_df['residue'].str.split('_', expand=True)
    count_df['position'] = count_df['position'].astype(int) + increment
    format_residues_dict = {'ALA': 'A',
                            'ARG': 'R',
                            'ASN': 'N',
                            'AP1': 'D',
                            'ASP': 'D',
                            'CYS': 'C',
                            'FE1': 'FE',
                            'GLU': 'E',
                            'GLN': 'Q',
                            'GLY': 'G',
                            'HID': 'H',
                            'HIS': 'H',
                            'HIP': 'H',
                            'HIE': 'H',
                            'HD1': 'H',
                            'HD2': 'H',
                            'ILE': 'I',
                            'LEU': 'L',
                            'LYS': 'K',
                            'MET': 'M',
                            'OO1': 'OXO',
                            'PHE': 'F',
                            'PRO': 'P',
                            'SER': 'S',
                            'SC1': 'SUC',
                            'THR': 'T',
                            'TRP': 'W',
                            'TYR': 'Y',
                            'VAL': 'V',
                            '_': ''
                            }
    for old, new in format_residues_dict.items():
        count_df['residue'] = count_df['residue'].str.replace(old, new, regex=False)
    count_df['residue'] = count_df['residue'] + count_df['position'].astype(str)
    count_df = count_df.rename(columns={'percent_occurrence': name})[['residue', name, 'position']]
    count_df = count_df.set_index('residue')
    count_df[name] = count_df[name] * 100
    return count_df


def figure_formatting():
    """
    Sets formatting for matplotlib.

    """
    font = {"family": "sans-serif", "weight": "bold", "size": 14}
    plt.rc("font", **font)
    plt.rcParams["svg.fonttype"] = "none"
    plt.rcParams["axes.linewidth"] = 2.5
    plt.rcParams["xtick.major.size"] = 10
    plt.rcParams["xtick.major.width"] = 2.5
    plt.rcParams["ytick.major.size"] = 10
    plt.rcParams["ytick.major.width"] = 2.5
    plt.rcParams["xtick.direction"] = "in"
    plt.rcParams["ytick.direction"] = "in"
    plt.rcParams["mathtext.default"] = "regular"


def plot(data, file_path):
    """
    Plot single figure for hbonding analysis.

    Parameters
    ----------
    data: pd.DataFrame
        Data that will be used to plot the figure
    file_path: str
        Path to directory where output image should go

    """
    figure_formatting()
    df = data.sort_values('position').drop(['position'], axis=1)
    df = df[df.ge(0.1).all(axis=1)] # 10% occurence cutoff
    ax = df.plot.bar(color=["Black"])
    ax.set_ylabel("occurrence (%)", weight="bold")
    ax.set_xlabel("residue", weight="bold")
    ax.legend().set_visible(False)
    ax.tick_params(axis='x', labelrotation=90)
    plt.savefig(file_path + 'hbond.png', bbox_inches="tight", transparent=False, dpi=600)


def plot_multi(data, file_path):
    """
    Plot hbonding comparison between two trajectories.

    Parameters
    ----------
    data: list of two dataframes
    file_path: path to directory where output image should go

    """
    figure_formatting()
    new_df = pd.merge(data[0], data[1], on=['residue', 'position'], how='inner').sort_index().sort_values('position')
    new_df = new_df.dropna(axis=0).drop(['position'], axis=1)
    new_df = new_df[new_df.ge(0.1).all(axis=1)] # 10% ocurrence cutoff
    ax = new_df.plot.bar(color=["Blue", "Red", "Orange"])
    ax.set_ylabel("occurrence (%)", weight="bold")
    ax.set_xlabel("residue", weight="bold")
    ax.legend(bbox_to_anchor=(1.34, 1.02), frameon=False)
    ax.tick_params(axis='x', labelrotation=90)
    plt.savefig(file_path + 'hbond_comparison.png', bbox_inches="tight", transparent=False, dpi=600)


def analyze_hbonds(file_paths, names, substrate):
    """
    Driver for analyzing hbonds from hbond.gnu file

    Parameters
    ----------
    file_paths: list[str]
        A list of paths to hbond.gnu files
    names: list[str]
        A list of names of each hbond.gnu files
    """
    data = []
    for file_path, name in zip(file_paths, names):
        data_path = Path(file_path + 'hbond.csv')
        if data_path.is_file():
            print(f"{data_path} already exists")
            d = pd.read_csv(file_path + 'hbond.csv')
            d = d.set_index('residue')
        else:
            path = file_path + 'hbond.gnu'
            print(f"Processing: {path}")
            label_df = bond_labels(path)
            count_df, frame_count = count_occurrences(path, label_df)
            d = process_data(count_df, frame_count, name, substrate)
            d.to_csv(file_path + 'hbond.csv')
        plot(d, file_path)
        data.append(d)

    plot_multi(data, file_paths[0])


if __name__ == "__main__":
    """
    First argument contains [data_file1, data_file2] -- two directories containing hbond.gnu files
    --> this will also be the output directories
    Second argument contains [name1, name2] -- names corresponding to the hbond.gnu files (e.g., H127A, Wild-type)
    """

    analyze_hbonds(["/Users/kastner/Downloads/test/obtuse/", "/Users/kastner/Downloads/test/acute/"], ["acute", "obtuse"], "DHK")