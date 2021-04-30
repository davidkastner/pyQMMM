# pdb-utilities
Useful scripts for working with PDB files

## Analysis Plot v1.2
This script helps simplify four key analyses that should be performed after any MD simulation finishes. It can be very helpful to check the RMSD, the radius of gyration, the density of the water box, and the total energy as a function of time or frames. Execute this script in the same folder where you ran your MD simualtion and performed your analysis. It will search your current directory from four files: rmsd.dat, rog.dat, density.dat, and energy.dat. The first two can be obtained using the CPPTraj tool in Amber and the last two can be obtained very easily by running the classic Amber process_mdout.perl script. The script will drop three pdf figures corresponding to each of the data files in a folder named *figures*.

## EDIA Chains v1.1
Electron support for individual atoms is a powerful software that can be used to inspect the quality of a PDB. The native output will provide an EDIA score for all the individual atoms in the structure or by residue. However, one utility of EDIA is to help chose which protein chain to use for an MD simulation, as one chain is usually higher resolution than the others. After executing EDIA Chains, the script will ask the user for the location of the EDIA output file, the letters of the chains they are interested in (e.g., ABCD), and a list of important key residues the user will be investigating (e.g., 9,23,134). The script will then analyze the EDIA output file and return to figures summarizing the EDIA scores for each chain considering all atoms and another figure just looking at the key residues. 

## PDB Ensemblizer v1.1
This script was written to simplify the process of generating PDB ensembles. It will search the directory that it is executed from for all PDBs. It will then combine the PDBs and format the resulting file as an ensemble. The final file is then saved in a folder that the script creates called *ensemble*.

## Renumerate v1.1

