import os
import uuid
import shutil
from sets import Set

from simphony.core.cuba import CUBA
from simphony.core.data_container import DataContainer
from simphony.cuds.particles import Particle, ParticleContainer
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

        # cache of particle containers
        # TODO optimize so smaller number of particles
        # are stored in memory and if there are too many particles
        # then stored in a file
        self._particle_containers = {}

        # map from lammps-id to simphony-id (id/name)
        self._lammpsid_to_id = {}

        # flags to keep track of current state of this
        # cache  (e.g. _invalid is True when we no longer
        # have up-to-date information)
        self._invalid = False

    def get_data(self, name):
        return self._particle_containers[name].data

    def set_data(self, data, name):
        self._particle_containers[name].data = data

    def new_particle_container(self, name):
        # create empty stand-alone particle container
        # to use as a cache of for input/output to LAMMPS
        self._particle_containers[name] = ParticleContainer()

    def get_particle(self, id, name):
        self._ensure_up_to_date()
        return self._particle_containers[name].get_particle(id)

    def update_particle(self, particle, name):
        self._ensure_up_to_date()
        return self._particle_containers[name].update_particle(particle)

    def add_particle(self, particle, name):
        self._ensure_up_to_date()
        # TODO remove once PC is using uuid
        # and returns that UUID
        if self._particle_containers[name].has_particle(particle.id):
            raise KeyError(
                "particle with same id ({}) alread exists".format(id))
        else:
            id = particle.id
            if id is None:
                id = uuid.uuid4()
            p = Particle(
                id=id, coordinates=particle.coordinates,
                data=DataContainer(particle.data))
            self._particle_containers[name].add_particle(p)
            return id

    def remove_particle(self, id, name):
        self._ensure_up_to_date()
        self._particle_containers[name].remove_particle(id)

    def iter_particles(self, name, ids=None):
        """Iterate over the particles of a certain type

        Parameters:

        ids : list of particle ids
            sequence of ids of particles that should be iterated over. If
            ids is None then all particles will be iterated over.

        """
        self._ensure_up_to_date()
        return self._particle_containers[name].iter_particles(ids)

    def flush(self):
        if self._particle_containers:
            self._write_data_file(self._data_filename)
        else:
            raise Exception(
                "No particles.  Lammps cannot run without a particle")
        # TODO handle properly when there are no particle containers
        # or when some of them do not contain any particles
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

        atoms = handler.get_atoms()
        velocities = handler.get_velocities()
        masses = handler.get_masses()

        assert(len(atoms) == len(velocities))

        type_data = {}

        for atom_type, mass in masses.iteritems():
            type_data[atom_type] = DataContainer()
            type_data[atom_type][CUBA.MASS] = mass

        # update each particle container with these
        # material-specific attributes
        for _, pc in self._particle_containers.iteritems():
            data = type_data[pc.data[CUBA.MATERIAL_TYPE]]
            for key, value in data.iteritems():
                pc.data[key] = value

        for lammpsid, atom in atoms.iteritems():
            name, id = self._lammpsid_to_id[lammpsid]
            p = self._particle_containers[name].get_particle(id)
            p.coordinates = tuple(atom[1:4])
            self._particle_containers[name].update_particle(p)

            # TODO
            atom_type = atom[0]
            self._particle_containers[name].data[CUBA.MATERIAL_TYPE] = \
                atom_type

        for lammpsid, velocity in velocities.iteritems():
            name, id = self._lammpsid_to_id[lammpsid]
            p = self._particle_containers[name].get_particle(id)
            p.data[CUBA.VELOCITY] = tuple(velocity)
            self._particle_containers[name].update_particle(p)

    def _write_data_file(self, filename):
        """ Write data file containing current state of simulation

        """
        header = ("LAMMPS data file via write_data,"
                  "version 28 Jun 2014, timestep = 0\n\n"
                  "# file written by SimPhony\n\n")

        dumy_box = ("0.0000000000000000e+00 2.5687134504920127e+01 xlo xhi\n"
                    "-2.2245711031688635e-03 2.2247935602791809e+01 ylo yhi\n"
                    "-3.2108918131150160e-01 3.2108918131150160e-01 zlo zhi\n")

        # recreate map from lammps-id to simphony-id
        self._lammpsid_to_id = {}

        # TODO improve
        num_particles = 0
        types = Set()
        for _, pc in self._particle_containers.iteritems():
            types.add(pc.data[CUBA.MATERIAL_TYPE])
            num_particles = num_particles + sum(1 for _ in pc.iter_particles())

        with open(filename, 'w') as f:
            f.write(header)
            f.write('{} atoms\n'.format(num_particles))
            f.write('{} atom types\n\n'.format(len(types)))
            f.write("\n")
            f.write(dumy_box)
            f.write("\n")
            f.write("Masses\n\n")
            material_type_to_mass = self._get_mass()
            for material_type in sorted(material_type_to_mass):
                mass = material_type_to_mass[material_type]
                f.write('{} {}\n'.format(material_type, mass))
            f.write("\n")

            f.write("Atoms\n\n")
            lammpsid = 0
            id_to_lammpsid = {}
            for name, pc in self._particle_containers.iteritems():
                for p in pc.iter_particles():
                    lammpsid = lammpsid + 1
                    self._lammpsid_to_id[lammpsid] = (name, p.id)
                    id_to_lammpsid[(name, p.id)] = lammpsid
                    atom_type = pc.data[CUBA.MATERIAL_TYPE]
                    coord = '{0[0]:.16e} {0[1]:.16e} {0[2]:.16e}'.format(
                        p.coordinates)
                    f.write('{0} {1} {2} 0 0 0\n'.format(
                        lammpsid, atom_type, coord))
            f.write("\n")

            f.write("Velocities\n\n")
            for name, pc in self._particle_containers.iteritems():
                for p in pc.iter_particles():
                    lammpsid = id_to_lammpsid[(name, p.id)]
                    vel = '{0[0]:.16e} {0[1]:.16e} {0[2]:.16e}'.format(
                        p.data[CUBA.VELOCITY])
                    f.write('{0} {1}\n'.format(lammpsid, vel))
            f.write("\n")
        shutil.copyfile("data.lammps", "data_input_from_sim.lammps")

    def _get_mass(self):
        """ Create a dictionary from 'material type' to 'mass'

            Check that fits what LAMMPS can handle as well
            as ensure that it works with the limitations
            of how we are currently handling this info
        """
        mass = {}
        for name, pc in self._particle_containers.iteritems():
            data = pc.data
            material_type = data[CUBA.MATERIAL_TYPE]
            if material_type in mass:
                # check that mass is consistent with an matching type
                if data[CUBA.MASS] != mass[material_type]:
                    raise Exception(
                        "Each material type must have the same mass")
            else:
                mass[material_type] = data[CUBA.MASS]
        return mass
