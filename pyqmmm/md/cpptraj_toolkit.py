import os
import subprocess

def create_cpptraj_script(input_file, output_file, prmtop_file):
    """
    Create a CPPTRAJ script to process the given trajectory file.

    Parameters
    ----------
    input_file : str
        The name of the input trajectory file (.mdcrd or .nc)
    output_file : str
        The name of the output PDB file
    prmtop_file : str
        The name of the parameter/topology file

    Returns
    -------
    str
        The content of the CPPTRAJ script as a string
    """
    cpptraj_script = f"""
    parm {prmtop_file}
    trajin {input_file} lastframe
    strip :WAT,Na+
    trajout {output_file} pdb
    run
    """

    return cpptraj_script

def run_cpptraj(cpptraj_script, script_name="cpptraj_script.in"):
    """
    Run a CPPTRAJ script.

    Parameters
    ----------
    cpptraj_script : str
        The content of the CPPTRAJ script as a string
    script_name : str, optional
        The name of the script file (default is "cpptraj_script.in")
    """
    with open(script_name, "w") as script_file:
        script_file.write(cpptraj_script)

    subprocess.run(["cpptraj", "-i", script_name])

    if os.path.exists(script_name):
        os.remove(script_name)

def get_last_frame():
    """
    Use CPPTraj to get the last frame.
    
    See Also
    --------
    pyqmmm.md.create_cpptraj_script()
    pyqmmm.md.run_cpptraj()
    
    """
    input_file = input("Enter the name of your trajectory file (.mdcrd or .nc): ")
    prmtop_file = input("Enter the name of your prmtop file: ")
    output_file = "last_frame_stripped.pdb"

    cpptraj_script = create_cpptraj_script(input_file, output_file, prmtop_file)
    run_cpptraj(cpptraj_script)

if __name__ == "__main__":
    get_last_frame()
