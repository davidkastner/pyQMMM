"""This script will find all frames in the main cluster and condense them."""


def get_clusters(file):
    """
    Opens the CPPTraj cnumvtime.dat file,
    which contains every frame and its assigned cluster.
    Creates a list containing the indices of all frames in cluster 0,
    which will always be the predominant cluster.

    Parameters
    ----------
    file : str
        The file containing the cluster assignments for every frame.

    Returns
    -------
    cluster_list : list
        A list of all the frame indices from cluster 0.
    """
    cluster_list = []
    with open(file, "r") as cluster_file:
        # Skip first line as it is just text
        next(cluster_file)
        for line in cluster_file:
            frame_num = int(line.split()[0])
            cluster_num = int(line.split()[1])
            if cluster_num == 0:
                cluster_list.append(frame_num)
    return cluster_list


def condense_numbering(cluster_list):
    seq = []
    final = []
    last = 0

    for index, val in enumerate(cluster_list):
        if last + 1 == val or index == 0:
            seq.append(val)
            last = val
        else:
            if len(seq) > 1:
                final.append(str(seq[0]) + "-" + str(seq[len(seq) - 1]))
            else:
                final.append(str(seq[0]))
            seq = []
            seq.append(val)
            last = val

        if index == len(cluster_list) - 1:
            if len(seq) > 1:
                final.append(str(seq[0]) + "-" + str(seq[len(seq) - 1]))
            else:
                final.append(str(seq[0]))

    final_selection = ",".join(map(str, final))
    return final_selection


def main():
    """
    Condenses the frame indices of a clustered MD run into a single string.

    Examples
    --------
    Run the following to generate the CPPTraj output first

    >> parm welo5_solv.prmtop
    >> trajin constP_prod.mdcrd
    >> trajout output.mdcrd onlyframes 2,5-200,202-400

    """

    # Provide the user with general info about this utility
    print("\n.-----------------------.")
    print("| CLUSTER FRAME INDEXER |")
    print(".-----------------------.\n")
    print("Run this script in the same directory as cnumvtime.dat.")
    print("The script prints the frame indices.\n")
    print("It will also provide an interval if you want only a subset.\n")

    # This is the standard name but feel free to change it if yours is different
    cluster_definitions_file = "cnumvtime.dat"
    cluster_list = get_clusters(cluster_definitions_file)
    final_selection = condense_numbering(cluster_list)

    # Important output for the user
    print(f"   > Total frames: {len(cluster_list)}")
    print(f"   > Final selection: {final_selection}")


if __name__ == "__main__":
    main()
