#!/bin/bash
# install simphony-common
#  -install requirements for simphony
#  -install simphony-common
set -e
sudo apt-get install libhdf5-serial-dev

pip install numpy numexpr cython==0.20
pip install -e git://github.com/simphony/simphony-common.git#egg=simphony
