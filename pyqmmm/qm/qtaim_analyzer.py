"""
Docs: https://github.com/davidkastner/pyQMMM/blob/main/pyqmmm/README.md
DESCRIPTION
    Creates paired bar plot for halogenase vs hydroxylase project.
    Author: David Kastner
    Massachusetts Institute of Technology
    kastner (at) mit . edu
"""

# Imports
import pandas as pd
import plotly.graph_objects as go


def plotly_styling():
    """
    Set lab styling preferences for plotly.
    """
    # Generalized Plotly styling dictionary
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
        paper_bgcolor="rgba(255,255,255,1)",
        plot_bgcolor="white",
    )

    return glob_layout


def get_barplot_plot(dataframe, filename):
    """
    Generate a paired barplot.

    """
    # Additional color settings
    blue = "rgba(0, 0, 255, 1)"
    red = "rgba(255, 0, 0, 1)"
    # green = "rgba(0, 196, 64, 1)"
    # gray = "rgba(140, 140, 140, 1)"
    # orange = "rgba(246, 141, 40, 1)"
    # sky = "rgba(103, 171, 201, 1)"

    # Set the layout
    glob_layout = plotly_styling()
    layout = go.Layout()
    layout.update(glob_layout)
    layout["xaxis"].update({"title": "residues"})
    layout["yaxis"].update({"title": "energy (kcal/mol)"})
    layout.update(width=575, height=500)

    # Create the plotly figure
    fig = go.Figure()
    acute = go.Bar(x=dataframe["residue"], y=dataframe["acute"], marker_color=blue)
    obtuse = go.Bar(x=dataframe["residue"], y=dataframe["obtuse"], marker_color=red)
    fig.add_trace(acute)
    fig.add_trace(obtuse)
    fig.layout.update(layout)
    fig.update_layout(showlegend=False)
    fig.write_image(f"{filename}.svg")
    fig.show()


def hbond_plotter():
    print("\n.-------------.")
    print("| HBOND PLOTTER |")
    print(".-------------.\n")
    print("Plots hbond grouped bar plot.\n")

    # Create dataframes for hbonding data
    taud = pd.DataFrame(
        [
            ["R270", -10.79, -12.69],
            ["N95", -10.50, -9.83],
            ["D94", -9.12, -0.001],
            ["H70", -8.62, -8.19],
            ["V102", -6.00, -5.62],
            ["Y73", -4.4, -2.14],
        ],
        columns=["residue", "acute", "obtuse"],
    )

    vioc = pd.DataFrame(
        [
            ["D268", -21.93, -23.54],
            ["R334", -16.83, -4.97],
            ["D222", -15.33, -9.53],
            ["S158", -13.30, -11.41],
            ["E170", -9.05, -11.41],
            ["D270", -8.89, -8.93],
            ["L156", -6.60, -4.97],
            ["S224", -4.54, -6.12],
            ["Q137", -0.51, -9.21],
            ["D171", -0.25, -8.12],
        ],
        columns=["residue", "acute", "obtuse"],
    )

    besd = pd.DataFrame(
        [
            ["R67", -17.83, -16.43],
            ["E120", -15.85, -16.77],
            ["T214", -8.75, -11.01],
            ["W231", -8.47, -6.22],
            ["W131", -0.94, -6.57],
            ["H127", -0.13, -10.77],
        ],
        columns=["residue", "acute", "obtuse"],
    )

    # welo5 = pd.DataFrame([['T151',-5.29,0],
    #                       ['R153',-0.89,0],
    #                       ['M221',-0.85,-3.08],
    #                       ['A82',0,-4.10],
    #                       ['M225',0,0]],
    #                       columns = ['residue','acute','obtuse'])

    welo5 = pd.DataFrame(
        [
            ["T151", -5.29, 0],
            ["R153", -0.89, 0],
            ["M221", -0.85, -3.08],
            ["A82", 0, -4.10],
            ["M225", 0, 0],
        ],
        columns=["residue", "acute", "obtuse"],
    )

    # Define lists that we can loop over
    filenames = ["taud", "vioc", "besd", "welo5"]
    dataframes = [taud, vioc, besd, welo5]
    for dataframe, filename in zip(dataframes, filenames):
        get_barplot_plot(dataframe, filename)


# Collect energies into .csv file and create a dataframe
if __name__ == "__main__":
    hbond_plotter()
