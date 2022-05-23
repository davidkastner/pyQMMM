Getting Started
===============

This page details how to get started with pyQMMM. 

Installation
------------

Usage
-----
Once installed, you can use the package. This example draws a benzene molecule from an xyz file.
::

    import pyqmmm

    benzene_symbols, benzene_coords = molecool.open_xyz('benzene.xyz')
    benzene_bonds = molecool.build_bond_list(benzene_coords)
    molecool.draw_molecule(benzene_coords, benzene_symbols, draw_bonds=benzene_bonds)