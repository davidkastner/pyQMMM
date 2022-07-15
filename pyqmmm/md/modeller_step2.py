from modeller import *
from modeller.automodel import *    # Load the AutoModel class

def modeller_step2():
    log.verbose()
    env = Environ()

    # directories for input atom files
    env.io.atom_files_directory = ['.', '../atom_files']
    code = input("Enter a PDB accession: ")

    class MyModel(AutoModel):
        def select_atoms(self):
            return Selection(self.residue_range('1:A', '10:A'),self.residue_range('169:A', '173:A'))

    a = MyModel(env, alnfile = '{}.ali'.format(code),
                knowns = code, sequence = '{}_fill'.format(code))
    a.starting_model= 1
    a.ending_model  = 1

    a.make()

# Execute the function when run as a script but not if used as a pyQM/MM module
if __name__ == "__main__":
    modeller_step2()