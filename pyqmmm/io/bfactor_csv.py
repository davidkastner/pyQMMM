#!/usr/bin/env python3
"""
Transfer a per-residue numeric column from a CSV into the B-factor column of a PDB.

- Prompts for CSV path, PDB path, and the CSV column to transfer.
- CSV must identify residues by columns (case-insensitive):
    * Chain   -> one of: ["chain", "Chain", "CHAIN"] (optional; blank if absent)
    * ResSeq  -> one of: ["resseq","resseqid","resnum","res_seq","residue","Residue","resid","ResID","ResSeq"] (required)
    * ICode   -> one of: ["icode","inscode","insertion","iCode","ICode"] (optional; blank if absent)
- Column chosen must be numeric; duplicates per residue key are not allowed.
- Every residue present in the PDB must be present exactly once in the CSV mapping.
- Non-ATOM/HETATM (e.g., HEADER, TER, REMARK) are preserved as-is.
- Output: <pdb_stem>_bfactor_from_csv_<col>.pdb
"""

import os
import re
import sys
import pandas as pd
from typing import Tuple, Optional

# ---------------------------- Helpers ---------------------------- #

def die(msg: str, code: int = 1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)

def ask_path(prompt: str, default: Optional[str] = None) -> str:
    if default:
        s = input(f"{prompt} [{default}]: ").strip()
        return s or default
    return input(f"{prompt}: ").strip()

def is_atom_record(line: str) -> bool:
    rec = line[:6]
    return rec == "ATOM  " or rec == "HETATM"

def residue_key_from_pdb_line(line: str) -> Tuple[str, str, str]:
    """Return (chain, resseq, icode) from ATOM/HETATM line."""
    chain = line[21].strip()
    resseq = line[22:26].strip()  # keep as string (handles e.g., '401')
    icode = line[26].strip()      # insertion code
    return (chain, resseq, icode)

def format_bfactor(line: str, b: float) -> str:
    """Overwrite B-factor (cols 61-66, 1-based) with {:6.3f}, preserve occupancy."""
    nl = "\n" if line.endswith("\n") else ""
    core = line[:-1] if nl else line
    if len(core) < 66:
        core = core + " " * (66 - len(core))
    return core[:60] + f"{b:6.3f}" + core[66:] + nl

def find_column(df: pd.DataFrame, candidates) -> Optional[str]:
    for c in candidates:
        if c in df.columns:
            return c
    # case-insensitive
    lower_map = {c.lower(): c for c in df.columns}
    for c in candidates:
        if c.lower() in lower_map:
            return lower_map[c.lower()]
    return None

def sanitize_for_filename(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s).strip("_")

# ---------------------------- Main ---------------------------- #

def main():
    # Prompt for inputs
    csv_path = ask_path("CSV file", "values.csv")
    pdb_path = ask_path("PDB file", "structure.pdb")

    if not os.path.isfile(csv_path):
        die(f"CSV not found: {csv_path}")
    if not os.path.isfile(pdb_path):
        die(f"PDB not found: {pdb_path}")

    # Read CSV
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        die(f"Failed to read CSV: {e}")

    # Identify residue key columns
    chain_col = find_column(df, ["chain", "Chain", "CHAIN"])
    resseq_col = find_column(df, ["resseq","resseqid","resnum","res_seq","residue","Residue","resid","ResID","ResSeq"])
    icode_col = find_column(df, ["icode","inscode","insertion","iCode","ICode"])

    if resseq_col is None:
        die("Could not find a residue sequence column in CSV. "
            "Expected one of: ResSeq, resseq, resnum, residue, resid, etc.")

    # Normalize key columns
    df_keys = pd.DataFrame()
    df_keys["Chain"] = df[chain_col].fillna("").astype(str) if chain_col else ""
    df_keys["ResSeq"] = df[resseq_col].astype(str).str.strip()
    df_keys["ICode"] = df[icode_col].fillna("").astype(str).str.strip() if icode_col else ""

    # Choose value column (prompt)
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if not numeric_cols:
        die("CSV has no numeric columns to transfer.")
    print("\nNumeric columns available to transfer:")
    for i, c in enumerate(numeric_cols, 1):
        print(f"  {i}. {c}")
    col_name = input("Enter the exact column name to transfer (or number): ").strip()
    if col_name.isdigit():
        idx = int(col_name) - 1
        if idx < 0 or idx >= len(numeric_cols):
            die("Invalid column selection.")
        value_col = numeric_cols[idx]
    else:
        if col_name not in df.columns:
            die(f"Column '{col_name}' not found in CSV.")
        if not pd.api.types.is_numeric_dtype(df[col_name]):
            die(f"Column '{col_name}' is not numeric.")
        value_col = col_name

    # Build residue->value map; require uniqueness & non-NA
    df_map = pd.concat([df_keys, df[[value_col]]], axis=1)
    if df_map[value_col].isna().any():
        bad = df_map[df_map[value_col].isna()][["Chain","ResSeq","ICode"]].head(10).to_dict("records")
        die(f"Selected column has NA values; first 10 offending residue keys: {bad}")

    # Enforce unique rows per residue key
    dup_mask = df_map.duplicated(subset=["Chain","ResSeq","ICode"], keep=False)
    if dup_mask.any():
        dups = df_map.loc[dup_mask, ["Chain","ResSeq","ICode"]].value_counts().head(10)
        die("CSV contains duplicate rows for the same residue key. "
            f"First 10 duplicates (key -> count):\n{dups}")

    # Convert to dict
    value_by_key = {
        (row.Chain, row.ResSeq, row.ICode): float(row[value_col])
        for row in df_map.itertuples(index=False)
    }

    # Read PDB & collect residue keys
    with open(pdb_path, "r") as f:
        pdb_lines = f.readlines()

    atom_keys = []
    atom_idx = []
    for i, ln in enumerate(pdb_lines):
        if is_atom_record(ln):
            atom_idx.append(i)
            atom_keys.append(residue_key_from_pdb_line(ln))

    if not atom_idx:
        die("No ATOM/HETATM records found in PDB.")

    # Compute set of residues present in the PDB
    pdb_residues = sorted(set(atom_keys))

    # Check coverage: every PDB residue must be in CSV mapping
    missing = [k for k in pdb_residues if k not in value_by_key]
    extra = [k for k in value_by_key.keys() if k not in set(pdb_residues)]

    if extra:
        print(f"NOTE: {len(extra)} CSV residue keys not present in PDB (they will be ignored). "
              f"Example: {extra[:5]}")
    if missing:
        preview = missing[:10]
        die(f"CSV does not cover all PDB residues. Missing {len(missing)} residues. "
            f"First 10 missing keys: {preview}")

    # Write output with updated B-factors
    out_lines = list(pdb_lines)
    for i, rk in zip(atom_idx, atom_keys):
        bval = value_by_key[rk]
        out_lines[i] = format_bfactor(out_lines[i], bval)

    stem, _ = os.path.splitext(pdb_path)
    out_col = sanitize_for_filename(value_col)
    out_path = f"{stem}_bfactor_from_csv_{out_col}.pdb"
    with open(out_path, "w") as f:
        f.writelines(out_lines)

    # Summary
    print("\nSuccess.")
    print(f"  Wrote: {out_path}")
    print(f"  ATOM/HETATM updated: {len(atom_idx)}")
    print(f"  Residues in PDB:     {len(pdb_residues)}")
    print(f"  CSV residues used:    {len(value_by_key)} (extras ignored: {len(extra)})")
    print(f"  Column transferred:   {value_col}")

if __name__ == "__main__":
    main()
