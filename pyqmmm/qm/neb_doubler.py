#!/usr/bin/env python3
from pathlib import Path
from typing import List, Tuple, Dict, Any
import os
import shutil
import subprocess
import sys

# -------------------------
# Minimal, clean progress bar
# -------------------------
def _progress_bar(iter_idx: int, total: int, width: int = 32, prefix: str = ""):
    frac = (iter_idx / total) if total else 1.0
    filled = int(round(width * frac))
    bar = "█" * filled + " " * (width - filled)
    sys.stdout.write(f"\r{prefix}[{bar}] {iter_idx}/{total}")
    sys.stdout.flush()
    if iter_idx >= total:
        sys.stdout.write("\n")
        sys.stdout.flush()

# -------------------------
# Light logging
# -------------------------
def _info(msg: str) -> None:
    print(msg, flush=True)

def _err(msg: str) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr, flush=True)

# -------------------------
# Core utilities
# -------------------------
def _parse_charge_spin(input_file: Path) -> Tuple[str, str]:
    if not input_file.exists():
        return None, None
    with input_file.open("r") as f:
        for line in f:
            s = line.strip()
            if s.startswith("* xyzfile"):
                parts = s.split()
                if len(parts) >= 4:
                    # parts[2] = charge, parts[3] = spin multiplicity
                    return parts[2], parts[3]
    return None, None

def _get_charge_spin(input_file: Path) -> Tuple[str, str]:
    charge, spin = _parse_charge_spin(input_file)
    if charge is None or spin is None:
        _info("Unable to auto-detect charge/spin from qmscript.in.")
        charge = input("Please enter the charge: ").strip()
        spin = input("Please enter the spin multiplicity: ").strip()
    return charge, spin

def _read_all_lines(path: Path) -> List[str]:
    with path.open("r") as f:
        return f.read().splitlines()

def _parse_allxyz(file_path: Path) -> List[str]:
    """
    Robust ORCA .allxyz parser:
    - Accepts '>' separators and extra blank lines.
    - Enforces consistent natoms across frames.
    Returns list of exact frame strings: "N\\nTitle\\n<natoms lines>".
    """
    if not file_path.exists():
        raise FileNotFoundError(f"{file_path} not found.")
    lines = _read_all_lines(file_path)
    i = 0
    frames = []
    natoms_set = set()

    def skip_seps(j):
        while j < len(lines) and (lines[j].strip() in {"", ">"}):
            j += 1
        return j

    while i < len(lines):
        i = skip_seps(i)
        if i >= len(lines):
            break
        try:
            natoms = int(lines[i].strip())
        except ValueError:
            raise ValueError(f"Expected integer atom count at line {i+1} in {file_path}")
        natoms_set.add(natoms)
        i += 1
        if i >= len(lines):
            raise ValueError("Unexpected EOF while reading title.")
        title = lines[i].rstrip()
        i += 1
        if i + natoms > len(lines):
            raise ValueError("Unexpected EOF while reading coordinates.")
        coords = lines[i:i+natoms]
        i += natoms
        frames.append("\n".join([str(natoms), title] + coords))
        i = skip_seps(i)

    if not frames:
        raise ValueError(f"No frames parsed in {file_path}")
    if len(natoms_set) != 1:
        raise ValueError("Inconsistent number of atoms across frames.")
    return frames

def _write_text(path: Path, text: str) -> None:
    with path.open("w") as f:
        f.write(text if text.endswith("\n") else text + "\n")

def _write_frame_xyz(frame_str: str, out_xyz: Path) -> None:
    _write_text(out_xyz, frame_str)

def _make_interpolate_input(charge: str, spin: str, nimages: int, nprocs: int, maxcore: int) -> str:
    s = (
        "! NEB-IDPP\n\n"
        "%neb\n"
        'NEB_End_XYZFile "end.xyz"\n'
        "Free_End true\n"
        f"NImages {nimages}\n"
        "end\n\n"
    )
    if nprocs > 1:
        s += f"%pal nprocs {nprocs} end\n\n"
    s += f"%maxcore {maxcore}\n\n"
    s += f"* xyzfile {charge} {spin} start.xyz\n"
    return s

def _run_orca_interpolation(module_cmd: str, orca_path: str, workdir: Path) -> None:
    cmd = (f"{module_cmd} > /dev/null 2>&1; " if module_cmd.strip() else "") + \
          f"{orca_path} interpolate.in > interpolate.out 2>&1"
    result = subprocess.run(["bash", "-lc", cmd], cwd=str(workdir), capture_output=True, text=True)
    if result.returncode != 0:
        _err("ORCA returned non-zero exit code.")
        out = workdir / "interpolate.out"
        if out.exists():
            try:
                tail = out.read_text().splitlines()[-60:]
                _err("Last ~60 lines of interpolate.out:\n" + "\n".join(tail))
            except Exception:
                _err("Could not read interpolate.out tail.")
        raise RuntimeError("ORCA interpolation failed.")
    if not (workdir / "interpolate_initial_path.allxyz").exists():
        raise FileNotFoundError("Missing 'interpolate_initial_path.allxyz' after ORCA run.")

def _extract_middle_frame(allxyz_path: Path, expected_nimages: int) -> str:
    frames = _parse_allxyz(allxyz_path)
    if len(frames) != expected_nimages:
        raise ValueError(
            f"Expected {expected_nimages} frames in {allxyz_path.name}, found {len(frames)}."
        )
    return frames[expected_nimages // 2]

# -------------------------
# Core doubling logic
# -------------------------
def _double_path(
    original_traj: Path,
    output_traj_allxyz: Path,
    output_traj_xyz: Path,
    input_file: Path,
    module_load_cmd: str,
    orca_path: str,
    archive_dir: Path,
    nprocs: int,
    maxcore: int,
    nimages: int,
    strict_double: bool,
) -> Dict[str, Any]:

    # Discover initial state for cleanup later
    initial_listing = set(os.listdir("."))
    archive_dir.mkdir(exist_ok=True)

    # Parse inputs first to assemble intro summary details
    frames = _parse_allxyz(original_traj)
    nframes = len(frames)
    if nframes < 2:
        raise ValueError("At least 2 frames are required in the input trajectory.")

    # Determine natoms for info line
    natoms = int(frames[0].splitlines()[0].strip())

    # Charge/spin (prompt if not found)
    charge, spin = _get_charge_spin(input_file)

    # Intro summary (with a little breathing room)
    print()
    _info("=== NEB EXPANSION DETAILS ===")
    _info(f"Input  : {original_traj.name}")
    _info(f"QM reference : {input_file.name}")
    _info(f"Outputs: {output_traj_allxyz.name} and {output_traj_xyz.name}")
    _info(f"PAL/max: nprocs={nprocs}, maxcore={maxcore} MB")
    _info(f"Module : {module_load_cmd if module_load_cmd.strip() else '(none)'}")
    _info(f"Run    : {orca_path} interpolate.in > interpolate.out")
    _info("[env] Loading ORCA module once...")
    _info(f"[input] Found {nframes} frames; {natoms} atoms/frame.")
    _info(f"[output] {2*nframes} frame expansion")
    _info("============================")
    print()

    # Build new frames via IDPP midpoints
    new_frames: List[str] = []
    total_pairs = nframes - 1

    # Progress bar
    _progress_bar(0, total_pairs, prefix="Progress ")

    for i in range(total_pairs):
        work = Path(f".neb_pair_{i+1:03d}")
        work.mkdir(exist_ok=True)

        _write_frame_xyz(frames[i], work / "start.xyz")
        _write_frame_xyz(frames[i + 1], work / "end.xyz")

        interpolate_in = _make_interpolate_input(charge, spin, nimages, nprocs, maxcore)
        _write_text(work / "interpolate.in", interpolate_in)

        _run_orca_interpolation(module_load_cmd, orca_path, work)
        mid_frame = _extract_middle_frame(work / "interpolate_initial_path.allxyz", nimages)

        new_frames.append(frames[i])
        new_frames.append(mid_frame)

        _progress_bar(i + 1, total_pairs, prefix="Progress ")

    # Append final original frame
    new_frames.append(frames[-1])

    # Strict pad to exactly 2*N frames (duplicate last) instead of extrapolating
    if strict_double and len(new_frames) == (2 * nframes - 1):
        new_frames.append(frames[-1])

    # Write outputs
    _write_text(output_traj_allxyz, "\n>\n".join(new_frames) + "\n")  # ORCA-style
    _write_text(output_traj_xyz, "\n".join(new_frames) + "\n")        # plain stacked XYZ

    # Cleanup/archive everything created this run except outputs, inputs, original, and the archive dir itself
    final_listing = set(os.listdir("."))
    created = final_listing - initial_listing
    keep = {
        original_traj.name,
        input_file.name if input_file.exists() else "",
        output_traj_allxyz.name,
        output_traj_xyz.name,
        archive_dir.name,  # don't move archive into itself
    }
    moved = []
    for name in sorted(created):
        if name in keep or not name:
            continue
        try:
            shutil.move(name, archive_dir / name)
            moved.append(name)
        except Exception as e:
            _err(f"Could not move '{name}' to archive: {e}")

    # Completion summary with spacing
    print()
    _info("=== Completed ===")
    _info(f"[result] Wrote: {output_traj_allxyz.name} ({len(new_frames)} frames, '>'-separated)")
    _info(f"[result] Wrote: {output_traj_xyz.name} ({len(new_frames)} frames, stacked XYZ)")
    _info(f"[archive] Moved {len(moved)} item(s) to ./{archive_dir}/")
    _info("================")
    print()

    return {
        "input_frames": nframes,
        "output_frames": len(new_frames),
        "natoms": natoms,
        "archived_items": moved,
        "output_allxyz": str(output_traj_allxyz),
        "output_xyz": str(output_traj_xyz),
    }

# -------------------------
# Public entry point (no CLI)
# -------------------------
def main(
    original: str = "restart.allxyz",
    output_allxyz: str = "restart_doubled.allxyz",
    output_xyz: str = "restart_doubled.xyz",
    input_file: str = "qmscript.in",
    module_load_cmd: str = "module load orca/6.0.0",
    orca_path: str = "/data1/groups/HJKgroup/src/orca/orca6/6.0.0/orca",
    archive_dir: str = "path_doubling_archive",
    nprocs: int = 1,
    maxcore: int = 3600,
    nimages: int = 3,
    strict_double: bool = True,
) -> Dict[str, Any]:
    """
    Double an ORCA NEB .allxyz trajectory by inserting NEB-IDPP midpoints between each pair.

    Parameters
    ----------
    original : str
        Input .allxyz (default: 'restart.allxyz')
    output_allxyz : str
        Output .allxyz with '>' separators (default: 'restart_doubled.allxyz')
    output_xyz : str
        Output stacked .xyz (default: 'restart_doubled.xyz')
    input_file : str
        Previous ORCA input to read charge/spin (default: 'qmscript.in')
    module_load_cmd : str
        Module load command, empty to skip (default: 'module load orca/6.0.0')
    orca_path : str
        Path to ORCA executable
    archive_dir : str
        Directory to move temporary artifacts
    nprocs : int
        PAL nprocs (default: 1)
    maxcore : int
        Maxcore per process in MB (default: 3600)
    nimages : int
        Total images for NEB-IDPP (odd >= 3): start + middle + end (default: 3)
    strict_double : bool
        If True, pad with last frame to reach exactly 2*N frames (no extrapolation)

    Returns
    -------
    dict
        Summary info with keys:
        ['input_frames','output_frames','natoms','archived_items','output_allxyz','output_xyz']
    """
    if nimages < 3 or nimages % 2 == 0:
        raise ValueError("nimages must be an odd integer >= 3 (e.g., 3, 5, ...).")

    return _double_path(
        original_traj=Path(original),
        output_traj_allxyz=Path(output_allxyz),
        output_traj_xyz=Path(output_xyz),
        input_file=Path(input_file),
        module_load_cmd=module_load_cmd,
        orca_path=orca_path,
        archive_dir=Path(archive_dir),
        nprocs=nprocs,
        maxcore=maxcore,
        nimages=nimages,
        strict_double=strict_double,
    )

# Optional: allow running directly with defaults (no CLI parsing)
if __name__ == "__main__":
    main()
