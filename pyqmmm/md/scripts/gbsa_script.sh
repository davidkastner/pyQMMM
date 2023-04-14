#!/bin/bash
#$ -S /bin/bash
#$ -N AxU1
#$ -l h_rt=168:00:00
#$ -cwd
#$ -l h_rss=16G
#$ -q cpus
#$ -pe smp 16
cd $SGE_O_WORKDIR

module unload amber
module unload cuda
module load openmpi/4.1.0
module load amber/18-cuda10
source /opt/amber_18_cuda10/amber.sh
export PYTHONPATH=/opt/amber_18_cuda10/lib/python2.7/site-packages

prmtop="dah_stripped.prmtop"
struc=$(echo $prmtop | sed 's/.prmtop/dah/')
coords="dah_stripped.nc"
start="100000"
ligand_name="dca" # Define your ligand name here
entropy="1"
igbval="2"
ligmask=":355"

python /opt/amber_18_cuda10/bin/ante-MMPBSA.py -p $prmtop -c $struc.$ligand_name.complex.prmtop -r $struc.$ligand_name.receptor.prmtop -l $struc.$ligand_name.ligand.prmtop -n $ligmask -s :WAT

idecompval="4"
cat > $struc.$ligand_name.g$igbval.e1.i$idecompval.in << EOF
Per-residue GB and PB decomposition
&general
   interval=50, startframe=$start,verbose=1,entropy=$entropy,strip_mask=":WAT",debug_printlevel=1,use_sander=1,
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