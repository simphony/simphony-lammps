import os
import uuid
from sets import Set

from simphony.core.cuba import CUBA
from simphony.core.data_container import DataContainer
from simphony.cuds.particles import ParticleContainer
from simlammps.lammps_particle_container import LammpsParticleContainer
from simlammps.io.lammps_data_file_parser import LammpsDataFileParser
from simlammps.io.lammps_simple_data_handler import LammpsSimpleDataHandler
from simlammps.config.domain import get_box


class LammpsFileIoDataManager(object):
    """  Class managing Lammps data information using
        FILE-IO communications (i.e. through input and output
        files).

        Class manages data existing in Lammps (via lammps data file)
        and allows this data to be queried and to be changed.

        Class provides LammpsParticleContainer which implements
        the ABCParticleContainer class so that users can update
        the particles/bonds.

        A cache of the particle information is maintained:  It
        is read from file with the update_from_lammps() method
        and written to file whenever the flush() method is called.

        Parameters
        ----------
        data_filename :
            file name of data file where information is read from
            and written to.

    """
    def __init__(self, data_filename):
        self._data_filename = data_filename
        self._number_types = 0

        # map from name to unique name
        self._unames = {}

        # map from unique name to names
        self._names = {}

        # cache of particle containers where
        # particle containers are stored by a
        # unique name
        self._particle_containers = {}

        # lammps_particle containers where
        # particle containers are stored by a
        # unique name
        self._lammps_particle_containers = {}

        # map from lammps-id to simphony-uid
        self._lammpsid_to_id = {}

        # flags to keep track of current state of this
        # cache  (e.g. invalid is True when we no longer
        # have up-to-date information)
        self._invalid = False

    def get_name(self, uname):
        """
        Get the name of a particle container

        Parameters
        ----------
        uname : str
            unique name of particle container

        Returns
        -------
        str
            name of particle container

        """
        return self._names[uname]

    def rename(self, uname, new_name):
        """
        rename a particle container

        Parameters
        ---------
        uname :
            unique name of particle container to be renamed
        new_name :
            new name of the particle container

        """
        del self._unames[self._names[uname]]
        self._unames[new_name] = uname
        self._names[uname] = new_name

    def __iter__(self):
        """ iter over names of particle containers

        """
        for name in self._unames:
            yield name

    def __contains__(self, name):
        """
        checks if particle container with this name exists

        """
        return name in self._unames

    def __getitem__(self, name):
        """
        returns particle container with this name

        """
        return self._lammps_particle_containers[self._unames[name]]

    def __delitem__(self, name):
        """
        deletes lammps particle container and associated cache

        """
        del self._particle_containers[self._unames[name]]
        del self._lammps_particle_containers[self._unames[name]]
        del self._unames[name]

    def get_data(self, uname):
        """
        returns data container associated with particle container

        """
        return self._particle_containers[uname].data

    def set_data(self, data, uname):
        """
        sets data container associated with particle container

        """
        self._particle_containers[uname].data = data

    def new_particle_container(self, particle_container):
        """
        add new particle container to this manager


        Parameters
        ----------
        particle_container : ABCParticleContainer
            paticle container to be added

        Returns
        -------
        LammpsParticleContainer

        """

        # generate a unique name that will not change over the lifetime
        # of the wrapper.
        uname = uuid.uuid4()

        self._unames[particle_container.name] = uname
        self._names[uname] = particle_container.name

        # create empty stand-alone particle container
        # to use as a cache of for input/output to LAMMPS
        pc = ParticleContainer(name="_")
        pc.data = DataContainer(particle_container.data)
        for p in particle_container.iter_particles():
            pc.add_particle(p)

        self._particle_containers[uname] = pc
        lammps_pc = LammpsParticleContainer(self, uname)
        self._lammps_particle_containers[uname] = lammps_pc
        return lammps_pc

    def get_particle(self, uid, uname):
        self._ensure_up_to_date()
        return self._particle_containers[uname].get_particle(uid)

    def update_particle(self, particle, uname):
        self._ensure_up_to_date()
        return self._particle_containers[uname].update_particle(particle)

    def add_particle(self, particle, uname):
        self._ensure_up_to_date()
        if self._particle_containers[uname].has_particle(particle.uid):
            raise KeyError(
                "particle with same uid ({}) alread exists".format(
                    particle.uid))
        else:
            return self._particle_containers[uname].add_particle(particle)

    def remove_particle(self, uid, uname):
        self._ensure_up_to_date()
        self._particle_containers[uname].remove_particle(uid)

    def iter_particles(self, uname, uids=None):
        """Iterate over the particles of a certain type

        Parameters
        ----------

        uids : list of particle uids
            sequence of uids of particles that should be iterated over. If
            ids is None then all particles will be iterated over.

        """
        self._ensure_up_to_date()
        return self._particle_containers[uname].iter_particles(uids)

    def flush(self):
        if self._particle_containers:
            self._write_data_file(self._data_filename)
        else:
            raise Exception(
                "No particles.  Lammps cannot run without a particle")
        # TODO handle properly when there are no particle containers
        # or when some of them do not contain any particles
        # (i.e. someone has deleted all the particles)

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
            uname, uid = self._lammpsid_to_id[lammpsid]
            p = self._particle_containers[uname].get_particle(uid)
            p.coordinates = tuple(atom[1:4])
            self._particle_containers[uname].update_particle(p)

            # TODO
            atom_type = atom[0]
            self._particle_containers[uname].data[CUBA.MATERIAL_TYPE] = \
                atom_type

        for lammpsid, velocity in velocities.iteritems():
            uname, uid = self._lammpsid_to_id[lammpsid]
            p = self._particle_containers[uname].get_particle(uid)
            p.data[CUBA.VELOCITY] = tuple(velocity)
            self._particle_containers[uname].update_particle(p)

    def _write_data_file(self, filename):
        """ Write data file containing current state of simulation

        """
        header = ("LAMMPS data file via write_data,"
                  "version 28 Jun 2014, timestep = 0\n\n"
                  "# file written by SimPhony\n\n")

        # recreate map from lammps-id to simphony-id
        self._lammpsid_to_id = {}

        # TODO improve
        num_particles = 0
        types = Set()
        for _, pc in self._particle_containers.iteritems():
            types.add(pc.data[CUBA.MATERIAL_TYPE])
            num_particles = num_particles + sum(1 for _ in pc.iter_particles())

        box = get_box(self._particle_containers)

        with open(filename, 'w') as f:
            f.write(header)
            f.write('{} atoms\n'.format(num_particles))
            f.write('{} atom types\n\n'.format(len(types)))
            f.write("\n")
            f.write(box)
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
            for uname, pc in self._particle_containers.iteritems():
                for p in pc.iter_particles():
                    lammpsid = lammpsid + 1
                    self._lammpsid_to_id[lammpsid] = (uname, p.uid)
                    id_to_lammpsid[(uname, p.uid)] = lammpsid
                    atom_type = pc.data[CUBA.MATERIAL_TYPE]
                    coord = '{0[0]:.16e} {0[1]:.16e} {0[2]:.16e}'.format(
                        p.coordinates)
                    f.write('{0} {1} {2} 0 0 0\n'.format(
                        lammpsid, atom_type, coord))
            f.write("\n")

            f.write("Velocities\n\n")
            for uname, pc in self._particle_containers.iteritems():
                for p in pc.iter_particles():
                    lammpsid = id_to_lammpsid[(uname, p.uid)]
                    vel = '{0[0]:.16e} {0[1]:.16e} {0[2]:.16e}'.format(
                        p.data[CUBA.VELOCITY])
                    f.write('{0} {1}\n'.format(lammpsid, vel))
            f.write("\n")

    def _get_mass(self):
        """ Create a dictionary from 'material type' to 'mass'

            Check that fits what LAMMPS can handle as well
            as ensure that it works with the limitations
            of how we are currently handling this info

        """
        mass = {}
        for uname, pc in self._particle_containers.iteritems():
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
