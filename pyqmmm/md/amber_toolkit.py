"""A library of CPPTraj scripts and built-in generator functions."""

import os
import textwrap
import subprocess


def get_last_frame(prmtop, mdcrd, output_pdb):
    """
    Get the last frame from a trajectory as a PDB.

    Parameters
    ----------
    prmtop : str
        The path to the prmtop file
    mdcrd : str
        The path to the mdcrd file

    """
    command = f"cpptraj -p {prmtop} -y {mdcrd} -ya 'lastframe' -x {output_pdb}"
    try:
        process = subprocess.run(
            command, shell=True, check=True, text=True, capture_output=True
        )
        print("CPPTraj output:", process.stdout)
    except subprocess.CalledProcessError as e:
        print(f"CPPTraj command failed with error: {e.returncode}")


def run_cpptraj(cpptraj_script, script_name="cpptraj_script.in"):
    """
    A generalizable function that can be used to run any of the cpptraj scripts.

    This script will submit the job interactively rather than as a queued job.
    It would not be a good idea to use this script with a long job.

    Parameters
    ----------
    cpptraj_script : str
        The content of the CPPTRAJ script as a string
    script_name : str, optional
        The name of the script file (default is "cpptraj_script.in")

    """
    # Create a new file with the contents of the script
    with open(script_name, "w") as script_file:
        script_file.write(cpptraj_script)

    # Submit the script from the command line
    subprocess.run(["cpptraj", "-i", script_name])

    # Delete the script after it has run
    if os.path.exists(script_name):
        os.remove(script_name)


def submit_script(protein_id, script_name, cpus):
    """
    Classic submit script for CPPTraj jobs.

    This script is for Gibraltar but can be modified for any SGE system.

    """
    submit_script = textwrap.dedent(
        f"""\
    #!/bin/bash
    #$ -S /bin/bash
    #$ -N {protein_id}_cpptraj_job
    #$ -l h_rt=168:00:00
    #$ -cwd
    #$ -l h_rss=8G
    #$ -q cpus
    #$ -pe smp {cpus}
    cd $SGE_O_WORKDIR

    module load amber/18

    cpptraj -i {script_name}
    """
    )

    # Create a new file with the contents of the script and submit to queue
    with open("jobscript.sh", "w") as script_file:
        script_file.write(submit_script)
    subprocess.run(["/bin/bash", "-c", "module load sge && qsub jobscript.sh"])


def calculate_hbonds_script(protein_id, substrate_index, residue_range):
    """
    Calculate all hbonds that form between the protein and substrate.

    """
    hbonds_script = textwrap.dedent(
        f"""\
    parm ../../{protein_id.lower()}_solv.prmtop
    trajin ../../1_output/constP_prod.mdcrd
    strip :NA+,Na+,WAT
    autoimage
    hbond donormask :{substrate_index} acceptormask :{residue_range} out nhb1.dat avgout avghb1.dat dist 3.2
    hbond donormask :{residue_range} acceptormask :{substrate_index} out nhb2.dat avgout avghb2.dat dist 3.2
    hbond contacts avgout avg.dat series uuseries hbond.gnu nointramol dist 3.2
    run
    """
    )

    # Create a new file with the contents of the script
    with open("hbonds.in", "w") as script_file:
        script_file.write(hbonds_script)


def closest_waters_script(protein_id, centroid, all_residues):
    """
    Extract the 9000 waters closest to the centroid

    """
    closest_waters = textwrap.dedent(
        f"""\
    parm ../../{protein_id.lower()}_solv.prmtop
    trajin ../../1_output/constP_prod.mdcrd {centroid} {centroid} 1
    strip :NA+,Na+
    autoimage
    closestwaters 9000 :{all_residues} noimage center outprefix closest
    trajout {protein_id}_closest9000.pdb pdb
    run
    """
    )

    # Create a new file with the contents of the script
    with open("closest_waters.in", "w") as script_file:
        script_file.write(closest_waters)


def strip_all_script(protein_id):
    """
    Strip waters, ions, and metals and generate new mdcrd and prmtop files

    """
    strip_all = textwrap.dedent(
        f"""\
    parm ../../{protein_id.lower()}_solv.prmtop
    trajin ../../1_output/constP_prod.mdcrd
    strip :NA+,Na+,WAT,FE1 outprefix prmtop
    trajout {protein_id}_stripped.mdcrd
    run
    """
    )

    # Create a new file with the contents of the script
    with open("strip.in", "w") as script_file:
        script_file.write(strip_all)


def basic_metrics_script(protein_id, all_residues, select_residues):
    """
    Get basic useful metrics

    """
    basic_metrics = textwrap.dedent(
        f"""\
    parm ../../{protein_id.lower()}_solv.prmtop
    trajin ../../../1_output/constP_prod.mdcrd
    strip :NA+,Na+
    autoimage
    rms first :67,113,127,130,131,133,197,214,212,231,232,244,245,246,247,248&!@H= out rmsd.dat
    radgyr :{all_residues}&!(@H=) out rog.dat mass nomax
    atomicfluct :{select_residues}&!@H= out rmsf.dat
    secstruct :{select_residues} out dssp.gnu sumout dssp.agr
    run
    """
    )

    # Create a new file with the contents of the script
    with open("basic_metrics.in", "w") as script_file:
        script_file.write(basic_metrics)


def angles_and_dist_script(protein_id, h_index, oxo_index, iron_index):
    """
    Get distances and angles

    """
    angles_distances = textwrap.dedent(
        f"""\
    parm ../../{protein_id.lower()}_solv.prmtop
    trajin ../../../1_output/constP_prod.mdcrd
    strip :NA+,Na+
    autoimage
    distance h_oxo @{h_index} @{oxo_index} out h_oxo_distance.agr
    distance h_fe @{h_index} @{iron_index} out h_fe_distance.agr
    angle h_fe_oxo @{h_index} @{iron_index} @{oxo_index} out h_fe_oxo_angle.agr
    run
    """
    )

    # Create a new file with the contents of the script
    with open("angles_distances.in", "w") as script_file:
        script_file.write(angles_distances)


def gbsa_script(protein_id, ligand_name, ligand_index_minus_one, stride, cpus=16):
    """
    Automated GBSA script.

    """
    gbsa_script = textwrap.dedent(
        f"""\
    #!/bin/bash
    #$ -S /bin/bash
    #$ -N {protein_id}
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

    prmtop="{protein_id}_stripped.prmtop"
    struc=$(echo $prmtop | sed 's/.prmtop/{protein_id}/')
    coords="{protein_id}_stripped.nc"
    start="100000"
    ligand_name="{ligand_name}"
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
    """
    )

    # Create a new file with the contents of the script and submit to queue
    with open("gbsa.sh", "w") as script_file:
        script_file.write(gbsa_script)
    subprocess.run(["/bin/bash", "-c", "module load sge && qsub gbsa.sh"])


if __name__ == "__main__":
    protein_id = input("Enter the name of your protein: ")
    cpptraj_script = pdb_trajectory_script(protein_id)
    run_cpptraj(cpptraj_script)
