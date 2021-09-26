################################ DEPENDENCIES ##################################
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
################################## FUNCTIONS ###################################
def get_df():
    df = pd.read_csv("pc.csv", index_col=None)
    df = df.iloc[:,1:]
    return df

def get_plot(df):
    font = {'family': 'sans-serif', 'weight': 'bold', 'size': 18}
    plt.rc('font', **font)
    plt.rc('axes', linewidth=2.5)
    plt.rcParams['lines.linewidth'] = 2.5
    plt.rcParams['xtick.major.size'] = 10
    plt.rcParams['xtick.major.width'] = 2.5
    plt.rcParams['ytick.major.size'] = 10
    plt.rcParams['ytick.major.width'] = 2.5
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.rcParams['mathtext.default'] = 'regular'

    plt.figure(figsize=(7, 7))
    plt.ylabel('PC2', fontweight='bold')
    plt.xlabel('PC1', fontweight='bold')

    plt.scatter(df.V1, df.V2, c=df.index, cmap="RdBu")
    plt.savefig('pc.pdf', bbox_inches='tight', dpi=300)

def pca_plot():
    df = get_df()
    get_plot(df)
    
# Execute the DCCM Mapper function when run as a script
if __name__ == "__main__":
    pca_plot()
