import os

from simphony.core.cuba import CUBA
from simphony.core.cuds_item import CUDSItem
from simphony.core.data_container import DataContainer
from simphony.cuds.particles import Particles, Particle

from simlammps.io.lammps_data_file_parser import LammpsDataFileParser
from simlammps.io.lammps_simple_data_handler import LammpsSimpleDataHandler
from simlammps.io.lammps_data_line_interpreter import LammpsDataLineInterpreter
from simlammps.io.lammps_data_file_writer import LammpsDataFileWriter
from simlammps.common.utils import create_material_to_atom_type_map
from simlammps.common.atom_style_description import (ATOM_STYLE_DESCRIPTIONS,
                                                     get_attributes)

from simlammps.config.domain import get_box

from simlammps.abc_data_manager import ABCDataManager


def _filter_unsupported_data(iterable, supported_cuba):
    """Ensure iterators only provide particles with only supported data

    Parameters
    ----------
    iterable : iterator of Particles
        iterable of particles
    supported_cuba: list of CUBA
        what cuba is supported

    """
    for particle in iterable:
        data = particle.data
        supported_data = {cuba: data[cuba] for cuba in
                          data if cuba in supported_cuba}
        supported_particle = Particle(coordinates=particle.coordinates,
                                      uid=particle.uid,
                                      data=supported_data)
        yield supported_particle


class LammpsFileIoDataManager(ABCDataManager):
    """  Class managing Lammps data information using file-io

    The class performs communicating the data to and from lammps using FILE-IO
    communications (i.e. through input and output files). The class manages
    data existing in Lammps (via lammps data file) and allows this data to be
    queried and to be changed.

    Class maintains a cache of the particle information. This information
    is read from file whenever the read() method is called and written to
    the file whenever the flush() method is called.

    Parameters
    ----------
    state_data : StateData
        state data
    atom_style : str
        style of atoms

    """
    def __init__(self, state_data, atom_style):
        super(LammpsFileIoDataManager, self).__init__()

        self._state_data = state_data

        self._atom_style = atom_style

        # map from lammps-id to simphony-uid
        self._lammpsid_to_uid = {}

        # cache of particle containers
        self._pc_cache = {}

        # cache of data container extensions
        self._dc_extension_cache = {}

        self._supported_cuba = get_attributes(self._atom_style)

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
        # create stand-alone particle container to use
        # as a cache of for input/output to LAMMPS
        pc = Particles(name="_")
        pc.data = DataContainer(particles.data)

        for p in particles.iter_particles():
            pc.add_particles([p])

        for b in particles.iter_bonds():
            pc.add_bonds([b])

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

    def update_particles(self, iterable, uname):
        """Update particles

        """
        self._pc_cache[uname].update_particles(
            _filter_unsupported_data(iterable, self._supported_cuba))

    def add_particles(self, iterable, uname):
        """Add particles

        """
        uids = self._pc_cache[uname].add_particles(iterable)

        # filter the cached particles of unsupported CUBA
        self._pc_cache[uname].update_particles(_filter_unsupported_data(
            self._pc_cache[uname].iter_particles(uids), self._supported_cuba))

        return uids

    def remove_particle(self, uid, uname):
        """Remove particle

        Parameters
        ----------
        uid :
            uid of particle
        uname : string
            name of particle container

        """
        self._pc_cache[uname].remove_particles([uid])

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

    def number_of_particles(self, uname):
        """Get number of particles in a container

        Parameters
        ----------
        uname : string
            non-changing unique name of particles

        """
        return self._pc_cache[uname].count_of(CUDSItem.PARTICLE)

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

        atom_type_to_material = {v: k for k, v
                                 in self._material_to_atom.iteritems()}

        def convert_atom_type_to_material(atom_type):
            return atom_type_to_material[atom_type]

        interpreter = LammpsDataLineInterpreter(self._atom_style,
                                                convert_atom_type_to_material)

        atoms = handler.get_atoms()
        velocities = handler.get_velocities()

        assert(len(atoms) == len(velocities))

        for lammps_id, values in atoms.iteritems():
            uname, uid = self._lammpsid_to_uid[lammps_id]
            cache_pc = self._pc_cache[uname]
            p = cache_pc.get_particle(uid)
            p.coordinates, p.data = interpreter.convert_atom_values(values)
            p.data.update(
                interpreter.convert_velocity_values(velocities[lammps_id]))

            cache_pc.update_particles([p])

    def _write_data_file(self, filename):
        """ Write data file containing current state of simulation

        """
        # recreate (and store) map from lammps-id to simphony-id
        self._lammpsid_to_uid = {}

        # determine the number of particles
        num_particles = sum(
            pc.count_of(
                CUDSItem.PARTICLE) for pc in self._pc_cache.itervalues())

        # create the mapping from material to atom-type
        self._material_to_atom = create_material_to_atom_type_map(
            self._state_data)

        box = get_box([de for _, de in self._dc_extension_cache.iteritems()])

        mass = self._get_mass() \
            if ATOM_STYLE_DESCRIPTIONS[self._atom_style].has_mass_per_type \
            else None
        mat_to_atom = self._material_to_atom
        writer = LammpsDataFileWriter(filename,
                                      atom_style=self._atom_style,
                                      number_atoms=num_particles,
                                      material_to_atom_type=mat_to_atom,
                                      simulation_box=box,
                                      material_type_to_mass=mass)
        for uname, pc in self._pc_cache.iteritems():
            for p in pc.iter_particles():
                lammps_id = writer.write_atom(p)
                self._lammpsid_to_uid[lammps_id] = (uname, p.uid)
        writer.close()

    def _get_mass(self):
        """ Get a dictionary from 'material type' to 'mass'.

        Use the materials stored in the state data to get a map
        from each material to its mass

        Raises
        ------
        RuntimeError :
            if there is a material which does not have a mass (CUBA.MASS)

        """
        mass = {}
        for material in self._state_data.iter_materials():
            if CUBA.MASS not in material.data:
                raise RuntimeError(
                    "Material does not have the required mass")
            else:
                mass[material.uid] = material.data[CUBA.MASS]
        return mass
