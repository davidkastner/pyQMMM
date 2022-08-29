from modeller import *
from modeller.automodel import *


def modeller_step1():
    """
    Takes a PDB accession when prompted and generates a sequence file
    """
    code = input("Enter a PDB accession: ")
    e = Environ()
    m = Model(e, file=code)
    aln = Alignment(e)
    aln.append_model(m, align_codes=code)
    aln.write(file=code + ".seq")
    print("A sequence file for {} was generated.".format(code))


def modeller_step2():
    log.verbose()
    env = Environ()

    # directories for input atom files
    env.io.atom_files_directory = [".", "../atom_files"]
    code = input("Enter a PDB accession: ")

    class MyModel(AutoModel):
        def select_atoms(self):
            return Selection(
                self.residue_range("1:A", "10:A"), self.residue_range("169:A", "173:A")
            )

    a = MyModel(
        env, alnfile="{}.ali".format(code), knowns=code, sequence="{}_fill".format(code)
    )
    a.starting_model = 1
    a.ending_model = 1

    a.make()
