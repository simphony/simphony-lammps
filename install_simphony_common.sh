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
# installing tables as although we aren't using H5I0, we
# are using simphony-common.simphony.testing.abc_check_particle_containers
# which uses testing.utils which does utilize H5IO to get types of CUBA
pip install tables
pip install -e git://github.com/simphony/simphony-common.git#egg=simphony
