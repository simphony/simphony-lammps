import os
import copy
import uuid

from simphony.core.cuba import CUBA
from simphony.core.data_container import DataContainer
from simphony.cuds.particles import Particle
from simlammps.io.lammps_data_file_parser import LammpsDataFileParser
from simlammps.io.lammps_simple_data_handler import LammpsSimpleDataHandler


class LammpsFileIoDataManager(object):
    """  Class managing Lammps data information using
        FILE-IO communications (i.e. through input and output
        files).

        Class manages data existing in Lammps in lammps
        and allows user to query and change them.

        Parameters
        ----------
        data_filename :
            file name of data file where information is read from
            and written to.
    """
    def __init__(self, data_filename):
        self._data_filename = data_filename
        self._number_types = 0

        # cache particles and their type
        # and type-specific data (e.g. mass)
        self._particles = {}
        self._particle_type = {}
        self._type_data = {}

        # map from simphony-id to lammps-id
        self._id_to_lammpsid = {}

        # flags to keep track of current state of this
        # cache  (e.g. _invalid is True when we no longer
        # have up-to-date information)
        self._invalid = True

    @property
    def number_types(self):
        return self._number_types

    def get_particle(self, id):
        self._ensure_up_to_date()
        if id in self._particles:
            return self._particles[id]
        else:
            raise KeyError("id ({}) was not found".format(id))

    def update_particle(self, particle):
        self._ensure_up_to_date()
        if particle.id in self._particles:
            self._particles[particle.id] = copy.deepcopy(particle)
        else:
            raise KeyError("id ({}) was not found".format(id))

    def add_particle(self, particle_type, particle):
        self._ensure_up_to_date()
        if particle.id not in self._particles:
            id = particle.id
            if id is None:
                id = uuid.uuid4()
            p = Particle(
                id=id, coordinates=particle.coordinates,
                data=DataContainer(particle.data))
            self._particles[id] = p
            return id
        else:
            raise KeyError(
                "particle with same id ({}) alread exists".format(id))

    def remove_particle(self, particle):
        self._ensure_up_to_date()
        if particle.id in self._particles:
            del self._particles[particle.id]
            del self._particle_type[particle.id]
        else:
            raise KeyError(
                "particle with id ({}) does not exist".format(id))

    def iter_id_particles(self, particle_type, ids=None):
        """Iterate over the particles of a certain type

        Parameters:

        ids : list of particle ids
            sequence of ids of particles that should be iterated over. If
            ids is None then all particles will be iterated over.

        """
        self._ensure_up_to_date()
        if ids:
            raise NotImplemented()
        else:
            for id, p in self._particles.iteritems():
                if self._particle_type[id] == particle_type:
                    yield p

    def flush(self):
        if self._particles:
            self._write_data_file(self._data_filename)
        else:
            raise Exception(
                "No particles.  Lammps cannot run without a particle")
        # TODO handle properly when particles is empty
        # (i.e. someone has deleted all the partlces)

    def mark_as_invalid(self):
        self._invalid = True

# Private methods #######################################################
    def _ensure_up_to_date(self):
        if self._invalid:
            self.update_from_lammps()
            self._invalid = False

    def update_from_lammps(self):
        assert os.path.isfile(self._data_filename)

        handler = LammpsSimpleDataHandler()
        parser = LammpsDataFileParser(handler)
        parser.parse(self._data_filename)

        self._number_types = handler.get_number_atom_types()
        atoms = handler.get_atoms()
        velocities = handler.get_velocities()
        masses = handler.get_masses()

        assert(len(atoms) == len(velocities))

        # TODO what if there are no particles

        self._particles = {}
        self._particle_type = {}
        self._type_data = {}

        for atom_type in range(1, self._number_types+1):
            self._type_data[atom_type] = DataContainer()

        for atom_type, mass in masses.iteritems():
            self._type_data[atom_type][CUBA.MASS] = mass

        for id, atom in atoms.iteritems():
            atom_type = atom[0]
            coord = tuple(atom[1:4])
            p = Particle(id=id, coordinates=coord)
            self._particles[id] = p
            self._particle_type[id] = atom_type

        for id, vel in velocities.iteritems():
            velocity = tuple(vel)
            self._particles[id].data[CUBA.VELOCITY] = velocity

    def _write_data_file(self, filename):
        """ Write data file containing current state of simulation

        """
        header = ("LAMMPS data file via write_data,"
                  "version 28 Jun 2014, timestep = 0\n\n"
                  "# file written by SimPhony\n\n")

        dumy_box = ("0.0000000000000000e+00 2.5687134504920127e+01 xlo xhi\n"
                    "-2.2245711031688635e-03 2.2247935602791809e+01 ylo yhi\n"
                    "-3.2108918131150160e-01 3.2108918131150160e-01 zlo zhi\n")
        dummy_coef = ("1 1 1\n"
                      "2 1 1\n"
                      "3 1 1\n")

        # TODO handle empty particles
        assert self._number_types != 0

        with open(filename, 'w') as f:
            f.write(header)
            f.write('{} atoms\n'.format(len(self._particles)))
            f.write('{} atom types\n\n'.format(self._number_types))
            f.write("\n")
            f.write(dumy_box)
            f.write("\n")
            f.write("Masses\n\n")
            for atom_type, data in self._type_data.iteritems():
                f.write('{} {}\n'.format(atom_type, data[CUBA.MASS]))
            f.write("\n")
            f.write("Pair Coeffs # lj/cut\n\n")
            f.write(dummy_coef)
            f.write("\n")
            f.write("Atoms\n\n")
            for id, p in self._particles.iteritems():
                ptype = self._particle_type[id]
                coord = '{0[0]:.16e} {0[1]:.16e} {0[2]:.16e}'.format(
                    p.coordinates)
                f.write('{0} {1} {2} 0 0 0\n'.format(id, ptype, coord))
            f.write("\n")
            f.write("Velocities\n\n")
            for id, p in self._particles.iteritems():
                vel = '{0[0]:.16e} {0[1]:.16e} {0[2]:.16e}'.format(
                    p.data[CUBA.VELOCITY])
                f.write('{0} {1}\n'.format(id, vel))
            f.write("\n")
