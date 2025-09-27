#!/usr/bin/env python3
"""
Replace the B-factor column of a PDB with residue-summed charges from a .chg file.

Behavior:
- Prompts for PDB and CHG filenames.
- Verifies:
    1) The total number of non-empty lines in PDB equals the number of data lines in CHG.
    2) The PDB contains NO 'TER' lines (will abort if found).
    3) Every non-empty PDB line is ATOM or HETATM (since we expect 1:1 with CHG lines).
- Sums charges per residue (chainID, resSeq, iCode) and writes that sum to the B-factor
  of every atom in the residue.
- Writes output as: <pdb_stem>_bfactor_charge.pdb (e.g., B401_B402_bfactor_charge.pdb)

Notes on .chg:
- Similar to XYZ but no header. We read the last whitespace-separated token as charge.
- The number/order of lines must exactly match the PDB atom order.
"""

import os
import sys
from collections import defaultdict

def ask_path(prompt, default):
    s = input(f"{prompt} [{default}]: ").strip()
    return s or default

def die(msg, code=1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)

def is_atom_record(line: str) -> bool:
    rec = line[:6]
    return rec == "ATOM  " or rec == "HETATM"

def residue_key(line: str):
    """Key residues by (chain_id, resseq, icode)."""
    chain_id = line[21].strip()
    resseq   = line[22:26].strip()
    icode    = line[26].strip()
    return (chain_id, resseq, icode)

def set_bfactor(line: str, b: float) -> str:
    """
    Return a copy of the PDB ATOM/HETATM line with B-factor (cols 61-66, 1-based)
    set to b, preserving occupancy (cols 55-60).
    """
    # Ensure at least up to col 66 exists
    if line.endswith("\n"):
        core, nl = line[:-1], "\n"
    else:
        core, nl = line, ""
    if len(core) < 66:
        core = core + " " * (66 - len(core))
    bstr = f"{b:6.3f}"
    # occupancy is cols 55-60 (0-based 54:60), B-factor 61-66 (0-based 60:66)
    out = core[:60] + bstr + core[66:] + nl
    return out

def read_charges_from_chg(path: str):
    charges = []
    with open(path, "r") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            try:
                charges.append(float(parts[-1]))
            except Exception as e:
                die(f"Failed to parse charge from line:\n{raw}\n{e}")
    if not charges:
        die("No charge lines found in .chg file.")
    return charges

def count_nonempty_lines(path: str):
    n = 0
    with open(path, "r") as f:
        for raw in f:
            if raw.strip():
                n += 1
    return n

def main():
    # ---- Prompt for filenames (with sensible defaults) ----
    default_pdb = "B401_B402.pdb"
    default_chg = "B401_B402.chg"
    pdb_in = ask_path("PDB file", default_pdb)
    chg_in = ask_path(".chg file", default_chg)

    if not os.path.isfile(pdb_in):
        die(f"PDB file not found: {pdb_in}")
    if not os.path.isfile(chg_in):
        die(f".chg file not found: {chg_in}")

    # ---- Quick line-count parity check (exact match expected) ----
    pdb_nonempty = count_nonempty_lines(pdb_in)
    chg_nonempty = count_nonempty_lines(chg_in)
    if pdb_nonempty != chg_nonempty:
        die(f"Line count mismatch: PDB has {pdb_nonempty} non-empty lines, "
            f"but CHG has {chg_nonempty}. These must be identical.")

    # ---- Load files ----
    with open(pdb_in, "r") as f:
        pdb_lines = [ln for ln in f]

    # ---- Disallow TER lines explicitly ----
    if any(ln.startswith("TER") for ln in pdb_lines):
        die("Found 'TER' lines in the PDB. "
            "This script expects a PDB with only ATOM/HETATM records and no TER.")

    # ---- Ensure every non-empty PDB line is ATOM/HETATM ----
    for ln in pdb_lines:
        if ln.strip() and not is_atom_record(ln):
            die("Found a non-ATOM/HETATM line in the PDB. "
                "For 1:1 mapping with .chg, the PDB must contain only ATOM/HETATM lines.")

    # ---- Read charges (must match line-for-line with PDB atoms) ----
    charges = read_charges_from_chg(chg_in)
    atom_count = sum(1 for ln in pdb_lines if ln.strip())
    if atom_count != len(charges):
        die(f"Atom/charge count mismatch after filtering: "
            f"PDB atoms={atom_count}, CHG charges={len(charges)}.")

    # ---- Build residue keys in order ----
    residue_keys = [residue_key(ln) for ln in pdb_lines if ln.strip()]

    # ---- Sum charges per residue ----
    res_sums = defaultdict(float)
    for q, rkey in zip(charges, residue_keys):
        res_sums[rkey] += q

    # ---- Create output lines with updated B-factors (no REMARK insertion) ----
    out_lines = []
    idx = 0
    for ln in pdb_lines:
        if ln.strip():  # ATOM/HETATM by earlier check
            rkey = residue_keys[idx]
            bval = res_sums[rkey]
            out_lines.append(set_bfactor(ln, bval))
            idx += 1
        else:
            out_lines.append(ln)  # preserve blank lines if any (shouldn't be)
    assert idx == len(charges)

    # ---- Derive output filename ----
    root, ext = os.path.splitext(pdb_in)
    pdb_out = f"{root}_bfactor_charge.pdb"

    with open(pdb_out, "w") as f:
        f.writelines(out_lines)

    # ---- Summary ----
    total_q = sum(charges)
    print(f"Wrote: {pdb_out}")
    print(f"Atoms processed: {atom_count}")
    print(f"Residues found:  {len(res_sums)}")
    print(f"Sum of CHG charges:            {total_q:.6f}")
    print(f"Sum of residue-summed charges: {sum(res_sums.values()):.6f}")

if __name__ == "__main__":
    main()
