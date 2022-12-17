"""Creates an energy profile for a TeraChem constrained geometry scan."""

import glob
import numpy as np
import pandas as pd
import plotly.io as pio
import plotly.graph_objs as go
import plotly.express as px
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot


def get_opt_energies(file_name):
    '''
    Loop through the file, collect optimized energies.
    
    Returns
    -------
    energy_df : dataframe
        The optimized energy from the current convergence line of the file.
    energy_list : list
        Returns a list of the energies extracted from the .out file.
    '''

    energy_list = []
    with open(file_name, 'r') as file:
        for line in file:
            if "Job" in line:
                # The fifth element should be the energy
                energy = float(line.split()[4])
                energy_list.append(energy)
    
    return energy_list

def get_relative_energies(energy_list):
    """
    Convert energies to relative energies

    """

    # Take the smallest value as the ground state
    ground_state = energy_list[0]
    # The equation for calculating the relative energy
    relative_energy = lambda x: -(ground_state*627.5)+(x*627.5)
    # Convert all energies to relative energies
    energy_list = [relative_energy(i) for i in energy_list]

    return energy_list

def plotly_styling():
    '''
    Set lab styling preferences for plotly.
    '''

    glob_layout = go.Layout(
        font=dict(family='Arial', size=22, color='black'),
        margin=dict(l=100, r=225, t=10, b=100),
        xaxis=dict(showgrid=False,  zeroline=False, ticks="inside", showline=True,
                   tickwidth=3, linewidth=3, ticklen=10, linecolor='black',
                   mirror="allticks", color="black"),
        yaxis=dict(showgrid=False,  zeroline=False, ticks="inside", showline=True,
                   tickwidth=3, linewidth=3, ticklen=10, linecolor='black',
                   mirror="allticks", color="black"),
        legend_orientation="v",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='white')

    return glob_layout


def get_scatter_plot(energy_list, out_name, start, end, atoms):
    '''
    Generate a scatterplot to help quickly vizualize the data.
    '''

    # Kulik Lab color definitions
    blue = "rgba(0, 0, 255, 1)"
    red = "rgba(255, 0, 0, 1)"
    green = "rgba(0, 196, 64, 1)"
    gray = "rgba(140, 140, 140, 1)"
    orange = "rgba(246, 141, 40, 1)"
    sky = "rgba(103, 171, 201, 1)"

    # User defined variables
    color = 'blue'
    start = start
    end = end
    points = 70
    file_name = out_name
    x_title = f"<b>{atoms} distance (Å)</b>"
    y_title = "<b>energy (kcal/mol)</b>"

    data = []
    glob_layout = plotly_styling()
    trace = go.Scatter(
        x=np.linspace(start, end, points),
        y=energy_list,
        mode='markers+lines',
        opacity=0.8,
        marker=dict(size=10, color=color))

    layout = go.Layout()
    layout.update(glob_layout)
    layout["xaxis"].update({'title': x_title})
    layout["yaxis"].update({'title': y_title})

    fig = go.Figure()
    # Add minor ticks to the x-axis
    fig.update_xaxes(minor=dict(dtick=.25, ticklen=6, tickcolor="black"))
    fig.update_xaxes(minor_ticks="inside")
    fig.update_xaxes(autorange="reversed")
    # Bold the axis labels
    fig.update_yaxes(tickprefix="<b>")
    fig.update_xaxes(tickprefix="<b>")
    # Change the size of the axes fonts
    fig.update_layout(xaxis = dict(titlefont = dict(size=22)))
    fig.update_layout(yaxis = dict(titlefont = dict(size=22)))
    fig.add_trace(trace)
    fig.layout.update(layout)
    fig.write_image(file_name)
    iplot(fig)


def references(name):
    """
    Stores user defined variables.
    """
    if name == "besd_acute":
        start = 2.202
        end = 0.981
        atoms = "O···H"
    elif name == "besd_obtuse":
        start = 2.205
        end = 0.981
        atoms = "O···H"
    elif name == "welo5_acute":
        start = 2.538
        end = 0.981
        atoms = "O···H"
    elif name == "welo5_obtuse":
        start = 2.659
        end = 0.981
        atoms = "O···H"
        
    # if name == "besd_acute":
    #     start = 3.5
    #     end = 1.87
    #     atoms = "Cl···C"
    # elif name == "besd_obtuse":
    #     start = 3.2
    #     end = 1.87
    #     atoms = "Cl···C"
    # elif name == "taud_acute":
    #     start = 3.08
    #     end = 1.41
    #     atoms = "O···C"
    # elif name == "taud_obtuse":
    #     start = 2.92
    #     end = 1.41
    #     atoms = "O···C"
    # elif name == "vioc_acute":
    #     start = 2.79
    #     end = 1.4
    #     atoms = "O···C"
    # elif name == "vioc_obtuse":
    #     start = 2.79
    #     end = 1.44
    #     atoms = "O···C"
    # elif name == "welo5_acute":
    #     start = 3.40
    #     end = 1.87
    #     atoms = "Cl···C"
    # elif name == "welo5_obtuse":
    #     start = 3.50
    #     end = 1.87
    #     atoms = "Cl···C"
    # else:
    #     start = 1.0
    #     end = 3.0
    #     atoms = "C···H"

    return start, end, atoms


def pes_plotter():
    """
    Generates the PES plot using the extracted data.

    Note
    ----
    If you want to save the image
    > pip install -U kaleido

    """
    
    print('\n.-------------.')
    print('| PES PLOTTER |')
    print('.-------------.\n')
    print('Collects the final energies from a TeraChem scan into a CSV file.')
    print('The script assumes the .out file is in the current directory.')
    print('--------------------------\n')

    # Get the name of the scan xyz to process
    name = "welo5_obtuse"
    file_name = f"{name}.xyz"
    out_name = f"{name}.svg"
    # Extract energies
    energy_list = get_opt_energies(file_name)
    energy_list = get_relative_energies(energy_list)
    # Send a list of energy lists to the plotting function
    start, end, atoms = references(name)
    get_scatter_plot(energy_list, out_name, start, end, atoms)


# Collect energies into .csv file and create a dataframe
if __name__ == "__main__":
    pes_plotter()
