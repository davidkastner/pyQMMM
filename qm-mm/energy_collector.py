'''
See more here: https://github.com/davidkastner/quick-csa/blob/main/README.md
DESCRIPTION
   Searches through the job output for a TeraChem job and collects the energies
   into a CSV file that can be read in later as a pandas dataframe.
   Author: David Kastner
   Massachusetts Institute of Technology
   kastner (at) mit . edu
SEE ALSO

'''
################################ DEPENDENCIES ################################## 
import glob
import sys
import pandas as pd
import matplotlib.pyplot as plt
import plotly
import plotly.io as pio
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
!conda install -c plotly plotly-orca
################################# FUNCTIONS #################################### 
'''
Find the .out file in the current directory.
'''    
def get_out_file():
    out_pattern = r'./*.out'
    out = glob.glob(out_pattern)
    if len(out) == 0:
        print('No .out file in the current directory.')
        sys.exit()
    if len(out) > 1:
        print('More than one .out file has been provided.')
        sys.exit()
    out_name = out[0].split('/')[-1]
    return out_name

'''
Set lab styling preferences for plotly.
'''    
def plotly_styling():
    glob_layout = go.Layout(
        font=dict(family='Helvetica', size=24, color='black'),
        margin=dict(l=100, r=10, t=10, b=100),
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

'''
Generate a scatterplot to help quickly vizualize the data.
'''    
def get_scatter_plot(energy_list):
    blue = "rgba(0, 0, 255, 1)"
    red = "rgba(255, 0, 0, 1)"
    green = "rgba(0, 196, 64, 1)"
    gray = "rgba(140, 140, 140, 1)"

    glob_layout = plotly_styling()
    trace = go.Scatter(
    x=list(range(len(energy_list))),
    y=energy_list,
    mode='markers',
    opacity=0.8,
    marker=dict(
        size=8,
        color=blue),
    showlegend=False)

    data = [trace]
    layout = go.Layout()
    layout.update(glob_layout)
    layout["xaxis"].update({'title': "frame"})
    layout["yaxis"].update({'title': "energy"})
    layout.update(width=1000, height=500)
    fig = dict(data=data, layout=layout)
    iplot(fig)
    pio.write_image(fig, 'energies.pdf')


'''
Loop through the file, collect optimized energies and create a dataframe.

Parameters
----------

Returns
-------
energy_df : dataframe
    The optimized energy from the current convergence line of the file.
energy_list : list
    Returns a list of the energies extracted from the .out file.
'''    
def extract_energies():
    out_name = get_out_file()
    energy_list = []
    conv_iter = 1
    with open('./{}'.format(out_name), 'r') as out_file:
        with open('./opt_energies.csv', 'w') as opt_energies_file:
            for line in out_file:
                if line[6:22] == 'Optimized Energy':
                    energy = line[26:42]
                    energy_list.append(energy)
                    opt_energy_line = '{},{}\n'.format(conv_iter, energy)
                    opt_energies_file.write(opt_energy_line)
                    conv_iter += 1
                else:
                    continue
    energy_df = pd.read_csv('./opt_energies.csv', header = None, 
                            names = ['Round','Energy'])
    return energy_list, energy_df

################################## QUICK CSA ################################### 
#Introduce user to Quick CSA functionality
print('WELCOME TO ENERGY COLLECTOR')
print('--------------------------\n')
print('Collects the final energies from a TeraChem scan into a CSV file.')
print('The script assumes the .out file is in the current directory.')
print('--------------------------\n')

#Collect energies into .csv file and create a dataframe
energy_list, energy_df = extract_energies()
get_scatter_plot(energy_list)