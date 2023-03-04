"""Automated protocol for the Modeller software"""

from modeller import *
from modeller.automodel import *

def modeller_step1(pdb_code):
    """
    Writes the alignment file.

    Parameters
    ----------
    pdb_code : str
        The PDB code of the protein to be modelled.

    Returns
    -------

    """
    e = Environ()
    m = Model(e, file=pdb_code)
    aln = Alignment(e)
    aln.append_model(m, align_codes=pdb_code)
    aln.write(file=f"{pdb_code}.seq")

    print(f"A sequence file for {pdb_code} was generated.")

def modeller_step2(pdb_code):
    """
    Models in missing residues.

    Parameters
    ----------

    Returns
    -------

    """
    log.verbose()
    env = Environ()

    # directories for input atom files
    env.io.atom_files_directory = [".", "../atom_files"]

    class MyModel(AutoModel):
        def select_atoms(self):
            return Selection(
                self.residue_range("1:A", "10:A"), self.residue_range("169:A", "173:A")
            )

    a = MyModel(env, alnfile=f"{pdb_code}.ali", knowns=pdb_code, sequence=f"{pdb_code}_fill")

    a.starting_model = 1
    a.ending_model = 1

    a.make()

if __name__ == "__main__":
    # Initialize variables that can be obtained from protein3D
    pdb_code = "1OS7"
    
    # Modeller workflow
    modeller_step1(pdb_code)
    modeller_step2(pdb_code)