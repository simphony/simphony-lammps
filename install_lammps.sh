#!/bin/bash

# checkout a recent stable version (from 28 June 2014)
cd mylammps/src && git checkout r12164
git clone git://git.lammps.org/lammps-ro.git mylammps

#  (1) build lammps as shared library
# make shared library for python
make makeshlib && make -f Makefile.shlib ubuntu_simple
cd ../python && sudo python install.py /usr/lib/ $VIRTUAL_ENV/lib/python2.7/site-packages/

#  (2) and install LAMMPS python wrapper
# make lammps executable and add to path
cd ../src
make ubuntu_simple
ln -s lmp_ubuntu_simple lammps
export PATH=$PWD:$PATH
cd ../../
