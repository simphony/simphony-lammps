simphony-lammps
===============

The LAMMPS engine-wrapper for the SimPhoNy framework (www.simphony-project.eu).

.. image:: https://travis-ci.org/simphony/simphony-lammps-md.svg?branch=master
    :target: https://travis-ci.org/simphony/simphony-lammps-md
      :alt: Build status

.. image:: https://coveralls.io/repos/simphony/simphony-lammps-md/badge.svg
   :target: https://coveralls.io/r/simphony/simphony-lammps-md
      :alt: Test coverage

Repository
----------

simphony-lammps is hosted on github: https://github.com/simphony/simphony-lammps-md

Requirements
------------

- enum34 >= 1.0.4
- pyyaml >= 3.11
 - `simphony-common`_ >= 0.0.1


Installation
------------

The package requires python 2.7.x. Installation is based on setuptools::

    # build and install
    python setup.py install

or::

    # build for in-place development
    python setup.py develop

LAMMPS installation
~~~~~~~~~~~~~~~~~~~

This engine-wrapper uses LAMMPS Molecular Dynamics Simulator. The engine wrapper assumes that there is an executable called "lammps" that can be found in the PATH and an exception is thrown if this is not the case.

A recent stable version (9 Dec 2014, tagged r12824) of LAMMPS is supported and has been tested. See ``install_lammps.sh`` for an example installation instructions. For further information, see http://lammps.sandia.gov/index.html

Usage
-----

After installation, the user should be able to import the ``lammps`` engine plugin module by::

  from simphony.engine import lammps
    wrapper = lammps.LammpsWrapper()


Testing
-------

To run the full test-suite run::

    python -m unittest discover


Directory structure
-------------------

- simlammps -- hold the lammps-md wrapper implementation
- examples -- holds different examples

.. _simphony-common: https://github.com/simphony/simphony-common
