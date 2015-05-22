#!/bin/bash
set -e
# checkout a recent stable version (from 9 Dec 2014)
git clone --branch r12824 --depth 1 git://git.lammps.org/lammps-ro.git mylammps

# build lammps executable
pushd mylammps/src
make -j 2 ubuntu_simple
ln -s lmp_ubuntu_simple lammps
popd


pushd mylammps/src
# make shared library for python
make -j 2 makeshlib && make -j 2 -f Makefile.shlib ubuntu_simple
popd
# install LAMMPS python wrapper
pushd mylammps/python
sudo python install.py /usr/lib/ $VIRTUAL_ENV/lib/python2.7/site-packages/
popd
python check_lammps_python.py
