"""Combines separate PDBs into a single ensemble."""

import os
import shutil


def pdb_ensemble_generator():
    model_count = 1
    dir = "ensemble"
    if os.path.exists(dir):
        shutil.rmtree(dir)
        os.makedirs(dir)
    else:
        os.makedirs(dir)
    with open("./ensemble/ensemble.pdb", "a") as ensemble:
        for file in os.listdir("."):
            if file.endswith(".pdb"):
                ensemble.write("MODEL        {}\n".format(model_count))
                with open(file, "r") as current_pdb:
                    for line in current_pdb:
                        if line[:4] == "ATOM":
                            ensemble.write(line)
                        elif line[:3] == "TER":
                            ensemble.write(line + "ENDMDL\n")
                    model_count += 1


if __name__ == "__main__":
    pdb_ensemble_generator()
