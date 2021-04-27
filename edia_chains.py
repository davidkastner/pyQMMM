#https://proteins.plus/
#EDIA is a powerful tool for evaluating the quality of crystal structures.
#However, the output looks at individual residues or atoms
#This script takes EDIA output and cacluates the average chain EDIA scores
#The chain with the highest EDIA score is likely the best one to use

#Import packages and dependencies
import numpy as numpy
import matplotlib.pyplot as plt
import pandas as pd

#Get user input
csv = input('What is the name of your EDIA CSV file without extension?')
chains = input('What chains would you like to compare (e.g., "ABC")?')
print('')

#Open CSV file into pandas dataframe
df = pd.read_csv('{}.csv'.format(csv))
df_all = df[['Chain','EDIAm','Median EDIA']]

#Examine user input and return errors
chains = chains.upper()
chain_list = []
for chain in chains:
  if chain in df_all.Chain.values:
    print('Chain {} found.'.format(chain))
    chain_list.append(chain)
  else:
    print('Chain {} not found.'.format(chain))
    print('Will check other chains.')
print('-------------------')
print()

#Create empty dataframe to store means
df_means = pd.DataFrame(index = [chain for chain in chain_list],
                          columns = ['EDIAm','EDIA'])
#Create empty dataframe to store standard error
df_se = pd.DataFrame(index = [chain for chain in chain_list],
                          columns = ['EDIAm SE','EDIA SE'])

#Calculate the Avg. EDIAm, Avg. EDIA, and Std. Error
for chain in chain_list:
  #Isolate a specific chain
  isolated_chain = df_all.loc[df['Chain'] == chain]

  #Get the mean for EDIAm and EDIA
  avg_ediam = isolated_chain['EDIAm'].mean()
  avg_edia = isolated_chain['Median EDIA'].mean()
  #Store it in the df_means dataframe
  df_means.loc[chain] = [avg_ediam, avg_edia]

  #Get the standard error for EDIAm and EDIA
  std_err_ediam = isolated_chain['EDIAm'].sem()
  std_err_edia = isolated_chain['Median EDIA'].sem()
  #Store it in the df_means dataframe
  df_se.loc[chain] = [std_err_ediam, std_err_edia]

#Rank order the chains by EDIA score
sorted_df = df_means.sort_values(by='EDIA', ascending=False)
print('Your sorted results:')
print(sorted_df)
print('-------------------')
print()

#Plot the findings
#Plot constants
colors = ['#48bfe3','#6930c3']
label = [chain for chain in chain_list]

#Plot parameters
plt.rc('axes', linewidth=2.5)
fig, ax = plt.subplots()
df_means.plot.bar(yerr=df_se, ax=ax, capsize=4, rot=0, color=colors)
plt.title('Chain Comparison', fontsize=18)
plt.ylabel('EDIA Score', fontsize=16)
plt.xlabel('Chains', fontsize=16)
plt.xticks(rotation=0)
plt.tick_params(labelsize=14)
plt.legend(fontsize=12, loc='lower right')
plt.savefig('chain_comparison.pdf', bbox_inches = 'tight')
print('Figure has been created.')
print('-------------------')
