from __future__ import print_function

import subprocess
import os
import tempfile
import shutil

from simlammps import read_data_file


def get_particles(y_range):
    """ get particles for benchmarking

    Parameters
    ----------
    y_range : float
        range of particle domain in y

    Returns
    -------
    particle_list : iterable of ABCParticles

    """
    particles_list = None

    temp_dir = tempfile.mkdtemp()
    script_name = os.path.join(temp_dir, "script")
    data_name = os.path.join(temp_dir, "output")
    try:
        with open(script_name, "w") as script_file:
            script_file.write(lammps_script.format(y_range=y_range,
                                                   data_name=data_name))
        cmd = ("lammps -screen none"
               " -log none -echo none"
               " < {}").format(script_name)
        subprocess.check_call(cmd, shell=True)
        particles_list = read_data_file(data_name)
    finally:
        shutil.rmtree(temp_dir)
    return particles_list


lammps_script = """# create particles"
dimension	2
atom_style	atomic

# create geometry
lattice		hex .7
region		box block 0 {y_range} 0 10 -0.25 0.25
create_box	3 box
create_atoms	1 box

mass		1 1.0
mass		2 1.0
mass		3 1.0

# define groups
region	     1 block INF INF INF 1.25 INF INF
group	     lower region 1
region	     2 block INF INF 8.75 INF INF INF
group	     upper region 2
group	     boundary union lower upper
group	     flow subtract all boundary

set          group lower type 2
set          group upper type 3

# write atoms to a lammps data file
write_data {data_name}"""
