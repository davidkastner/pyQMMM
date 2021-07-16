# pdb-utilities
>Useful scripts for working with PDB files

## Quick Plotter v1.2
Executes four key analyses that should be performed after any MD simulation. It checks the RMSD, the radius of gyration, the density of the water box, and the total energy as a function of time or frames. Execute this script in the same folder where you ran your MD simualtion. It will search your current directory for four files: rmsd.dat, rog.dat, summary.DENSITY, and summary.ETOT. The first two can be obtained using the CPPTraj tool in Amber and the last two can be obtained by running the Amber process_mdout.perl script in AmberTools. The script will create three pdf figures corresponding to each of the data files in a folder named *figures*.

## EDIA Chains v1.1
Electron support for individual atoms is a powerful software that can be used to inspect the quality of a PDB. The native output will provide an EDIA score for all the individual atoms in the structure or by residue. However, one utility of EDIA is to help chose which protein chain to use for an MD simulation, as one chain is usually higher resolution than the others. After executing EDIA Chains, the script will ask the user for the location of the EDIA output file, the letters of the chains they are interested in (e.g., ABCD), and a list of important key residues the user will be investigating (e.g., 9,23,134). The script will then analyze the EDIA output file and return to figures summarizing the EDIA scores for each chain considering all atoms and another figure just looking at the key residues. 

## PDB Ensemblizer v1.1
This script was written to simplify the process of generating PDB ensembles. It will search the directory that it is executed from for all PDBs. It will then combine the PDBs and format the resulting file as an ensemble. The final file is then saved in a folder that the script creates called *ensemble*.

## Renumerate v1.3
Many Amber preprocessing functions such as pdb4amber will restart residue number at one. While this can be useful when preparing files, it can be frustrating when the protein sequences does not start at one. This is very common as many proteins crystallize better without their N-terminus. When you execute this script, it will ask the user for the name of the PDB that got renumbered inappropriately and what the first residue should be. The script will then correct the number of the residues to start at the residue prompted by the user.

## Renumber Waters v1.1
CPPTRAJ is a tool for working with Amber outputs. However, it will renumber any residues after 9999 starting at 0 in the output PDBs. This is a problem when trying to work with the PDB because the residue IDs are no longer unique and selecting ID 1 will now select residue 1 and water 1. This script fixes this problem by continue the numbering. It will replace the residue 0 that follows 9999 with 10000. Run the script from the same directory as the PDB you would like to renumber and the script will prompt you for the information it needs such as the name of the file.

## Movie Prep v1.0
The Movie Prep script takes the output of a TeraChem geometry optimization and prepares a folder for Chimera's MD Movie plugin. The output of a TeraChem optimization is an ensemble of xyz optimization frames all inside the same file. However, Chimera's MD Movie needs each of the xyz frames to be in its own file. To this end, the script will create a new directory called ```movie``` and fill it with individual xyz files pulled from the TeraChem output ```optim.xyz``` file. The name of each file will be ordered consecutively ```1.xyz, 2.xyz, 3.xyz, etc.```.

## ClusterRMSD v1.0
Almost all MD processing packages can perform clustering and RMSD calculations. ClusterRMSD will take the two and merge them together into a single useful plot. The plot depicts frames on the x-axis and RMSD on the y-axis. It then will color code each point based on which cluster it belongs to. This type of analysis can be useful in helping distinguish how a trajectory evolves over time and what are the main poses that dominate a given trajectory.
