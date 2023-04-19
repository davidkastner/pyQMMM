"""A library of common CPPTraj scripts and built-in generator functions."""

import textwrap

# Define the submit script
submit_script = textwrap.dedent(f"""\
#!/bin/bash
#$ -S /bin/bash
#$ -N {protein_name}_hbond
#$ -l h_rt=168:00:00
#$ -cwd
#$ -l h_rss=8G
#$ -q cpus
#$ -pe smp {cpus}
cd $SGE_O_WORKDIR
module load amber/18
cpptraj -i {script}.in
""")


# Define the CPPTRAJ script
cpptraj_script = textwrap.dedent(f"""\
parm ../../{protein_name}_solv.prmtop
trajin ../../1_output/constP_prod.mdcrd
strip :NA+,Na+,WAT autoimage hbond donormask :{substrate_index} acceptormask :{residue_range} out nhb1.dat avgout avghb1.dat dist 3.2
hbond donormask :{residue_range} acceptormask :{substrate_index} out nhb2.dat avgout avghb2.dat dist 3.2
hbond contacts avgout avg.dat series uuseries hbond.gnu nointramol dist 3.2 run
run
""")

# Extract the 9000 waters closest to the centroid
closest_waters = textwrap.dedent(f"""\
parm ../../{protein_name}_solv.prmtop
trajin ../../1_output/constP_prod.mdcrd {centroid} {centroid} 1
strip :NA+,Na+
autoimage
closestwaters 9000 :{all_residues} noimage center outprefix closest
trajout {protein_name}_closest9000.pdb pdb
run
""")

# Strip waters and generate a AMBER nc file
strip_waters = textwrap.dedent(f"""\
parm ../../../{protein_name}_solv.prmtop
trajin ../../../1_output/constP_prod.mdcrd
strip :NA+,Na+,WAT,FE1 outprefix prmtop
trajout {protein_name}_stripped.nc
run
""")

# Get basic useful metrics
basic_metrics = textwrap.dedent(f"""\
parm ../../{protein_name}_solv.prmtop
trajin ../../1_output/constP_prod.mdcrd {centroid} {centroid} 1
strip :NA+,Na+
autoimage
rms first :67,113,127,130,131,133,197,214,212,231,232,244,245,246,247,248&!@H= out rmsd.dat
radgyr :{all_residues}&!(@H=) out rog.dat mass nomax
atomicfluct :{select_residues}&!@H= out rmsf.dat
secstruct :{select_residues} out dssp.gnu sumout dssp.agr
run
""")

# Get distances and angles
angles_distances = textwrap.dedent(f"""\
parm ../../{protein_name}_solv.prmtop
trajin ../../1_output/constP_prod.mdcrd {centroid} {centroid} 1
strip :NA+,Na+
autoimage
distance h_oxo @{h_index} @{oxo_index} out h_oxo_distance.agr
distance h_fe @{h_index} @{iron_index} out h_fe_distance.agr
angle h_fe_oxo @{h_index} @{iron_index} @{oxo_index} out h_fe_oxo_angle.agr
run
""")

# GBSA script
gbsa_script = = textwrap.dedent(f"""\
#!/bin/bash
#$ -S /bin/bash
#$ -N {protein_name}
#$ -l h_rt=168:00:00
#$ -cwd
#$ -l h_rss=16G
#$ -q cpus
#$ -pe smp {cpus}
cd $SGE_O_WORKDIR

module unload amber
module unload cuda
module load openmpi/4.1.0
module load amber/18-cuda10
source /opt/amber_18_cuda10/amber.sh
export PYTHONPATH=/opt/amber_18_cuda10/lib/python2.7/site-packages

prmtop="{protein_name}_stripped.prmtop"
struc=$(echo $prmtop | sed 's/.prmtop/{protein_name}/')
coords="{protein_name}_stripped.nc"
start="100000"
ligand_name="{ligand_name}" # Define your ligand name here
entropy="1"
igbval="2"
ligmask=":{ligand_index_minus_one}"

python /opt/amber_18_cuda10/bin/ante-MMPBSA.py -p $prmtop -c $struc.$ligand_name.complex.prmtop -r $struc.$ligand_name.receptor.prmtop -l $struc.$ligand_name.ligand.prmtop -n $ligmask -s :WAT

idecompval="4"
cat > $struc.$ligand_name.g$igbval.e1.i$idecompval.in << EOF
Per-residue GB and PB decomposition
&general
   interval={stride}, startframe=$start,verbose=1,entropy=$entropy,strip_mask=":WAT",debug_printlevel=1,use_sander=1,
/
&gb
  igb=$igbval,molsurf=0,
/
&decomp
  idecomp=$idecompval,
  dec_verbose=3,
/
EOF

/opt/amber_18_cuda10/bin/MMPBSA.py -O -i $struc.$ligand_name.g$igbval.e1.i$idecompval.in  -o $struc.$ligand_name.g$igbval.e1.file1$idecompval.dat  -do $struc.$ligand_name.g$igbval.e1.file2$idecompval.dat -eo $struc.$ligand_name.g$igbval.e1.file3$idecompval.dat -deo $struc.$ligand_name.g$igbval.e1.file4$idecompval.dat -sp $prmtop -cp $struc.$ligand_name.complex.prmtop -lp $struc.$ligand_name.ligand.prmtop -rp $struc.$ligand_name.receptor.prmtop -y $coords

mkdir pbsa$struc$ligand_name$igbval1$idecompval/
mv -f _MMPBSA* pbsa$struc$ligand_name$igbval1$idecompval/
""")