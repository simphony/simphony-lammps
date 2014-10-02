from __future__ import print_function
import os

from simlammps.lammps_wrapper import LammpsWrapper


def _configure_lammps(wrapper):
    # we *workaround* the fact that we cannot
    # configure the wrapper/lammps yet
    # here we use the example script file
    # which has the run command commented out
    infile = os.path.dirname(__file__) + "/in.flow.pois"
    lines = open(infile, 'r').readlines()
    for line in lines:
        print("executing:", line)
        wrapper._lammps.command(line)


wrapper = LammpsWrapper()
_configure_lammps(wrapper)

for _ in xrange(10):
    wrapper.run()
    print("--------------------------------------")
    for name, pc in wrapper.iter_particle_containers():
        print("  ParticleContainer named '{}'".format(name))

        x = []
        y = []
        z = []
        for p in pc.iter_particles():
            x.append(p.coordinates[0])
            y.append(p.coordinates[1])
            z.append(p.coordinates[2])

        print("      number of points: {}".format(len(x)))
        if x:
            print("      x-range: {}, {}".format(min(x), max(x)))
            print("      y-range: {}, {}".format(min(y), max(y)))
            print("      z-range: {}, {}".format(min(z), max(z)))
    print("--------------------------------------")
