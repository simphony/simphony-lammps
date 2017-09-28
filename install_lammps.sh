#!/bin/bash
echo "Checking out a recent stable version (from 11 Aug 2017)"
git clone git://github.com/lammps/lammps.git
cd lammps
git checkout tags/stable_11Aug2017

echo "Building LAMMPS executable"
cd src
make -j 5 ubuntu_simple
sudo cp ./lmp_ubuntu_simple /usr/bin/lammps

echo "Building LAMMPS shared library"
make -j 5 ubuntu_simple mode=shlib

echo "Installing LAMMPS shared library and python package"
make install-python

echo "Cleaning up"
cd ../..
rm -rf lammps

echo "Checker whether LAMMPS is available in python"
python -c 'import lammps as l;l.lammps(cmdargs=["-l", "none"]).command("print \"Hi from LAMMPS\"")'

echo "LAMMPS installation complete. Bye."