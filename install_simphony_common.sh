#!/bin/bash
# install simphony-common
#  -install requirements for simphony
#  -install simphony-common
set -e
sudo apt-get install libhdf5-serial-dev

# (1) Install cython and numexpr externally because the requirements does
#     work with them
# (2) Pytables breaks with latest Cython
#     see https://github.com/PyTables/PyTables/issues/388
pip install numpy numexpr cython==0.20
pip install -e git://github.com/simphony/simphony-common.git#egg=simphony
