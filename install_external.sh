#!/bin/bash
set -e

if [ -z "$PYTHON_LIB_DIR" ]; then echo "Set PYTHON_LIB_DIR variable to location of where lammps shared library and lammps.py should be installed (currently using default)"; fi

PYTHON_LIB_DIR=${PYTHON_LIB_DIR:-$VIRTUAL_ENV/lib/python2.7/site-packages/}

echo "Installing python LAMMPS wrapper to '$PYTHON_LIB_DIR'"


echo "Checking out a recent stable version (from 10 Aug 2015)"
git clone --branch r13864 --depth 1 git://github.com/lammps/lammps mylammps

echo "Building LAMMPS executable"
pushd mylammps/src
make -j 2 ubuntu_simple
ln -s lmp_ubuntu_simple lammps
popd


pushd mylammps/src
echo "Making shared library for LAMMPS python wrapper"
make -j 2 ubuntu_simple mode=shlib
popd
echo "Installing LAMMPS python wrapper"
pushd mylammps/python
python install.py $PYTHON_LIB_DIR 
popd
python check_lammps_python.py
