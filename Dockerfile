From simphony/simphony-common

ENV PYTHON_LIB_DIR /usr/local/lib/python2.7/dist-packages/

RUN apt-get update \
    && apt-get install -yq --no-install-recommends make mpic++ \
    && git clone https://github.com/simphony/simphony-lammps.git

RUN cd simphony-lammps \
    && ./install_external.sh

RUN cd simphony-lammps \
    && python setup.py install \
    && cd .. \
    && rm -rf simphony-lammps \
    && apt-get autoremove -yq \
    && apt-get clean -yq \
    && rm -rf /var/lib/apt/lists/*
