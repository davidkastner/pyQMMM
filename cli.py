"""Command-line interface (CLI) entry point."""

# Print first to welcome the user while it waits to load the modules
print("\n.---------------------------.")
print("| WELCOME TO THE PYQMMM CLI |")
print(".---------------------------.")
print("Default programmed actions for the pyQMMM package.")
print("GitHub: https://github.com/davidkastner/pyqmmm")
print("Documenation: https://pyqmmm.readthedocs.io\n")
print("""
    The overall command-line interface (CLI) entry point.
    The CLI interacts with the rest of the package.
    The CLI is advantagous as it summarizes the scope of the package,
    and improves long-term maintainability and readability.\n
    """)

import os
import click

@click.command()
@click.option("--gbsa_analysis", "-g", is_flag=True, help="Extract results from GBSA analysis.")
@click.option("--compute_hbond", "-hc", is_flag=True, help="Calculates hbonds with cpptraj.")
@click.option("--hbond_analysis", "-ha", is_flag=True, help="Extract Hbonding patterns from MD.")
@click.option("--last_frame", "-lf", is_flag=True, help="Get last frame from an AMBER trajectory.")
@click.option("--residue_list", "-lr", is_flag=True, help="Get a list of all residues in a PDB.")
@click.option("--colored_rmsd", "-cr", is_flag=True, help="Color RMSD by clusters.")
@click.option("--restraint_plot", "-rp", is_flag=True, help="Restraint plot KDE's on one plot.")
@click.help_option('--help', '-h', is_flag=True, help='Exiting pyQMMM.')
def md(
    gbsa_analysis,
    compute_hbond,
    hbond_analysis,
    last_frame,
    residue_list,
    colored_rmsd,
    restraint_plot,
    ):
    """
    Functions for molecular dynamics (MD) simulations.

    """
    if gbsa_analysis:
        click.echo("> Analyze a GBSA calculation output:")
        click.echo("> Loading...")
        import pyqmmm.md.gbsa_analyzer
        pyqmmm.md.gbsa_analyzer.analyze()

    elif compute_hbond:
        click.echo("> Compute all hbonds between the protein and the substrate using CPPTraj:")
        click.echo("> Loading...")
        import pyqmmm.md.hbond_analyzer
        import pyqmmm.md.amber_toolkit
        protein_id = input("What is the name of your protein (e.g., DAH)? ")
        substrate_index = input("What is the index of your substrate (e.g., 355)? ")
        residue_range = input("What is the range of residues in your protein (e.g., 1-351)? ")
        hbonds_script = pyqmmm.md.amber_toolkit.calculate_hbonds_script(protein_id, substrate_index, residue_range)
        submit_script = pyqmmm.md.amber_toolkit.submit_script(protein_id, "hbonds.in")
        pyqmmm.md.hbond_analyzer.compute_hbonds(hbonds_script, submit_script, "hbonds.in")

    elif hbond_analysis:
        click.echo("> Extract and plot hbonding patterns from an MD simulation:")
        click.echo("> Loading...")
        import pyqmmm.md.hbond_analyzer
        # Include more than one path in the list to perform multiple analyses
        file_paths = ["./"]
        names = ["unrestrained"]
        substrate = input("   > What is the resid of your substrate? (e.g., DCA) ")
        pyqmmm.md.hbond_analyzer.analyze_hbonds(file_paths, names, substrate)

    elif last_frame:
        click.echo("> Extracting the last frame from a MD simulation:")
        click.echo("> Loading...")
        import pyqmmm.md.amber_toolkit

        prmtop = input("What is your prmtop file? ")
        mdcrd = input("What is your trajectory file (e.g., nc or mdcrd)? ")
        output_pdb = input("What should you output PDB be called? ")

        pyqmmm.md.amber_toolkit.get_lastframe(prmtop, mdcrd, output_pdb)
        
    elif residue_list:
        click.echo("> Extract the residues from a PDB:")
        click.echo("> Loading...")
        import pyqmmm.md.residue_lister
        pyqmmm.md.residue_lister.list_residues()

    elif residue_list:
        click.echo("> Color a MD trajectory by clusters:")
        click.echo("> Loading...")
        import pyqmmm.md.rmsd_clusters_colorcoder
        pyqmmm.md.rmsd_clusters_colorcoder.rmsd_clusters_colorcoder()

    elif restraint_plot:
        click.echo("> Generate single KDE plot with hyscore measurements:")
        click.echo("> Loading...")
        import pyqmmm.md.kde_restraint_plotter
        pyqmmm.md.kde_restraint_plotter.restraint_plot()

@click.command()
@click.option("--plot_energy", "-pe", is_flag=True, help="Plot the energy of a xyz traj.")
@click.option("--flip_xyz", "-f", is_flag=True, help="Reverse and xyz trajectory.")
@click.option("--plot_mechanism", "-pm", is_flag=True, help="Plot energies for all steps of a mechanism.")
@click.help_option('--help', '-h', is_flag=True, help='Exiting pyQMMM.')
def qm(
    plot_energy,
    flip_xyz,
    plot_mechanism,
    ):
    """
    Functions for quantum mechanics (QM) simulations.

    """
    if plot_energy:
        click.echo("> Plot xyz trajectory energies:")
        click.echo("> Loading...")
        import pyqmmm.qm.energy_plotter
        pyqmmm.qm.energy_plotter.plot_energies()

    if flip_xyz:
        click.echo("> Reverse an xyz trajectory:")
        click.echo("> Loading...")
        import pyqmmm.qm.xyz_flipper
        in_file = input("What is the name of the xyz trajectory to reverse (omit extenstion)? ")
        pyqmmm.qm.xyz_flipper.xyz_flipper(in_file)

    if plot_mechanism:
        click.echo("> Combine all mechanism energetics and plot:")
        click.echo("> Loading...")
        import pyqmmm.qm.mechanism_plotter
        pyqmmm.qm.mechanism_plotter.process_xyz_files()


if __name__ == "__main__":
    # Run the command-line interface when this script is executed
    job = input("Would you like to run an MD or QM task? (md/qm) ")
    if job == "md":
        md()
    elif job == "qm":
        qm()
    else:
        print(f"{job} is not a valid response.")
