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

import click

@click.command()
@click.option("--gbsa_analysis", "-g", is_flag=True, help="Extract results from GBSA analysis.")
@click.option("--hbond_analysis", "-hb", is_flag=True, help="Extract Hbonding patterns from MD.")
@click.option("--last_frame", "-lf", is_flag=True, help="Get last frame from an AMBER trajectory.")
@click.option("--residue_list", "-lr", is_flag=True, help="Get a list of all residues in a PDB.")
@click.option("--colored_rmsd", "-cr", is_flag=True, help="Color RMSD by clusters.")
@click.help_option('--help', '-h', is_flag=True, help='Exiting pyQMMM.')
def md(
    gbsa_analysis,
    hbond_analysis,
    last_frame,
    residue_list,
    colored_rmsd,
    ):
    """
    Functions for molecular dynamics (MD) simulations.

    """
    if gbsa_analysis:
        click.echo("> Analyze a GBSA calculation output:")
        click.echo("> Loading...")
        import pyqmmm.md.gbsa_analyzer
        pyqmmm.md.gbsa_analyzer.analyze()

    elif hbond_analysis:
        click.echo("> Extract and plot hbonding patterns from an MD simulation:")
        click.echo("> Loading...")
        import pyqmmm.md.hbonding_analyzer
        file_paths = ["/Users/kastner/Downloads/test/obtuse/", "/Users/kastner/Downloads/test/acute/"]
        names = ["acute", "obtuse"]
        substrate = "DHK"
        pyqmmm.md.hbonding_analyzer.analyze_hbonds(file_paths, names, substrate)

    elif last_frame:
        click.echo("> Extracting the last frame from a MD simulation:")
        click.echo("> Loading...")
        import pyqmmm.md.cpptraj_toolkit
        pyqmmm.md.cpptraj_toolkit.get_last_frame()

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

@click.command()
@click.option("--first_task", "-a", is_flag=True, help="The first task.")
@click.help_option('--help', '-h', is_flag=True, help='Exiting pyQMMM.')
def qm(
    combine_restarts,
    ):
    """
    Functions for quantum mechanics (QM) simulations.

    """
    click.echo("> Combine restarts:")
    click.echo("> Loading...")
    import pyqmmm.qm.task
    # Perform task

if __name__ == "__main__":
    # Run the command-line interface when this script is executed
    job = input("Would you like to run an MD or QM task? (md/qm) ")
    if job == "md":
        md()
    elif job == "qm":
        qm()
    else:
        print(f"{job} is not a valid response.")
