#!/usr/bin/env python3
"""
Calculate the RMSF across replicates using MDAnalysis.

INPUT-FILE FORMAT (first non-comment line is now optional CPU count)

    # How many cores to use
    cpus = 48

    # Topology and static reference
    /abs/path/to/system.prmtop
    /abs/path/to/reference.pdb

    # Trajectories  (nickname  full/path/to/trajectory.crd)
    rep1 /abs/path/to/rep1/constP_prod.crd
    rep2 /abs/path/to/rep2/constP_prod.crd
    …
"""

# ──────────────────────────────────────────────────────────────────────────────
# Standard libs
# ──────────────────────────────────────────────────────────────────────────────
from pathlib import Path
import multiprocessing as mp
import warnings
import textwrap
import re
import sys
import os
import time

# ──────────────────────────────────────────────────────────────────────────────
# Third-party libs
# ──────────────────────────────────────────────────────────────────────────────
import numpy as np
import pandas as pd
import MDAnalysis as mda
from MDAnalysis.analysis import align, rms

# ──────────────────────────────────────────────────────────────────────────────
# Pretty printing helpers
# ──────────────────────────────────────────────────────────────────────────────
RESET = "\033[0m"
RED   = "\033[1;31m"
GRN   = "\033[1;32m"
BLU   = "\033[1;34m"
YLW   = "\033[1;33m"

def die(msg: str, code: int = 1) -> None:
    print(f"{RED}❌ {msg}{RESET}", file=sys.stderr)
    sys.exit(code)

warnings.filterwarnings("ignore", category=UserWarning, module="MDAnalysis")

# ──────────────────────────────────────────────────────────────────────────────
# Core calculation
# ──────────────────────────────────────────────────────────────────────────────
def calculate_rmsf_per_trajectory(topology: str, trajectory: str,
                                  reference: mda.Universe,
                                  column_name: str) -> pd.DataFrame:
    """Compute per-residue RMSF for a single trajectory."""
    print(f"   > Reading  : {trajectory}")
    u = mda.Universe(topology, trajectory, dt=0.2, format="TRJ")

    align.AlignTraj(
        u, reference,
        select="backbone and resid 3-14 19-26 29 30",
        in_memory=True
    ).run()

    print(f"   > Computing: {trajectory}")
    rmsf_values = rms.RMSF(u.select_atoms("all")).run().results.rmsf

    rmsf_res, resnames, resids = [], [], []
    offset = min(u.atoms.indices)

    for res in u.atoms.residues:
        idx = [i - offset for i in res.atoms.indices]
        if max(idx) >= len(rmsf_values):
            print(f"Skipping residue {res.resname}{res.resid}")
            continue
        rmsf_res.append(np.mean(rmsf_values[idx]))
        resnames.append(res.resname)
        resids.append(res.resid)

    return pd.DataFrame(
        dict(ResID=resids, ResName=resnames, **{column_name: rmsf_res})
    )

# ──────────────────────────────────────────────────────────────────────────────
# Input-file parser
# ──────────────────────────────────────────────────────────────────────────────
_CPU_RE = re.compile(r"cpus?\s*(?:=)?\s*(\d+)", re.I)

def parse_rmsf_input_file(file_path: Path):
    """
    Returns
    -------
    n_cpus : int | None
    topology : str
    reference : str
    trajectories : list[tuple[str, str]]
    """
    n_cpus = None
    topology = reference = None
    trajs   = []

    for raw in file_path.read_text().splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue

        # 1) Optional CPU line
        m = _CPU_RE.fullmatch(line.replace(" ", ""))
        if m and n_cpus is None:
            n_cpus = int(m.group(1))
            continue

        # 2) Topology / reference
        if line.endswith(".prmtop"):
            if topology:
                die("Multiple .prmtop entries in input file.")
            topology = line
            continue

        if line.endswith(".pdb"):
            if reference:
                die("Multiple .pdb entries in input file.")
            reference = line
            continue

        # 3) Trajectory lines
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            die(f"Trajectory line must be 'name path':\n{raw}")
        name, path = parts
        trajs.append((name, path))

    if not (topology and reference):
        die("Input must contain one .prmtop line and one .pdb line.")

    return n_cpus, topology, reference, trajs

# ──────────────────────────────────────────────────────────────────────────────
# Example generator
# ──────────────────────────────────────────────────────────────────────────────
def print_example_input() -> None:
    print(textwrap.dedent(f"""{BLU}
        # Example rmsf.in
        cpus = 48
        /abs/path/to/system.prmtop
        /abs/path/to/reference.pdb
        rep1 /abs/path/to/rep1/constP_prod.crd
        rep2 /abs/path/to/rep2/constP_prod.crd
        {RESET}"""))

# ──────────────────────────────────────────────────────────────────────────────
# Main driver
# ──────────────────────────────────────────────────────────────────────────────
def main() -> None:
    print(f"{GRN}\n.-----------------.")
    print("| RMSF Calculator |")
    print(f".-----------------.{RESET}\n")
    print("Calculates the RMSF by residue.\n")

    in_files = list(Path(".").glob("*.in"))
    if not in_files:
        die("No .in file found in current directory.\n", code=0)

    in_file = in_files[0]
    print(f"{BLU}📄 Using input file: {in_file}{RESET}")

    n_cpus, top, ref, trajs = parse_rmsf_input_file(in_file)

    # ── path check ──────────────────────────────────────────────────────────
    missing = [p for p in (top, ref, *(p for _, p in trajs)) if not Path(p).is_file()]
    if missing:
        die("Missing file(s):\n  " + "\n  ".join(missing))

    # ── CPU logic ───────────────────────────────────────────────────────────
    if n_cpus is None:
        n_cpus = int(os.getenv("NSLOTS", mp.cpu_count()))
    n_cpus = max(1, min(n_cpus, mp.cpu_count()))
    print(f"{GRN}🧠 Using {n_cpus} CPU cores{RESET}")

    # ── Analysis ────────────────────────────────────────────────────────────
    t0 = time.time()
    reference = mda.Universe(ref)
    args = [(top, path, reference, name) for name, path in trajs]

    with mp.Pool(processes=n_cpus) as pool:
        dfs = pool.starmap(calculate_rmsf_per_trajectory, args)

    df = pd.concat(dfs, axis=1).T.drop_duplicates().T
    df["Avg. RMSF"] = df.iloc[:, 2:].mean(axis=1)
    df["Std. Dev"]  = df.iloc[:, 2:-1].std(axis=1)
    df.to_csv("rmsf.csv", index=False)

    dt = time.time() - t0
    print(f"""\n{YLW}------------------------- RMSF SUMMARY -------------------------
RESULT : Computed RMSF for {len(trajs)} trajectories
OUTPUT : rmsf.csv
TIME   : {dt:.2f} s
-----------------------------------------------------------------{RESET}\n""")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        die("Interrupted by user.", code=130)
