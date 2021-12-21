#$ -S /bin/bash
#$ -N BesD_obtuse_GBSA
#$ -l h_rt=168:00:00
#$ -cwd
#$ -l h_rss=2G
#$ -q cpus
#$ -pe smp 4
cd $SGE_O_WORKDIR

module load amber/18-cuda10
source /opt/amber_18_cuda10/amber.sh
export PYTHONPATH=/opt/amber_18_cuda10/lib/python2.7/site-packages

prmtop="besd_stripped.prmtop"
struc=`echo $prmtop | sed  's/.prmtop/besd/'`
coords="besd_stripped.mdcrd"
start="124376"
for intdiel in 1; do
for obc in 1; do
for ligcomb in caba; do
if [ "$ligcomb" == "caba" ]; then
entropy="1"
else
entropy="0"
fi
if [ "$obc" == "1" ]; then
igbval="2"
else
igbval="5"
fi
stripmask=""
if [ "$ligcomb" == "caba" ]; then
ligmask=":247"

fi
python /opt/amber_18_cuda10/bin/ante-MMPBSA.py -p $prmtop -c $struc.$ligcomb.complex.prmtop -r $struc.$ligcomb.receptor.prmtop -l $struc.$ligcomb.ligand.prmtop -n :247 -s :WAT
#cp $prmtop $struc.$ligcomb.complex.prmtop
for idecompval in 4; do
cat > $struc.$ligcomb.g$igbval.e$intdiel.i$idecompval.in << EOF
Per-residue GB and PB decomposition
&general
   interval=1, startframe=$start,verbose=1,entropy=$entropy,strip_mask=":WAT",debug_printlevel=1,use_sander=1,
/
&gb
  igb=$igbval,molsurf=0,
/
&decomp
  idecomp=$idecompval,
  dec_verbose=3,
/
EOF
/opt/amber_18_cuda10/bin/MMPBSA.py -O -i $struc.$ligcomb.g$igbval.e$intdiel.i$idecompval.in  -o $struc.$ligcomb.g$igbval.e$intdiel.file1$idecompval.dat  -do $struc.$ligcomb.g$igbval.e$intdiel.file2$idecompval.dat -eo $struc.$ligcomb.g$igbval.e$intdiel.file3$idecompval.dat -deo $struc.$ligcomb.g$igbval.e$intdiel.file4$idecompval.dat -sp $prmtop -cp $struc.$ligcomb.complex.prmtop -lp $struc.$ligcomb.ligand.prmtop -rp $struc.$ligcomb.receptor.prmtop -y $coords
mkdir pbsa$struc$ligcomb$igbval$intdiel$idecompval/
mv -f _MMPBSA* pbsa$struc$ligcomb$igbval$intdiel$idecompval/
done
done
done
done
