#!/bin/bash

git clone git://github.com/simphony/simphony-common.git

# add additional cuba keywords to the official list
cat additional_cuba.yml >> simphony-common/simphony/core/cuba.yml

pushd simphony-common
python simphony/scripts/cuba_generate.py python simphony/core/cuba.yml simphony/core/cuba.py
python setup.py instal
popd
rm -rf simphony-common
