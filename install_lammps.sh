#!/bin/bash

# checkout a recent stable version (from 28 June 2014)
git clone git://git.lammps.org/lammps-ro.git mylammps
pushd mylammps && git checkout r12164 && popd

# (1) build lammps as shared library
#  and install LAMMPS python wrapper
pushd mylammps/src 
make makeshlib 
make -f Makefile.shlib ubuntu_simple
cd ../python && sudo python install.py /usr/lib/ $VIRTUAL_ENV/lib/python2.7/site-packages/
popd

# (2) make lammps executable and add to path
pushd mylammps/src 
make ubuntu_simple
ln -s lmp_ubuntu_simple lammps
export PATH=$PWD:$PATH
popd
