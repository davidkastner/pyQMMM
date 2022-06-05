Getting Started
===============

This page details how to get started with the pyQMMM package.
The purpose of the package is to act as a library for MD, QM, and QM/MM simulations of proteins as well as a repository for useful scripts.

Installation
------------
Download the package from GitHub.


Usage
-----
Once installed, you can use the package. This example draws a benzene molecule from an xyz file.
::

    import pyqmmm

    benzene_symbols, benzene_coords = molecool.open_xyz('benzene.xyz')
    benzene_bonds = molecool.build_bond_list(benzene_coords)
    molecool.draw_molecule(benzene_coords, benzene_symbols, draw_bonds=benzene_bonds)