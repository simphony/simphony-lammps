import os

from simphony.core.cuba import CUBA
from simphony.core.data_container import DataContainer
from simphony.cuds.particles import Particles
from simlammps.io.lammps_data_file_parser import LammpsDataFileParser
from simlammps.io.lammps_simple_data_handler import LammpsSimpleDataHandler
from simlammps.config.domain import get_box

from simlammps.abc_data_manager import ABCDataManager


class LammpsFileIoDataManager(ABCDataManager):
    """  Class managing Lammps data information using file-io

    The class performs communicating the data to and from lammps using FILE-IO
    communications (i.e. through input and output files). The class manages
    data existing in Lammps (via lammps data file) and allows this data to be
    queried and to be changed.

    Class maintains a cache of the particle information.  This information
    is read from file whenever the read() method is called and written to
    the file whenever the flush() method is called.

    """
    def __init__(self):
        super(LammpsFileIoDataManager, self).__init__()

        # map from lammps-id to simphony-uid
        self._lammpsid_to_uid = {}

        # cache of particle containers
        self._pc_cache = {}

        # cache of data container extensions
        self._dc_extension_cache = {}

    def get_data(self, uname):
        """Returns data container associated with particle container

        Parameters
        ----------
        uname : string
            non-changing unique name of particles

        """
        return DataContainer(self._pc_cache[uname].data)

    def set_data(self, data, uname):
        """Sets data container associated with particle container

        Parameters
        ----------
        uname : string
            non-changing unique name of particles

        """
        self._pc_cache[uname].data = DataContainer(data)

    def get_data_extension(self, uname):
        """Returns data container extension associated with particle container

        Parameters
        ----------
        uname : string
            non-changing unique name of particles

        """
        return dict(self._dc_extension_cache[uname])

    def set_data_extension(self, data, uname):
        """Sets data container extension associated with particle container

        Parameters
        ----------
        uname : string
            non-changing unique name of particles

        """
        self._dc_extension_cache[uname] = dict(data)

    def _handle_delete_particles(self, uname):
        """Handle when a Particles is deleted

        Parameters
        ----------
        uname : string
            non-changing unique name of particles

        """
        del self._pc_cache[uname]
        del self._dc_extension_cache[uname]

    def _handle_new_particles(self, uname, particles):
        """Add new particle container to this manager.


        Parameters
        ----------
        uname : string
            non-changing unique name of particles
        particles : ABCParticles
            particle container to be added

        """
        # create empty stand-alone particle container
        # to use as a cache of for input/output to LAMMPS
        pc = Particles(name="_")
        pc.data = DataContainer(particles.data)
        for p in particles.iter_particles():
            pc.add_particle(p)
        for p in particles.iter_bonds():
            pc.add_bond(p)

        self._pc_cache[uname] = pc

        if hasattr(particles, 'data_extension'):
            self._dc_extension_cache[uname] = dict(particles.data_extension)
        else:
            # create empty dc extension
            self._dc_extension_cache[uname] = {}

    def get_particle(self, uid, uname):
        """Get particle

        Parameters
        ----------
        uid :
            uid of particle
        uname : string
            name of particle container

        """
        return self._pc_cache[uname].get_particle(uid)

    def update_particle(self, particle, uname):
        """Update particle

        Parameters
        ----------
        uid :
            uid of particle
        uname : string
            name of particle container

        """
        self._pc_cache[uname].update_particle(particle)

    def add_particle(self, particle, uname):
        """Add particle

        Parameters
        ----------
        uid :
            uid of particle
        uname : string
            name of particle container

        """
        return self._pc_cache[uname].add_particle(particle)

    def remove_particle(self, uid, uname):
        """Remove particle

        Parameters
        ----------
        uid :
            uid of particle
        uname : string
            name of particle container

        """
        self._pc_cache[uname].remove_particle(uid)

    def has_particle(self, uid, uname):
        """Has particle

        Parameters
        ----------
        uid :
            uid of particle
        uname : string
            name of particle container

        """
        return self._pc_cache[uname].has_particle(uid)

    def iter_particles(self, uname, uids=None):
        """Iterate over the particles of a certain type

        Parameters
        ----------
        uids : list of particle uids
            sequence of uids of particles that should be iterated over. If
            uids is None then all particles will be iterated over.

        """
        return self._pc_cache[uname].iter_particles(uids)

    def flush(self, input_data_filename):
        """flush to file

        Parameters
        ----------
        input_data_filename :
            name of data-file where inform is written to (i.e lammps's input).
        """
        if self._pc_cache:
            self._write_data_file(input_data_filename)
        else:
            raise RuntimeError(
                "No particles.  Lammps cannot run without a particle")
        # TODO handle properly when there are no particle containers
        # or when some of them do not contain any particles
        # (i.e. someone has deleted all the particles)

    def read(self, output_data_filename):
        """read from file

        Parameters
        ----------
        output_data_filename :
            name of data-file where info read from (i.e lammps's output).
        """
        self._update_from_lammps(output_data_filename)

# Private methods #######################################################
    def _update_from_lammps(self, output_data_filename):
        """read from file and update cache

        """
        assert os.path.isfile(output_data_filename)

        handler = LammpsSimpleDataHandler()
        parser = LammpsDataFileParser(handler)
        parser.parse(output_data_filename)

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
        # TODO updating the material_type from lammps should possibly be
        # removed as lammps is not going to change it
        for _, pc in self._pc_cache.iteritems():
            data = type_data[pc.data[CUBA.MATERIAL_TYPE]]
            for key, value in data.iteritems():
                pc.data[key] = value

        for lammpsid, atom in atoms.iteritems():
            uname, uid = self._lammpsid_to_uid[lammpsid]
            cache_pc = self._pc_cache[uname]
            p = cache_pc.get_particle(uid)
            p.coordinates = tuple(atom[1:4])
            cache_pc.update_particle(p)

            # set the pc's material type
            # (current requirement/assumption is that each
            # pc has particle containers of one type)
            atom_type = atom[0]
            cache_pc.data[CUBA.MATERIAL_TYPE] = atom_type

        for lammpsid, velocity in velocities.iteritems():
            uname, uid = self._lammpsid_to_uid[lammpsid]
            cache_pc = self._pc_cache[uname]
            p = cache_pc.get_particle(uid)
            p.data[CUBA.VELOCITY] = tuple(velocity)
            cache_pc.update_particle(p)

    def _write_data_file(self, filename):
        """ Write data file containing current state of simulation

        """
        lines = ["LAMMPS data file via write_data"
                 ", file written by SimPhony\n\n"]

        # recreate (and store) map from lammps-id to simphony-id
        self._lammpsid_to_uid = {}

        # determine the number of particles
        # and collect the different material types
        # in oder to determine the number of types
        num_particles = 0
        types = set()
        for _, pc in self._pc_cache.iteritems():
            types.add(pc.data[CUBA.MATERIAL_TYPE])
            num_particles += sum(1 for _ in pc.iter_particles())

        box = get_box([de for _, de in self._dc_extension_cache.iteritems()])

        lines.append('{} atoms\n'.format(num_particles))
        lines.append('{} atom types\n\n'.format(len(types)))
        lines.append("\n")
        lines.append(box)
        lines.append("\n")
        lines.append("Masses\n\n")

        material_type_to_mass = self._get_mass()
        for material_type in sorted(material_type_to_mass):
            mass = material_type_to_mass[material_type]
            lines.append('{} {}\n'.format(material_type, mass))
        lines.append("\n")

        with open(filename, 'w') as f:
            f.writelines(lines)

            # keep track of what uid(for a specific pc)
            # corresponds to which lammpsid
            uid_to_lammpsid = {}

            f.write("Atoms\n\n")
            f.writelines(self._generate_atoms_lines(uid_to_lammpsid))

            f.write("\nVelocities\n\n")
            f.writelines(self._generate_velocities_lines(uid_to_lammpsid))
            f.write("\n")

    def _generate_atoms_lines(self, uid_to_lammpsid):
        """ Generate atom lines for a data file.

        Parameters
        ----------
        uid_to_lammpsid : dict
            empty dictionary which will be filled with uname and uid
            of each particle as a key and the corresponding lammpsid
            as the value

        Returns
        -------
        generator
            atom line strings for data file

        """
        lammpsid = 0
        for uname, pc in self._pc_cache.iteritems():
            for p in pc.iter_particles():
                lammpsid += 1
                self._lammpsid_to_uid[lammpsid] = (uname, p.uid)
                uid_to_lammpsid[(uname, p.uid)] = lammpsid
                atom_type = pc.data[CUBA.MATERIAL_TYPE]
                coord = '{0[0]:.16e} {0[1]:.16e} {0[2]:.16e}'.format(
                    p.coordinates)
                yield '{0} {1} {2} 0 0 0\n'.format(
                    lammpsid, atom_type, coord)

    def _generate_velocities_lines(self, uid_to_lammpsid):
        """ Generate velocity lines for a data file.

        Parameters
        ----------
        uid_to_lammpsid : dict
            dictionary filled with uname and uid of each particle as a
            key and the corresponding lammpsid as the value

        Returns
        -------
        generator
            velocities line strings for data file

        """
        for uname, pc in self._pc_cache.iteritems():
            for p in pc.iter_particles():
                lammpsid = uid_to_lammpsid[(uname, p.uid)]
                vel = '{0[0]:.16e} {0[1]:.16e} {0[2]:.16e}'.format(
                    p.data[CUBA.VELOCITY])
                yield '{0} {1}\n'.format(lammpsid, vel)

    def _get_mass(self):
        """ Get a dictionary from 'material type' to 'mass'.

        Check that fits what LAMMPS can handle as well
        as ensure that it works with the limitations
        of how we are currently handling this info.

        Raises
        ------
        RuntimeError :
            if there are particles' which have the same
            material type (CUBA.MATERIAL_TYPE) but different
            masses (CUBA.MASS)

        """
        mass = {}
        for uname, pc in self._pc_cache.iteritems():
            data = pc.data
            material_type = data[CUBA.MATERIAL_TYPE]
            if material_type in mass:
                # check that mass is consistent with an matching type
                if data[CUBA.MASS] != mass[material_type]:
                    raise RuntimeError(
                        "Each material type must have the same mass")
            else:
                mass[material_type] = data[CUBA.MASS]
        return mass
