#!/bin/bash
set -e
# checkout a recent stable version (from 10 Aug 2015)
git clone --branch r13864 --depth 1 git://github.com/lammps/lammps mylammps

# build lammps executable
pushd mylammps/src
make -j 2 ubuntu_simple
ln -s lmp_ubuntu_simple lammps
popd


pushd mylammps/src
# make shared library for python
make -j 2 ubuntu_simple mode=shlib
popd
# install LAMMPS python wrapper
pushd mylammps/python
sudo python install.py /usr/lib/ $VIRTUAL_ENV/lib/python2.7/site-packages/
popd
python check_lammps_python.py

# build liggghts
git clone --branch 3.3.0 --depth 1 git://github.com/CFDEMproject/LIGGGHTS-PUBLIC.git myliggghts
pushd myliggghts/src
make -j 2 fedora
ln -s lmp_fedora liggghts
popd
