"""Command-line interface (CLI) entry point."""

import os
import click

def welcome():
    click.secho("\n")
    click.secho(r" ╔════════════════════════════════════════════════╗")
    click.secho(r" ║                  ___  __  __ __  __ __  __     ║")
    click.secho(r" ║     _ __  _   _ / _ \|  \/  |  \/  |  \/  |    ║")
    click.secho(r" ║    | '_ \| | | | | | | |\/| | |\/| | |\/| |    ║")
    click.secho(r" ║    | |_) | |_| | |_| | |  | | |  | | |  | |    ║")
    click.secho(r" ║    | .__/ \__, |\__\_\_|  |_|_|  |_|_|  |_|    ║")
    click.secho(r" ║    |_|    |___/                                ║")
    click.secho(r" ║                       pyQMMM                   ║")
    click.secho(r" ║                   [pyqmmm.rtfd.io]             ║")
    click.secho(r" ╚══════════════════════════╗╔════════════════════╝")
    click.secho(r"                    ╔═══════╝╚═══════╗             ")
    click.secho(r"                    ║  David Kastner ║             ")
    click.secho(r"                    ╚═══════╗╔═══════╝             ")
    click.secho(r"      ╔═════════════════════╝╚══════════════════╗  ")
    click.secho(r"      ║  Code: github.com/davidkastner/pyqmmm   ║  ")
    click.secho(r"      ║  Docs: pyqmmm.readthedocs.io            ║  ")
    click.secho(r"      ║     - IO: pyqmmm io --help              ║  ")
    click.secho(r"      ║     - MD: pyqmmm md --help              ║  ")
    click.secho(r"      ║     - QM: pyqmmm qm --help              ║  ")
    click.secho(r"      ║     - QMMM: pyqmmm qmmmm --help         ║  ")
    click.secho(r"      ╚═════════════════════════════════════════╝  ")

welcome()

@click.group()
def cli():
    """CLI entry point"""
    pass


@cli.command()
@click.option("--ppm2png", "-p2p", is_flag=True, help="Converts PPM files to PNG.")
@click.option("--delete_xyz_atoms", "-dxa", is_flag=True, help="Deletes atoms from XYZ trajectory.")
@click.option("--delete_pdb_atoms", "-dpa", is_flag=True, help="Deletes atoms from PDB trajectory.")
@click.option("--translate_pdb_to_center", "-tc", is_flag=True, help="Translates PDB traj to new center.")
@click.option("--xyz2pdb", "-x2p", is_flag=True, help="Converts an xyz file or traj to a PDB.")
def io(
    ppm2png,
    delete_xyz_atoms,
    delete_pdb_atoms,
    translate_pdb_to_center,
    xyz2pdb,
    ):
    """
    Tools for useful manipulations of common file types.

    """
    if ppm2png:
        click.echo("Converting all PPM in current directory to PNGs:")
        click.echo("Loading...")
        import pyqmmm.io.ppm2png_converter
        pyqmmm.io.ppm2png_converter.ppm2png_converter()

    elif delete_xyz_atoms:
        click.echo("Deleting requested atoms from the xyz file:")
        click.echo("Loading...")
        import pyqmmm.io.delete_xyz_trj_atoms
        import sys
        import glob
        in_files = glob.glob("delete.in")
        if len(in_files) == 0:
            print("Error: There should be a delete.in in the current directory indicating which atoms to delete.\n")
            print("As an example, its contents could look like this:")
            print("  1-8,104-106,166 # Asn")
            print("  9-16,107-109,168 # Asn")
            print("  59-69,134,135   # Phe\n")
            sys.exit(1)
        xyz_name = input("What is the name of the XYZ file you want to delete atoms from without the extension? ")
        xyz_input = f"{xyz_name}.xyz"
        xyz_output = f"{xyz_name}_stripped.xyz"
        pyqmmm.io.delete_xyz_trj_atoms.main(in_files, xyz_input, xyz_output)

    elif delete_pdb_atoms:
        click.echo("Deleting requested atoms from the PDB file:")
        click.echo("Loading...")
        import pyqmmm.io.delete_pdb_trj_atoms
        import sys
        import glob
        in_files = glob.glob("delete.in")
        if len(in_files) == 0:
            print("Error: There should be a delete.in in the current directory indicating which atoms to delete.\n")
            print("As an example, its contents could look like this:")
            print("  1-8,104-106,166 # Asn")
            print("  9-16,107-109,168 # Asn")
            print("  59-69,134,135   # Phe\n")
            sys.exit(1)
        pdb_name = input("What is the name of the PDB file you want to delete atoms from without the extension? ")
        pdb_input = f"{pdb_name}.pdb"
        pdb_output = f"{pdb_name}_stripped.pdb"
        pyqmmm.io.delete_pdb_trj_atoms.main(in_files, pdb_input, pdb_output)

    elif translate_pdb_to_center:
        click.echo("Translates PDB traj to a new center")
        click.echo("Loading...")
        import pyqmmm.io.translate_pdb_to_center
        input_pdb = input("What is the name of the PDB you would like to center? ") + ".pdb"
        center_point = int(input("What atom would you like to make the new center of your trajectory (atom number)? ")) # Indexed at 1
        output_pdb = "centered_pdb.pdb"
        pyqmmm.io.translate_pdb_to_center.translate_pdb(input_pdb, output_pdb, center_point)

    elif xyz2pdb:
        click.echo("Converts an xyz file to a PDB")
        click.echo("Loading...")
        import pyqmmm.io.xyz2pdb
        xyz_traj = input("What is the name or your xyz trajectory without the extension? ") + ".xyz"
        template = input("What is the name or your PDB template without the extension? ") + ".pdb"
        output_pdb = "pdb_trajectory.pdb"
        pyqmmm.io.xyz2pdb.xyz2pdb_traj(xyz_traj, output_pdb, template)


@cli.command()
@click.option("--gbsa_submit", "-gs", is_flag=True, help="Prepares and submits a mmGBSA job.")
@click.option("--gbsa_analysis", "-ga", is_flag=True, help="Extract results from GBSA analysis.")
@click.option("--compute_hbond", "-hc", is_flag=True, help="Calculates hbonds with cpptraj.")
@click.option("--hbond_analysis", "-ha", is_flag=True, help="Extract Hbonding patterns from MD.")
@click.option("--last_frame", "-lf", is_flag=True, help="Get last frame from an AMBER trajectory.")
@click.option("--residue_list", "-lr", is_flag=True, help="Get a list of all residues in a PDB.")
@click.option("--colored_rmsd", "-cr", is_flag=True, help="Color RMSD by clusters.")
@click.option("--restraint_plot", "-rp", is_flag=True, help="Restraint plot KDE's on one plot.")
@click.option("--strip_all", "-sa", is_flag=True, help="Strip waters and metals.")
@click.option("--dssp_plot", "-dp", is_flag=True, help="Generate a DSSP plot.")
@click.option("--rmsf", "-rmsf", is_flag=True, help="Calculates the RMSF.")
@click.option("--plot_rmsf", "-prmsf", is_flag=True, help="Plots RMSF.")
@click.option("--cc_coupling", "-cc", is_flag=True, help="Plots the results from cc coupling analysis.")
@click.option("--compare_distances", "-cd", is_flag=True, help="Plots distance metrics together.")
@click.option("--plot_rmsd", "-rmsd", is_flag=True, help="Plots the RMSD from CPPTraj.")
@click.option("--cluster_frames", "-cf", is_flag=True, help="Gets frames for largest CPPTraj cluster.")
@click.help_option('--help', '-h', is_flag=True, help='Exiting pyqmmm.')
def md(
    gbsa_submit,
    gbsa_analysis,
    compute_hbond,
    hbond_analysis,
    last_frame,
    residue_list,
    colored_rmsd,
    restraint_plot,
    strip_all,
    dssp_plot,
    rmsf,
    plot_rmsf,
    cc_coupling,
    compare_distances,
    plot_rmsd,
    cluster_frames,
    ):
    """
    Functions for molecular dynamics (MD) simulations.

    """
    if gbsa_submit:
        click.echo("Submit a mmGBSA job:")
        click.echo("Loading...")
        import pyqmmm.md.amber_toolkit
        protein_id = input("What is the id of your protein (e.g., taud, mc6)? ")
        ligand_id = input("What is the id of your ligand (e.g., hm1, tau)? ")
        ligand_index = input("What is the index of your ligand minus 1 if after the stripped metal? ")
        start = 100000
        stride = 50
        cpus = 8
        pyqmmm.md.amber_toolkit.gbsa_script(protein_id, ligand_id, ligand_index, start, stride, cpus)

    elif gbsa_analysis:
        click.echo("Analyze a GBSA calculation output:")
        click.echo("Loading...")
        import pyqmmm.md.gbsa_analyzer
        pyqmmm.md.gbsa_analyzer.analyze()

    elif compute_hbond:
        click.echo("Compute all hbonds between the protein and the substrate using CPPTraj:")
        click.echo("Loading...")
        import pyqmmm.md.hbond_analyzer
        import pyqmmm.md.amber_toolkit
        protein_id = input("What is the name of your protein (e.g., DAH)? ")
        substrate_index = input("What is the index of your substrate (e.g., 355)? ")
        residue_range = input("What is the range of residues in your protein (e.g., 1-351)? ")
        hbonds_script = pyqmmm.md.amber_toolkit.calculate_hbonds_script(protein_id, substrate_index, residue_range)
        submit_script = pyqmmm.md.amber_toolkit.submit_script(protein_id, "hbonds.in")
        pyqmmm.md.hbond_analyzer.compute_hbonds(hbonds_script, submit_script, "hbonds.in")

    elif hbond_analysis:
        click.echo("Extract and plot hbonding patterns from an MD simulation:")
        click.echo("Loading...")
        import pyqmmm.md.hbond_analyzer
        # Include more than one path in the list to perform multiple analyses
        file_paths = ["./"]
        names = ["unrestrained"]
        substrate = input("   What is the resid of your substrate? (e.g., DCA) ")
        pyqmmm.md.hbond_analyzer.analyze_hbonds(file_paths, names, substrate)

    elif last_frame:
        click.echo("Extracting the last frame from a MD simulation:")
        click.echo("Loading...")
        import pyqmmm.md.amber_toolkit
        prmtop = input("What is the path of your prmtop file? ")
        mdcrd = input("What is the path of your trajectory file? ")
        pyqmmm.md.amber_toolkit.get_last_frame(prmtop, mdcrd, "final_frame.pdb")
        
    elif residue_list:
        click.echo("Extract the residues from a PDB:")
        click.echo("Loading...")
        import pyqmmm.md.residue_lister
        pyqmmm.md.residue_lister.list_residues()

    elif colored_rmsd:
        click.echo("Color a MD trajectory by clusters:")
        click.echo("Loading...")
        import pyqmmm.md.rmsd_clusters_colorcoder
        yaxis_title = "RMSD (Å)"
        cluster_count = int(input("How many cluster would you like plotted? "))
        layout = input("Enter layout (e.g., 'square', '5,4', or press enter for default): ").strip() or "wide"
        legend_input = input("Show legend? (y/n): ").strip().lower()
        show_legend = legend_input != 'n'
        pyqmmm.md.rmsd_clusters_colorcoder.rmsd_clusters_colorcoder(yaxis_title, cluster_count, layout, show_legend)

    elif restraint_plot:
        click.echo("Generate single KDE plot with hyscore measurements:")
        click.echo("Loading...")
        import pyqmmm.md.kde_restraint_plotter
        pyqmmm.md.kde_restraint_plotter.restraint_plot()

    elif strip_all:
        click.echo("Strip waters and metals and create new traj and prmtop file:")
        click.echo("Loading...")
        import pyqmmm.md.amber_toolkit
        protein_id = input("What is the id of your protein (e.g., taud, mc6)? ")
        cpus = 8
        pyqmmm.md.amber_toolkit.strip_all_script(protein_id)
        pyqmmm.md.amber_toolkit.submit_script(protein_id, "strip.in", cpus)

    elif dssp_plot:
        click.echo("Create a DSSP plot from CPPTraj data:")
        click.echo("Loading...")
        import pyqmmm.md.dssp_plotter
        pyqmmm.md.dssp_plotter.combine_dssp_files()

    elif rmsf:
        import pyqmmm.md.rmsf_calculator
        pyqmmm.md.rmsf_calculator.main()
    
    elif plot_rmsf:
        import pyqmmm.md.rmsf_plotter
        pyqmmm.md.rmsf_plotter.main()

    elif cc_coupling:
        import pyqmmm.md.cc_coupling
        pyqmmm.md.cc_coupling.heatmap(
            data="cacovar.dat",
            delete=[],
            out_file="matrix_geom",
        )

    elif compare_distances:
        import pyqmmm.md.compare_distances
        files = input("What distance files would you like to plot? ").split(",")
        pyqmmm.md.compare_distances.get_plot(files)

    elif plot_rmsd:
        import pyqmmm.md.rmsd_plotter
        yaxis_title = "RMSD (Å)"
        layout = "wide"
        pyqmmm.md.rmsd_plotter.rmsd_plotter(yaxis_title, layout)

    elif cluster_frames:
        import pyqmmm.md.cluster_frame_indexer
        pyqmmm.md.cluster_frame_indexer.main()


@cli.command()
@click.option("--plot_energy", "-pe", is_flag=True, help="Plot the energy of a xyz traj.")
@click.option("--flip_xyz", "-f", is_flag=True, help="Reverse and xyz trajectory.")
@click.option("--plot_mechanism", "-pm", is_flag=True, help="Plot energies for all steps of a mechanism.")
@click.option("--residue_decomp", "-rd", is_flag=True, help="Analyze residue decomposition analysis.")
@click.option("--qm_replace_pdb", "-qr", is_flag=True, help="Replace QM optimized atoms in a pdb.")
@click.option("--bond_valence", "-bv", is_flag=True, help="Replace QM optimized atoms in a pdb.")
@click.option("--orca_scan", "-os", is_flag=True, help="Plots an ORCA scan.")
@click.option("--orca_neb_restart", "-rneb", is_flag=True, help="Prepare to restart an ORCA NEB.")
@click.option("--combine_nebs", "-cneb", is_flag=True, help="Combines and NEBs.")
@click.option("--plot_combine_nebs", "-pcneb", is_flag=True, help="Combines and plots NEBs as a single trajectory.")
@click.option("--extract_energies", "-ee", is_flag=True, help="Extract electronic energies")
@click.option("--extract_gibbs", "-eg", is_flag=True, help="Extract Gibbs free energies")
@click.help_option('--help', '-h', is_flag=True, help='Exiting pyqmmm.')
def qm(
    plot_energy,
    flip_xyz,
    plot_mechanism,
    residue_decomp,
    qm_replace_pdb,
    bond_valence,
    orca_scan,
    orca_neb_restart,
    combine_nebs,
    plot_combine_nebs,
    extract_energies,
    extract_gibbs,
    ):
    """
    Functions for quantum mechanics (QM) simulations.

    """
    if plot_energy:
        click.echo("Plot xyz trajectory energies:")
        click.echo("Loading...")
        import pyqmmm.qm.energy_plotter
        pyqmmm.qm.energy_plotter.plot_energies()

    if flip_xyz:
        click.echo("Reverse an xyz trajectory:")
        click.echo("Loading...")
        import pyqmmm.qm.xyz_flipper
        in_file = input("What is the name of the xyz trajectory to reverse (omit extenstion)? ")
        pyqmmm.qm.xyz_flipper.xyz_flipper(in_file)

    if plot_mechanism:
        click.echo("Combine all mechanism energetics and plot:")
        click.echo("Loading...")
        import pyqmmm.qm.mechanism_plotter
        color_scheme = input("What color scheme would you like (e.g., tab20, viridis)? ")
        pyqmmm.qm.mechanism_plotter.generate_plot(color_scheme)

    if residue_decomp:
        click.echo("Analyze residue decomposition jobs:")
        click.echo("Loading...")
        import pyqmmm.qm.residue_decomposition
        pyqmmm.qm.residue_decomposition.residue_decomposition()

    if qm_replace_pdb:
        click.echo("Replace PDB atoms with QM optimized atoms:")
        click.echo("Loading...")
        import pyqmmm.qm.replace_pdb
        protein = input("   What is the name of your protein (e.g., DAH, TAUD)? ")
        pdb_file_path = f"{protein}.pdb"
        xyz_file_path = "scr/optim.xyz"
        info_file_path = "../info.csv"
        output_file_path = f"./{protein}_optim.pdb"
        pyqmmm.qm.replace_pdb.replace_coordinates_in_pdb(pdb_file_path, xyz_file_path, info_file_path, output_file_path)

    if bond_valence:
        click.echo("Calculates and plots the bond valence for a mechanism:")
        click.echo("Loading...")
        import pyqmmm.qm.bond_valence
        try:
            # Check if the CSV file exists
            with open("bond_valence.csv"):
                print("   CSV file found. Plotting the data.")
                pyqmmm.qm.bond_valence.plot_bond_valence()
        except FileNotFoundError:
            print("   CSV file not found. Running Multiwfn analysis.")
            atom_pairs = [(145, 146), (65, 145), (66, 145), (12, 145), (32, 145), (145, 149)]
            pyqmmm.qm.bond_valence.calculate_bond_valence(atom_pairs, 4)
            pyqmmm.qm.bond_valence.plot_bond_valence()
            
    if orca_scan:
        import pyqmmm.qm.orca_scan_plotter
        atom_1 = input("   What is your first atom being scanned? ")
        atom_2 = input("   What is your second atom being scanned? ")
        distances, relative_energies = pyqmmm.qm.orca_scan_plotter.read_orca_output("orca.out")
        print(f"   Start distance: {distances[0]}, End distance: {distances[-1]}\n")
        pyqmmm.qm.orca_scan_plotter.plot_energy(distances, relative_energies, atom_1, atom_2)

    if orca_neb_restart:
        import pyqmmm.qm.orca_neb_restart
        pyqmmm.qm.orca_neb_restart.create_delete_folder()
        files_in_directory = [f for f in os.listdir() if f != 'delete']
        pyqmmm.qm.orca_neb_restart.move_files(files_in_directory)

    if combine_nebs:
        import pyqmmm.qm.combine_nebs
        pyqmmm.qm.combine_nebs.combine_trajectories()

    if plot_combine_nebs:
        import pyqmmm.qm.plot_combined_nebs
        pyqmmm.qm.plot_combined_nebs.plot_energies()

    if extract_gibbs:
        import pyqmmm.qm.extract_gibbs_free_energies
        pyqmmm.qm.extract_gibbs_free_energies.extract()

    if extract_energies:
        import pyqmmm.qm.extract_electronic_energies
        pyqmmm.qm.extract_electronic_energies.extract()


@cli.command()
@click.option("--quick_csa", "-csa", is_flag=True, help="Performs charge shift analysis.")
def qmmm(
    quick_csa,
    ):
    """
    Functions for multiscale QM/MM simulations.

    """
    if quick_csa:
        click.echo("Charge shift analysis:")
        click.echo("Loading...")
        import pyqmmm.qmmm.quickcsa
        pyqmmm.qmmm.quickcsa.quick_csa()
    

if __name__ == "__main__":
    # Run the command-line interface when this script is executed
    cli()
