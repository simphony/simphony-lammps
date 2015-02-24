simphony-lammps
===============

The lammps wrapper for the simphony framework

.. image:: https://travis-ci.org/simphony/simphony-lammps-md.svg?branch=master
    :target: https://travis-ci.org/simphony/simphony-lammps-md

Repository
----------

simphony-lammps is hosted on github: https://github.com/simphony/simphony-lamps-md

Installation
------------

The package requires python 2.7.x, installation is based on setuptools::

    # build and install
    python setup.py install

or::

    # build for in-place development
    python setup.py develop

Testing
-------

To run the full test-suite run::

    python -m unittest discover


Directory structure
-------------------

There are three subpackages:

- wrapper -- to hold the wrapper implementation
- bench -- holds basic benchmarking code
- examples -- holds different examples
