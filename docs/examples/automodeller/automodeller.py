"""Automated protocol for the Modeller software"""

from modeller import *
from modeller.automodel import *

def modeller_step1(pdb_code):
    """
    Writes the sequence file.

    The first step of the Modeller workflow is to create a sequence (seq) file.
    The seq file is a template for manually creating an alignment (ali) file.
    The seq file contains the sequence of the protein as it appears in the PDB.
    This means it will be missing amino acids.
    The seq file is used to build the ali file which as all the amino acids.

    Parameters
    ----------
    pdb_code : str
        The PDB code of the protein to be modelled.

    Notes
    -----
    Example contents of the seq file. Notice the blank first line.
    `

    >P1;6l6x
    structureX:6l6x:30:A:+294:A:::-1.00:-1.00
    RMQIDEQPGNAIGAAVEGFDHATASDADIDALKSTIYTKKIAVLKGQDLSPQQFLALGKRLGRPEAYYEPMYQHP
    EVTEIFVSSNVPENGKQIGVPKTGKFWHADYQFMPDPFGITLIYPQVIPEKNRGTYFIDMGRAYDRLPEDLKKEI
    SGTYCRHSVRKYFKIRPHDVYRPISEIIEEVERKTPAVVQPTTFTHPMTGETVLYISEGFTVGIEDQDGKPLDEE
    LLKRLFDATGQLDESFEHDNIHLQSFEQGDLLVWDNRSLIHRARHTTTPEPTVSYRVTVHDERKLHDGI*
    `

    """
    e = Environ()
    m = Model(e, file=pdb_code)
    aln = Alignment(e)
    aln.append_model(m, align_codes=pdb_code)
    aln.write(file=f"{pdb_code}.seq")

    print(f"A sequence file for {pdb_code} was generated.")

def get_alignment_file(pdb_code, missing_residues):
    """
    Creates the alignment file from the sequence file.

    The ali file is the same as the seq file with an additional section added.
    The new section is added below, which contains the full gene of the protein.
    The that was generated with the seq file will need to be modified.
    The `-` symbols will need to be added where ever an amino acid is missing.


    Parameters
    ----------
    pdb_code : str
        The PDB code of the protein to be modelled.
    missing_residues : list[int]
        A list of the indices of the missing amino acids


    Notes
    -----
    Example contents of the alignment file.
    `
    >P1;6l6x
    structureX:6l6x:30:A:+294:A:::-1.00:-1.00
    -----------------------------RMQIDEQPGNAIGAAVEGFDHATASDADIDALKSTIYTKKIAVLKG
    QDLSPQQFLALGKRLGRPEAYYEPMYQHPEVTEIFVSSNVPENGKQIGVPKTGKFWHADYQFMPDPFGITLIYPQ
    VIPEKNRGTYFIDMGRAYDRLPEDLKKEISGTYCRHSVRKYFKIRPHDVYRPISEIIEEVERKTPAVVQPTTFTH
    PMTGETVLYISEGFTVGIEDQDGKPLDEELLKRLFDATGQLDESFEHDNIHLQSFEQGDLLVWDNRSLIHRARHT
    TTPEPTVSYRVTVHDERKLHDGI---*
    >P1;6l6x_fill
    sequence:::::::::
    MKETAAAKFERQHMDSPDLGTGGGSGIEGRMQIDEQPGNAIGAAVEGFDHATASDADIDALKSTIYTKKIAVLKG
    QDLSPQQFLALGKRLGRPEAYYEPMYQHPEVTEIFVSSNVPENGKQIGVPKTGKFWHADYQFMPDPFGITLIYPQ
    VIPEKNRGTYFIDMGRAYDRLPEDLKKEISGTYCRHSVRKYFKIRPHDVYRPISEIIEEVERKTPAVVQPTTFTH
    PMTGETVLYISEGFTVGIEDQDGKPLDEELLKRLFDATGQLDESFEHDNIHLQSFEQGDLLVWDNRSLIHRARHT
    TTPEPTVSYRVTVHDERKLHDGIQAA*
    `

    """

    return

def modeller_step2(pdb_code, chain, missing_residues):
    """
    Models in missing residues.

    Parameters
    ----------
    pdb_code: str
        The PDB code of the protein to be modelled.
    chain: str
        The letter of the chain given as input to Modeller.
    missing_residues : list[int]
        A list of the indices of the missing amino acids

    """
    log.verbose()
    env = Environ()

    # directories for input atom files
    env.io.atom_files_directory = [".", "../atom_files"]

    class MyModel(AutoModel):
        def select_atoms(self):
            return Selection(
                self.residue_range(f"1:{chain}", f"1:{chain}"),
                self.residue_range(f"134:{chain}", f"136:{chain}"),
                self.residue_range(f"218:{chain}", f"231:{chain}"),
            )

    a = MyModel(env, alnfile=f"{pdb_code}.ali", knowns=pdb_code, sequence=f"{pdb_code}_fill")

    a.starting_model = 1
    a.ending_model = 1

    a.make()

if __name__ == "__main__":
    # Initialize variables that can be obtained from protein3D
    pdb_code = "1qg8"
    chain = "A"
    missing_residues = [1,134,135,136,218,219,220,221,222,223,224,225,226,227,228,229,230,231]

    
    # Modeller workflow
    # 1. Generates the .seq file
    modeller_step1(pdb_code)
    # 2. Creates an .ali file from the .seq file
    get_alignment_file(pdb_code, missing_residues)
    # 3. Adds the missing residues
    modeller_step2(pdb_code, chain, missing_residues)