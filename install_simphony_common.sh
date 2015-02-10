#!/bin/bash
# install simphony-common
#  -install requirements for simphony
#  -edit cuba list
#  -install simphony-common


sudo apt-get install libhdf5-serial-dev

git clone git://github.com/simphony/simphony-common.git

# add additional cuba keywords to the official list
cat additional_cuba.yml >> simphony-common/simphony/core/cuba.yml

pushd simphony-common
pip install numexpr cython==0.20
pip install -r requirements.txt
python simphony/scripts/cuba_generate.py python simphony/core/cuba.yml simphony/core/cuba.py
python setup.py install
popd
rm -rf simphony-common
