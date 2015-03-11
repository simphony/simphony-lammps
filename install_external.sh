#!/bin/bash
set -e
# checkout a recent stable version (from 9 Dec 2014)
git clone git://git.lammps.org/lammps-ro.git mylammps
pushd mylammps && git checkout r12824 && popd

# build lammps executable 
pushd mylammps/src 
make ubuntu_simple
ln -s lmp_ubuntu_simple lammps
popd
