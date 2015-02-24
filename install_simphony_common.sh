#!/bin/bash
# install simphony-common
#  -install requirements for simphony
#  -edit cuba list
#  -install simphony-common
set -e
sudo apt-get install libhdf5-serial-dev

git clone git://github.com/simphony/simphony-common.git

# add additional cuba keywords to the official list
cat additional_cuba.yml >> simphony-common/simphony/core/cuba.yml

pushd simphony-common
pip install numpy numexpr cython==0.20
pip install -r dev_requirements.txt

# generate the code with the altered cuby.yml
python simphony/scripts/cuba_generate.py python simphony/core/cuba.yml simphony/core/cuba.py
python simphony/scripts/cuba_generate.py table simphony/core/cuba.yml simphony/io/data_container_description.py

python setup.py install
popd
rm -rf simphony-common
