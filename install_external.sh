#!/bin/bash
set -e
# checkout a recent stable version (from 9 Dec 2014)
git clone git://git.lammps.org/lammps-ro.git mylammps
pushd mylammps && git checkout r12824 && popd

# build lammps executable 
pushd mylammps/src 
make -j ubuntu_simple
ln -s lmp_ubuntu_simple lammps
popd


pushd mylammps/src
# make shared library for python
make -j makeshlib && make -j -f Makefile.shlib ubuntu_simple
popd
# install LAMMPS python wrapper
pushd mylammps/python 
sudo python install.py /usr/lib/ $VIRTUAL_ENV/lib/python2.7/site-packages/
popd
python check_lammps_python.py
