"""Collects the energies into a CSV file as a pandas dataframe."""

import glob
import plotly.graph_objs as go
from plotly.offline import iplot


def get_opt_energies(file_path):
    """
    Loop through the file, collect optimized energies.

    Parameters
    ----------

    Returns
    -------
    energy_df : dataframe
        The optimized energy from the current convergence line of the file.
    energy_list : list
        Returns a list of the energies extracted from the .out file.
    """
    energy_list = []
    opt_iter = 1
    with open(file_path, "r") as out_file:
        with open(
            "./opt_energies_{}.dat".format(file_path[9]), "w"
        ) as opt_energies_file:
            first_energy = None
            for line in out_file:
                if line[6:22] == "Optimized Energy":
                    energy = float(line[26:42])
                    if first_energy is None:
                        first_energy = energy
                    if opt_iter > 20:
                        relative_energy = (energy - first_energy) * 627.5
                        energy_list.append(relative_energy)
                    else:
                        relative_energy = (energy - first_energy) * 627.5
                        energy_list.append(relative_energy)
                    opt_energy_line = "{} {}\n".format(opt_iter, relative_energy)
                    opt_energies_file.write(opt_energy_line)
                    opt_iter += 1
                else:
                    continue
    return energy_list


def get_final_energies(file_path):
    """
    Loop through the file, collect final energies.

    Returns
    -------
    energy_df : dataframe
        The optimized energy from the current convergence line of the file.
    energy_list : list
        Returns a list of the energies extracted from the .out file.
    """
    energy_list = []
    conv_iter = 1
    with open(file_path, "r") as out_file:
        with open("./final_energies.csv", "w") as opt_energies_file:
            first_energy = None
            for line in out_file:
                if line[0:14] == "FINAL ENERGY: ":
                    energy = float(line[14:30])
                    if first_energy is None:
                        first_energy = energy
                    energy_list.append((energy - first_energy) * 627.5)
                    opt_energy_line = "{},{}\n".format(conv_iter, energy)
                    opt_energies_file.write(opt_energy_line)
                    conv_iter += 1
                else:
                    continue
    return energy_list


def plotly_styling():
    """
    Set lab styling preferences for plotly.
    """
    glob_layout = go.Layout(
        font=dict(family="Helvetica", size=24, color="black"),
        margin=dict(l=100, r=10, t=10, b=100),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            ticks="inside",
            showline=True,
            tickwidth=3,
            linewidth=3,
            ticklen=10,
            linecolor="black",
            mirror="allticks",
            color="black",
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            ticks="inside",
            showline=True,
            tickwidth=3,
            linewidth=3,
            ticklen=10,
            linecolor="black",
            mirror="allticks",
            color="black",
        ),
        legend_orientation="v",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="white",
    )

    return glob_layout


def get_scatter_plot(energy_lists):
    """
    Generate a scatterplot to help quickly vizualize the data.
    """
    glob_layout = plotly_styling()
    colors = ["#FFA500", "#6495ED", "#9370DB", "#E63946", "#000000", "#2a9d8f"]
    name_list = ["Acute", "Obtuse", "Axial", "good", "normal", "wpbeh"]
    blue = "rgba(0, 0, 255, 1)"
    red = "rgba(255, 0, 0, 1)"
    green = "rgba(0, 196, 64, 1)"
    gray = "rgba(140, 140, 140, 1)"
    orange = "rgba(246, 141, 40, 1)"
    sky = "rgba(103, 171, 201, 1)"
    data = []
    print(energy_lists)
    for index, energy_list in enumerate(energy_lists):
        trace = go.Scatter(
            x=list(range(len(energy_list))),
            y=energy_list,
            mode="markers+lines",
            opacity=0.8,
            name=name_list[index],
            marker=dict(size=10, color=colors[index]),
            showlegend=True,
        )
        data.append(trace)

    layout = go.Layout()
    layout.update(glob_layout)
    layout["xaxis"].update({"title": "reaction coordinate"})
    layout["yaxis"].update({"title": "energy (kcal/mol)"})
    layout.update(legend=dict(yanchor="top", xanchor="left"), width=800, height=600)
    fig = dict(data=data, layout=layout)
    iplot(fig)


def get_energies(file_path):
    # Ask the user what type of calculation they would like performed
    calc_type = input(
        "Would you like final (f) or converged (c) energies for {}?: ".format(file_path)
    )
    if calc_type == "f":
        return get_final_energies(file_path)
    elif calc_type == "c":
        return get_opt_energies(file_path)
    else:
        print("Not a valid calculation type")
        return get_energies(file_path)


def pes_plotter():
    print("\n.-------------.")
    print("| PES PLOTTER |")
    print(".-------------.\n")
    print("Collects the final energies from a TeraChem scan into a CSV file.")
    print("The script assumes the .out file is in the current directory.")
    print("Searches through the job output for a TeraChem job.")
    print("Collects the energies into a CSV file as a pandas dataframe.")

    # Get a list of all the .out files in the current directory
    out_list = glob.glob(r"./*.out")
    energy_lists = []
    for out_file in out_list:
        energy_list = get_energies(out_file)
        energy_lists.append(energy_list)

    # Send a list of energy lists to the plotting function
    get_scatter_plot(energy_lists)


# Collect energies into .csv file and create a dataframe
if __name__ == "__main__":
    pes_plotter()
