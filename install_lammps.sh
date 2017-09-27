#!/bin/bash
echo "Checking out a recent stable version (from 11 Aug 2017)"
git clone git://github.com/lammps/lammps.git
cd lammps
git checkout tags/stable_11Aug2017

echo "Building LAMMPS executable"
cd src
make -j 5 ubuntu_simple
ln -s lmp_ubuntu_simple lammps

echo "Building LAMMPS shared library"
make -j 5 ubuntu_simple mode=shlib

echo "Installing LAMMPS shared library and python package"
make install-python

python -c 'import lammps as l;l.lammps(cmdargs=["-l", "none"]).command("print `He from LAMMPS`")'