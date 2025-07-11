#!/usr/bin/env python3
"""
orca_irc_cleanup.py
===================

Utility to purge non‑essential files left over from an ORCA **I**ntrinsic **R**eaction **C**oordinate (IRC) job.

Safety features
---------------
1. **IRC verification** – The script aborts unless **at least one** ``*.out`` file in the working directory
   contains the phrase ``"Storing full IRC trajectory in"`` (case‑sensitive), which ORCA prints only for
   IRC runs.
2. **Interactive confirmation** – A simple "Continue? (y/N):" prompt; default is **No**.
3. **Scope limited to CWD** – Only files directly in the current working directory are affected.

Examples
--------
$ cd /path/to/irc_job  # <- run inside the job dir
$ python orca_irc_cleanup.py
Identified 8 left over files from the IRC calculation. Continue? (y/N): y
Deleted 8 files.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List, Set

ALLOWED_EXTS: Set[str] = {
    ".sh", ".out", ".in", ".gbw", ".xyz", ".densities", ".densitiesinfo", ".engrad",
}

MARKER = "Storing full IRC trajectory in"


def is_irc_directory(path: Path) -> bool:
    """Return *True* if any ``*.out`` file under *path* contains ``MARKER``.

    Parameters
    ----------
    path
        Directory expected to hold ORCA output files.

    Notes
    -----
    Reads files line‑by‑line and stops at the first match.
    """
    for out_file in path.glob("*.out"):
        try:
            with out_file.open("r", errors="ignore") as f:
                for line in f:
                    if MARKER in line:
                        return True
        except OSError:
            continue  # unreadable file – just skip
    return False


def find_leftovers(path: Path) -> List[Path]:
    """Return list of files lacking extensions in ``ALLOWED_EXTS``."""
    return [p for p in path.iterdir() if p.is_file() and p.suffix.lower() not in ALLOWED_EXTS]


def main() -> None:  # noqa: D401
    """Script entry point."""
    cwd = Path(".").resolve()

    if not is_irc_directory(cwd):
        sys.exit("This directory does not appear to be an ORCA IRC calculation (marker not found).")

    leftovers = find_leftovers(cwd)
    count = len(leftovers)
    if count == 0:
        print("No extraneous files found. Nothing to do.")
        return

    print(f"You are located in: {os.getcwd()}")
    response = input(
        f"Identified {count} left over file{'s' if count != 1 else ''} from the IRC calculation. "
        "Continue? (y/N): "
    ).strip().lower()
    if response != "y":
        print("Aborted.")
        return

    deleted = 0
    for fp in leftovers:
        try:
            fp.unlink()
            deleted += 1
        except Exception as exc:
            print(f"Could not delete {fp}: {exc}", file=sys.stderr)

    print(f"Deleted {deleted} file{'s' if deleted != 1 else ''}.")


if __name__ == "__main__":
    main()
