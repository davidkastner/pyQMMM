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
@click.help_option('--help', '-h', is_flag=True, help='Exiting pyQMMM.')
def md(
    gbsa_analysis,
    ):
    """
    Functions for molecular dynamics (MD) simulations.

    """
    click.echo("> Analyze a GBSA calculation output:")
    click.echo("> Loading...")
    import pyqmmm.md.gbsa_analyzer
    # Run the GBSA analysis
    pyqmmm.md.gbsa_analyzer.analyze()

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
